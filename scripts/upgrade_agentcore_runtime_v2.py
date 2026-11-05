#!/usr/bin/env python3
"""Plan or apply an in-place Amazon Bedrock AgentCore Runtime V2 upgrade.

The default mode is read-only: it retrieves the existing runtime, writes a local
snapshot, and prints the V2 update request without changing AWS resources.

Use --apply only after reviewing the snapshot and dry-run request:

    python scripts/upgrade_agentcore_runtime_v2.py \
      --runtime-id YOUR_RUNTIME_ID \
      --region YOUR_REGION \
      --snapshot-file runtime-before.json

    python scripts/upgrade_agentcore_runtime_v2.py \
      --runtime-id YOUR_RUNTIME_ID \
      --region YOUR_REGION \
      --snapshot-file runtime-before.json \
      --apply

The caller must have AgentCore control-plane permissions. No account ID, runtime
ARN, or credential value is embedded in this script.
"""

from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any

import boto3


UPDATE_FIELDS = (
    "agentRuntimeArtifact",
    "roleArn",
    "description",
    "environmentVariables",
    "networkConfiguration",
    "protocolConfiguration",
    "lifecycleConfiguration",
    "metadataConfiguration",
    "authorizerConfiguration",
    "filesystemConfigurations",
    "requestHeaderConfiguration",
    "capacityProviderConfiguration",
)


def build_v2_update_request(runtime: dict[str, Any]) -> dict[str, Any]:
    """Preserve mutable runtime settings while explicitly selecting platform V2."""
    request = {
        "agentRuntimeId": runtime["agentRuntimeId"],
        "agentRuntimeArtifact": runtime["agentRuntimeArtifact"],
        "roleArn": runtime["roleArn"],
        "platformVersion": "V2",
        "clientToken": str(uuid.uuid4()),
    }
    for field in UPDATE_FIELDS:
        if field in runtime and runtime[field] is not None:
            request[field] = runtime[field]
    return request


def wait_for_ready(client: Any, runtime_id: str, timeout_seconds: int) -> dict[str, Any]:
    """Poll until the runtime reaches READY or a terminal non-ready state."""
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        runtime = client.get_agent_runtime(agentRuntimeId=runtime_id)
        status = runtime["status"]
        print(f"[runtime] {runtime_id}: {status}")
        if status == "READY":
            return runtime
        if status in {"FAILED", "DELETE_FAILED"}:
            raise RuntimeError(f"Runtime entered terminal status: {status}")
        time.sleep(10)
    raise TimeoutError(f"Runtime did not reach READY within {timeout_seconds} seconds.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan or apply an AgentCore Runtime V2 upgrade")
    parser.add_argument("--runtime-id", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--snapshot-file", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Apply the V2 update after reviewing the dry run.")
    parser.add_argument("--wait-timeout", type=int, default=600)
    args = parser.parse_args()

    client = boto3.client("bedrock-agentcore-control", region_name=args.region)
    current = client.get_agent_runtime(agentRuntimeId=args.runtime_id)
    args.snapshot_file.write_text(json.dumps(current, indent=2, default=str), encoding="utf-8")
    request = build_v2_update_request(current)

    print(f"[snapshot] wrote {args.snapshot_file}")
    print("[plan] UpdateAgentRuntime request:")
    print(json.dumps(request, indent=2, default=str))

    if not args.apply:
        print("[plan] Dry run only. Re-run with --apply to update the runtime to V2.")
        return

    client.update_agent_runtime(**request)
    updated = wait_for_ready(client, args.runtime_id, args.wait_timeout)
    print("[complete] Runtime is READY")
    print(json.dumps({"runtimeId": updated["agentRuntimeId"], "status": updated["status"]}, indent=2))


if __name__ == "__main__":
    main()
