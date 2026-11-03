"""Agent 2: the Strands A2A specialist used in the OPN408 Code Talk.

Two intentional modes exist:

* rehearsal (default): deterministic A2A lifecycle. It proves AgentCard discovery,
  task state updates, input-required, task resumption, and streamed artifacts.
* bedrock: real Strands + global Claude Sonnet 4.6. It is optional local practice
  and can call the static re:Invent session-search tool.

The local server binds only to 127.0.0.1. It is never the shared/public demo
endpoint; AgentCore Runtime provides the managed authenticated version.
"""

from __future__ import annotations

import argparse
from typing import Literal

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TaskState, TextPart
from a2a.utils import get_message_text, new_agent_text_message, new_task
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.multiagent.a2a.executor import StrandsA2AExecutor

try:
    from .session_recommender_tool import recommend_reinvent_sessions
except ImportError:  # Supports direct `python talk/strands_analyst.py` execution.
    from session_recommender_tool import recommend_reinvent_sessions


# This is intentionally explicit in code: the local Bedrock option uses the
# same globally routed model family described in the Code Talk, not a secret.
BEDROCK_MODEL_ID = "global.anthropic.claude-sonnet-4-6"
ModelMode = Literal["rehearsal", "bedrock"]


def build_bedrock_strands_agent() -> Agent:
    """Create the optional real-model version of Agent 2.

    This function is not used by the default rehearsal. Showing it helps explain
    that the A2A server can wrap an ordinary Strands agent without exposing the
    agent's prompt, model, memory, or tools to LangGraph.
    """
    return Agent(
        name="OPN408 Local Strands Specialist",
        description="Architecture specialist for the OPN408 A2A Code Talk.",
        model=BedrockModel(model_id=BEDROCK_MODEL_ID, max_tokens=2048),
        system_prompt=(
            "You are an architecture specialist. Give concise, practical guidance for "
            "agentic architectures. If the user asks for re:Invent session suggestions, "
            "call recommend_reinvent_sessions first, then clearly say the static catalog "
            "is an unofficial snapshot and scheduling details need official verification."
        ),
        tools=[recommend_reinvent_sessions],
    )


class DeterministicA2AExecutor(AgentExecutor):
    """Teaching-first A2A behavior with no model or AWS dependency.

    The core lesson is deliberately visible: a remote specialist can request a
    missing engineering constraint through a standard task state instead of
    guessing or inventing a framework-private callback.
    """

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # A new A2A request has no task yet. A continuation receives the existing task.
        task = context.current_task or new_task(context.message)
        if context.current_task is None:
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        query = get_message_text(context.message) or ""

        # STATE 1: make work visible immediately; never leave the audience waiting.
        await updater.update_status(
            TaskState.working,
            message=new_agent_text_message("Strands specialist accepted the A2A task."),
        )

        # STATE 2: the A2A lesson. The agent requires data rather than guessing.
        if "Document profile:" not in query:
            await updater.update_status(
                TaskState.input_required,
                message=new_agent_text_message(
                    "Document profile required: formats, corpus size, update cadence, and metadata quality."
                ),
                final=True,
            )
            return

        # ARTIFACTS: named outputs are more useful than one opaque final answer.
        await updater.add_artifact(
            name="architecture-rationale",
            parts=[
                TextPart(
                    text=(
                        "A compact session-guide service needs a curated catalog, metadata "
                        "filters, and an A2A boundary between the coordinator and specialist."
                    )
                )
            ],
        )
        await updater.add_artifact(
            name="cdk-guidance",
            parts=[
                TextPart(
                    text="Create only the private catalog storage and least-privilege access needed for the demo."
                )
            ],
        )
        await updater.add_artifact(
            name="decision-summary",
            parts=[
                TextPart(
                    text=(
                        "LangGraph and Strands collaborated through AgentCard discovery, "
                        "task state, and artifacts—not shared framework internals."
                    )
                )
            ],
        )

        # STATE 3: the coordinator can now treat the task as complete.
        await updater.update_status(TaskState.completed, final=True)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Surface cancellation as an A2A lifecycle event."""
        if context.current_task is None:
            return
        updater = TaskUpdater(event_queue, context.current_task.id, context.current_task.context_id)
        await updater.update_status(TaskState.canceled, final=True)


def build_app(port: int = 9000, model_mode: ModelMode = "rehearsal"):
    """Build the local A2A server and publish its AgentCard.

    `model_mode` is the intentional fork between deterministic protocol teaching
    and optional local Sonnet 4.6 practice.
    """
    if model_mode == "bedrock":
        # Real model mode: Strands turns model output and tool calls into A2A events.
        executor: AgentExecutor = StrandsA2AExecutor(
            build_bedrock_strands_agent(),
            enable_a2a_compliant_streaming=True,
        )
        skills = [
            AgentSkill(
                id="recommend-reinvent-sessions",
                name="Recommend re:Invent sessions",
                description="Searches the static, curated re:Invent snapshot for relevant sessions.",
                tags=["reinvent", "agentcore", "a2a", "strands"],
            )
        ]
    else:
        # Default mode: no model call, no credential requirement, repeatable output.
        executor = DeterministicA2AExecutor()
        skills = [
            AgentSkill(
                id="design-session-guide-rag",
                name="Design a session-guide architecture",
                description="Requests the document profile and streams architecture decision artifacts.",
                tags=["a2a", "architecture", "teaching-demo"],
            )
        ]

    # The AgentCard is what LangGraph discovers. It exposes capability—not implementation.
    card = AgentCard(
        name="Strands Session Guide Analyst",
        description="A Strands specialist for the OPN408 cross-framework A2A demonstration.",
        url=f"http://127.0.0.1:{port}",
        version="0.1.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=True),
        skills=skills,
    )
    handler = DefaultRequestHandler(agent_executor=executor, task_store=InMemoryTaskStore())
    return A2AStarletteApplication(agent_card=card, http_handler=handler).build()


def main() -> None:
    parser = argparse.ArgumentParser(description="Loopback-only Strands A2A specialist")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument(
        "--model",
        choices=("rehearsal", "bedrock"),
        default="rehearsal",
        help="Use deterministic A2A teaching flow or real local Bedrock Sonnet 4.6.",
    )
    args = parser.parse_args()

    # SECURITY: keep the host loopback-only. AgentCore is the managed shared endpoint.
    uvicorn.run(build_app(args.port, args.model), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
