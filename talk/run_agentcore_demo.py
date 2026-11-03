"""Invoke the deployed OPN408 LangGraph A2A runtime using AWS SigV4.

Run from the repository root with AWS credentials for the demo account:

    uv run python talk/run_agentcore_demo.py

The script discovers a caller-specified READY runtime by name prefix, sends an
A2A JSON-RPC task through AgentCore Runtime, and prints the returned artifacts.
It contains no credentials, account IDs, or hard-coded runtime ARN.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any
from uuid import uuid4

import boto3


REGION = os.environ.get("AWS_REGION", "us-east-1")
# The caller supplies the runtime prefix at invocation time; no account-specific
# runtime name is baked into the public script.
DEFAULT_PROMPT = (
    "Design a minimal re:Invent session-guide retrieval service for 120 curated "
    "session abstracts and metadata records. Explain the architecture and trade-offs."
)


def resolve_runtime_arn(runtime_name_prefix: str) -> str:
    """Find one READY runtime by caller-supplied name prefix in the configured Region."""
    control = boto3.client("bedrock-agentcore-control", region_name=REGION)
    response = control.list_agent_runtimes(maxResults=100)
    matches = [
        runtime
        for runtime in response.get("agentRuntimes", [])
        if runtime["agentRuntimeName"].startswith(runtime_name_prefix)
        and runtime.get("status") == "READY"
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one READY runtime beginning {runtime_name_prefix!r}; found {len(matches)}."
        )
    return matches[0]["agentRuntimeArn"]


def a2a_request(text: str) -> bytes:
    """Create the JSON-RPC payload AgentCore transparently proxies to A2A."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "messageId": str(uuid4()),
            }
        },
    }
    return json.dumps(payload).encode("utf-8")


def decode_artifacts(response_text: str) -> list[tuple[str, str]]:
    """Return named A2A artifacts without exposing SDK-specific object types."""
    payload: dict[str, Any] = json.loads(response_text)
    result = payload.get("result", {})
    artifacts = result.get("artifacts", [])
    decoded: list[tuple[str, str]] = []
    for artifact in artifacts:
        text = "".join(part.get("text", "") for part in artifact.get("parts", []))
        decoded.append((artifact.get("name", "unnamed-artifact"), text))
    return decoded


def render_artifact(name: str, text: str, limit: int = 1800) -> str:
    """Flatten a nested remote A2A response for readable on-stage output."""
    if name == "strands-a2a-result":
        nested = decode_artifacts(text)
        text = "\n\n".join(f"[{nested_name}]\n{nested_text}" for nested_name, nested_text in nested)
    if len(text) > limit:
        return f"{text[:limit].rstrip()}\n\n… output truncated for presentation; full artifact is available in the raw response."
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Invoke a deployed AgentCore A2A runtime")
    parser.add_argument(
        "--runtime-prefix",
        required=True,
        help="Unique prefix for one READY AgentCore runtime in the configured AWS Region.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt sent as an A2A task to the deployed LangGraph runtime.",
    )
    args = parser.parse_args()
    runtime_arn = resolve_runtime_arn(args.runtime_prefix)
    runtime = boto3.client("bedrock-agentcore", region_name=REGION)
    response = runtime.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=str(uuid4()),
        payload=a2a_request(args.prompt),
        qualifier="DEFAULT",
    )
    raw = b"".join(response.get("response", [])).decode("utf-8")
    artifacts = decode_artifacts(raw)

    print(f"Invoked: {runtime_arn}")
    for name, text in artifacts:
        print(f"\n=== {name} ===")
        print(render_artifact(name, text))


if __name__ == "__main__":
    main()
