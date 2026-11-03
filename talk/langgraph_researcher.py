"""Agent 1: the LangGraph A2A coordinator used in the OPN408 Code Talk.

Run this in terminal two after `strands_analyst.py` starts in terminal one.
The workflow proves four A2A ideas in a readable order:

1. discover the remote AgentCard;
2. submit a task;
3. observe `input-required` rather than guessing;
4. resume the same task/context and receive artifacts.

This local coordinator intentionally does not use an LLM. That keeps the A2A
state machine visible and deterministic. The managed AgentCore coordinator is
the separate Sonnet-backed proof.
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Any, TypedDict
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import AgentCard, Message, MessageSendParams, Role, SendStreamingMessageRequest, TaskState, TextPart
from langgraph.graph import END, START, StateGraph


DEFAULT_PROMPT = "Design a minimal re:Invent session-guide retrieval architecture."
DEFAULT_DOCUMENT_PROFILE = (
    "Document profile: markdown session abstracts and JSON metadata; 120 curated records; "
    "updated before rehearsals; complete title, abstract, level, track, and speaker metadata."
)

# Backward-compatible names used by the focused talk-path tests.
QUESTION = DEFAULT_PROMPT
PROFILE = DEFAULT_DOCUMENT_PROFILE


class ResearchState(TypedDict, total=False):
    """Only protocol-relevant state crosses LangGraph nodes in the local demo."""

    endpoint: str
    prompt: str
    profile: str
    card: AgentCard
    task_id: str
    context_id: str
    first_events: list[dict[str, Any]]
    final_events: list[dict[str, Any]]


def streaming_request(
    text: str,
    task_id: str | None = None,
    context_id: str | None = None,
) -> SendStreamingMessageRequest:
    """Create one A2A message/send request.

    Passing task/context IDs is what turns the second request into a continuation
    rather than a new independent task.
    """
    message = Message(
        messageId=str(uuid4()),
        role=Role.user,
        parts=[TextPart(text=text)],
        taskId=task_id,
        contextId=context_id,
    )
    return SendStreamingMessageRequest(id=str(uuid4()), params=MessageSendParams(message=message))


async def stream_request(
    card: AgentCard,
    request: SendStreamingMessageRequest,
) -> tuple[list[dict[str, Any]], str, str]:
    """Call the remote A2A server and retain its real task/event stream."""
    async with httpx.AsyncClient(timeout=15.0) as http_client:
        client = ClientFactory(ClientConfig(streaming=True, httpx_client=http_client)).create(card)
        events: list[dict[str, Any]] = []
        task_id = ""
        context_id = ""

        async for result in client.send_message(request.params.message):
            # A streaming A2A result pairs the task with one incremental update.
            if isinstance(result, tuple):
                task, event = result
                task_id = task_id or task.id
                context_id = context_id or task.context_id
                if not events:
                    events.append(task.model_dump(mode="json"))
                if event is not None:
                    events.append(event.model_dump(mode="json"))
            else:
                events.append(result.model_dump(mode="json"))

        return events, task_id, context_id


class LangGraphA2AResearcher:
    """A tiny, explicit LangGraph workflow around a remote A2A specialist."""

    def __init__(self) -> None:
        builder = StateGraph(ResearchState)

        # Turn signals for the audience: discovery → submit → resume → done.
        builder.add_node("discover", self.discover)
        builder.add_node("submit_task", self.submit_task)
        builder.add_node("resume_task", self.resume_task)
        builder.add_edge(START, "discover")
        builder.add_edge("discover", "submit_task")
        builder.add_edge("submit_task", "resume_task")
        builder.add_edge("resume_task", END)
        self.graph = builder.compile()

    async def discover(self, state: ResearchState) -> ResearchState:
        """Fetch the remote public AgentCard before sending a task."""
        print(f"[discovery] fetching AgentCard from {state['endpoint']}")
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            card = await A2ACardResolver(http_client, state["endpoint"]).get_agent_card()

        if not card.capabilities.streaming:
            raise RuntimeError("The remote AgentCard does not advertise streaming.")
        print(f"[discovery] found {card.name}; streaming={card.capabilities.streaming}")
        return {"card": card}

    async def submit_task(self, state: ResearchState) -> ResearchState:
        """Send the caller prompt and require the specialist to request more context."""
        print("[task] submitting A2A task")
        events, task_id, context_id = await stream_request(
            state["card"],
            streaming_request(state["prompt"]),
        )
        if not any(
            event.get("status", {}).get("state") == TaskState.input_required.value
            for event in events
        ):
            raise RuntimeError("The Strands specialist did not request the document profile.")

        print(f"[state] input-required; task={task_id}; context={context_id}")
        return {"first_events": events, "task_id": task_id, "context_id": context_id}

    async def resume_task(self, state: ResearchState) -> ResearchState:
        """Continue the exact remote task with the requested document profile."""
        print("[resume] sending document profile on the same task and context")
        events, _, _ = await stream_request(
            state["card"],
            streaming_request(state["profile"], state["task_id"], state["context_id"]),
        )
        print("[state] remote task returned final artifacts")
        return {"final_events": events}

    async def run(
        self,
        endpoint: str,
        prompt: str = DEFAULT_PROMPT,
        profile: str = DEFAULT_DOCUMENT_PROFILE,
    ) -> ResearchState:
        return await self.graph.ainvoke({"endpoint": endpoint, "prompt": prompt, "profile": profile})


def print_events(events: list[dict[str, Any]]) -> None:
    """Render the protocol state changes; this avoids silent pauses in the demo."""
    for event in events:
        if event.get("kind") == "task":
            print(f"[task] {event['id']} — {event['status']['state']}")
        elif event.get("kind") == "status-update":
            print(f"[state] {event['status']['state']}")
        elif event.get("kind") == "artifact-update":
            artifact = event["artifact"]
            text = artifact["parts"][0].get("text", "")
            print(f"[artifact] {artifact.get('name')}: {text}")


async def main_async(endpoint: str, prompt: str, profile: str) -> None:
    result = await LangGraphA2AResearcher().run(endpoint, prompt, profile)
    card = result["card"]
    print(f"\nAgentCard: {card.name} ({card.url})")
    print("\nFirst A2A exchange")
    print_events(result["first_events"])
    print("\nResumed A2A exchange")
    print_events(result["final_events"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Local LangGraph A2A coordinator")
    parser.add_argument("--endpoint", default="http://127.0.0.1:9000")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Question delegated to the Strands specialist.")
    parser.add_argument(
        "--document-profile",
        default=DEFAULT_DOCUMENT_PROFILE,
        help="Follow-up sent after the specialist returns input-required.",
    )
    args = parser.parse_args()
    asyncio.run(main_async(args.endpoint, args.prompt, args.document_profile))


if __name__ == "__main__":
    main()
