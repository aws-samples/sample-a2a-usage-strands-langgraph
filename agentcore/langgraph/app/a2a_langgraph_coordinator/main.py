"""Account-free LangGraph A2A coordinator template for AgentCore Runtime."""

from __future__ import annotations

import asyncio
import json
import os
from typing import TypedDict
from uuid import uuid4

import boto3
from a2a.helpers import new_task_from_user_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill, Part
from bedrock_agentcore.runtime import serve_a2a
from langchain_aws import ChatBedrock
from langgraph.graph import END, START, StateGraph


MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REMOTE_SPECIALIST_RUNTIME_ARN = os.environ.get("REMOTE_SPECIALIST_RUNTIME_ARN", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
model = ChatBedrock(model_id=MODEL_ID, max_tokens=512)


class CoordinatorState(TypedDict):
    question: str
    brief: str
    specialist_result: str


def invoke_remote_specialist(question: str) -> str:
    """Delegate through AgentCore Runtime using execution-role SigV4 credentials."""
    if not REMOTE_SPECIALIST_RUNTIME_ARN:
        raise RuntimeError(
            "Set REMOTE_SPECIALIST_RUNTIME_ARN locally before deploying this coordinator."
        )

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": question}],
                "messageId": str(uuid4()),
            }
        },
    }
    client = boto3.client("bedrock-agentcore", region_name=AWS_REGION)
    response = client.invoke_agent_runtime(
        agentRuntimeArn=REMOTE_SPECIALIST_RUNTIME_ARN,
        runtimeSessionId=str(uuid4()),
        payload=json.dumps(payload).encode("utf-8"),
        qualifier="DEFAULT",
    )
    return b"".join(response.get("response", [])).decode("utf-8")


async def write_brief(state: CoordinatorState) -> dict:
    """Use LangGraph's model node to produce a concise specialist handoff."""
    response = await model.ainvoke(
        [
            ("system", "Write a concise architecture question for a remote specialist."),
            ("user", state["question"]),
        ]
    )
    return {"brief": str(response.content)}


async def delegate(state: CoordinatorState) -> dict:
    """Run the remote A2A invocation without blocking the async graph loop."""
    result = await asyncio.to_thread(invoke_remote_specialist, state["brief"])
    return {"specialist_result": result}


builder = StateGraph(CoordinatorState)
builder.add_node("write_brief", write_brief)
builder.add_node("delegate", delegate)
builder.add_edge(START, "write_brief")
builder.add_edge("write_brief", "delegate")
builder.add_edge("delegate", END)
graph = builder.compile()


class LangGraphA2AExecutor(AgentExecutor):
    """Expose the LangGraph coordinator as an authenticated A2A server."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task_from_user_message(context.message)
        if context.current_task is None:
            await event_queue.enqueue_event(task)

        question = context.get_user_input()
        if not isinstance(question, str) or not question.strip():
            raise ValueError("A2A coordinator input must contain a non-empty text prompt.")

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.start_work()
        result = await graph.ainvoke({"question": question})
        await updater.add_artifact([Part(text=result["brief"])], name="coordinator-brief")
        await updater.add_artifact(
            [Part(text=result["specialist_result"])],
            name="remote-specialist-result",
        )
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.current_task is not None:
            await TaskUpdater(event_queue, context.current_task.id, context.current_task.context_id).cancel()


card = AgentCard(
    name="A2A LangGraph Coordinator",
    description="A LangGraph coordinator that delegates to a remote A2A specialist.",
    version="0.1.0",
    capabilities=AgentCapabilities(streaming=True),
    skills=[
        AgentSkill(
            id="coordinate-architecture-question",
            name="Coordinate architecture question",
            description="Writes a specialist brief and delegates through AgentCore Runtime.",
            tags=["a2a", "langgraph", "agentcore"],
        )
    ],
    default_input_modes=["text"],
    default_output_modes=["text"],
    supported_interfaces=[
        AgentInterface(protocol_binding="JSONRPC", protocol_version="1.0", url="http://localhost:9000/")
    ],
)

if __name__ == "__main__":
    # AgentCore provides the AWS_IAM boundary; this is not a public unauthenticated server.
    serve_a2a(LangGraphA2AExecutor(), card)
