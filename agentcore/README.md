# Account-free AgentCore deployment templates

This directory provides **source templates**, not a ready-to-push deployment state. It contains no AWS account IDs, runtime ARNs, credentials, or deployment logs.

## What the templates demonstrate

- A Strands A2A specialist deployed behind an `AWS_IAM` AgentCore Runtime boundary.
- A LangGraph A2A coordinator that invokes a remote specialist through the AgentCore API using its execution-role credentials.
- Account-specific values supplied locally at deployment time.

## Create the two AgentCore projects

Create each project using the current AgentCore CLI. This generates the CDK deployment support for your own environment.

```zsh
# Strands specialist
agentcore create \
  --project-name A2AStrandsDemo \
  --name a2a_strands_specialist \
  --language Python \
  --framework Strands \
  --model-provider Bedrock \
  --memory none \
  --protocol A2A

# LangGraph coordinator
agentcore create \
  --project-name A2ALangGraphDemo \
  --name a2a_langgraph_coordinator \
  --language Python \
  --framework LangChain_LangGraph \
  --model-provider Bedrock \
  --memory none \
  --protocol A2A
```

Copy the matching `app/` template from this repository into the CLI-created project.

## Set local deployment targets

Copy `aws-targets.example.json` to `agentcore/aws-targets.json` in each generated project. Replace the placeholder account and region values. The real target file must remain uncommitted.

## Deploy order

1. Deploy the Strands specialist.
2. Record its runtime ARN locally.
3. Add that ARN to the LangGraph coordinator's local `envVars` configuration as `REMOTE_SPECIALIST_RUNTIME_ARN`.
4. Add least-privilege `bedrock-agentcore:InvokeAgentRuntime` permission for the specialist runtime and its `DEFAULT` endpoint to the coordinator execution role.
5. Deploy the LangGraph coordinator.
6. Invoke the coordinator using SigV4 and confirm the remote A2A task completes.

## Security boundary

The runtime templates set `authorizerType` to `AWS_IAM`. AgentCore A2A runtimes serve inside the managed runtime environment; do not expose the local development server beyond loopback or replace the runtime's authentication boundary with a custom token scheme.
