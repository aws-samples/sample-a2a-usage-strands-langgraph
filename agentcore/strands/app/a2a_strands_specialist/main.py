"""Account-free Strands A2A specialist template for AgentCore Runtime."""

from __future__ import annotations

import os

from bedrock_agentcore.runtime import serve_a2a
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.multiagent.a2a.executor import StrandsA2AExecutor


MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")

# A2A callers see the AgentCard, task states, and artifacts. They do not see
# this prompt, model configuration, or any specialist-specific tools.
agent = Agent(
    name="A2A Strands Specialist",
    description="A specialist agent exposed through the A2A protocol.",
    model=BedrockModel(model_id=MODEL_ID, max_tokens=2048),
    system_prompt=(
        "You are a concise architecture specialist. State assumptions, recommend a "
        "practical design, and explain the most important trade-offs."
    ),
)

if __name__ == "__main__":
    # In AgentCore, this serves the A2A JSON-RPC application inside the managed
    # runtime. Inbound authentication is configured by authorizerType=AWS_IAM.
    serve_a2a(StrandsA2AExecutor(agent, enable_a2a_compliant_streaming=True))
