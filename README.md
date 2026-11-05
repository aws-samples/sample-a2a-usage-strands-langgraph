# Cross-framework agent collaboration with A2A

# Cross-framework agent collaboration with A2A

A reusable reference pattern for connecting a **LangGraph coordinator** to a **Strands specialist** through the [Agent2Agent (A2A) protocol](https://a2a-protocol.org/).

> [!WARNING]
> **Not for production use.** This repository is an educational reference implementation. It intentionally prioritizes clear protocol behavior over production hardening. Do not deploy it unchanged for sensitive data, customer traffic, or critical workloads. Before production use, implement and validate your own durable task storage, authentication and authorization model, input validation, observability, dependency lifecycle, failure handling, and operational controls.

The sample focuses on the collaboration boundary rather than framework internals. The two agents do not share prompts, tools, state, or source code. They collaborate through an AgentCard, task lifecycle events, a structured request for missing input, and named artifacts.

## Architecture

```text
Caller
  → LangGraph coordinator
      → AgentCard discovery
      → A2A task submission
          → Strands specialist
              → input-required
              → streamed artifacts
              → completed
```

## What this sample demonstrates

- **Agent discovery** through a remote AgentCard.
- **A2A task lifecycle**: submitted, working, `input-required`, and completed.
- **Same-task continuation** using the original task and context IDs.
- **Named artifacts** instead of a single opaque response.
- **Framework independence**: LangGraph coordinates; Strands specializes.
- **Two operating modes**: deterministic local rehearsal and optional Bedrock-backed Strands practice.
- **Account-free AgentCore templates** for deploying the same pattern with `AWS_IAM` authentication.

## Quick start

Prerequisites:

- Python 3.13 or later
- [uv](https://docs.astral.sh/uv/)

Install dependencies:

```zsh
uv sync
```

Start the Strands specialist in one terminal:

```zsh
uv run python talk/strands_analyst.py --model rehearsal
```

Run the LangGraph coordinator in another terminal:

```zsh
uv run python talk/langgraph_researcher.py \
  --prompt "Design a document retrieval architecture for a curated knowledge catalog."
```

The terminal shows the protocol flow directly:

```text
[discovery] fetching AgentCard
[task] submitting A2A task
[state] input-required
[resume] sending document profile on the same task and context
[artifact] architecture-rationale
[artifact] cdk-guidance
[artifact] decision-summary
[state] completed
```

## Repository guide

| Path | Purpose |
|---|---|
| `talk/strands_analyst.py` | Strands A2A specialist. The default deterministic mode makes lifecycle behavior easy to inspect. |
| `talk/langgraph_researcher.py` | LangGraph A2A coordinator for discovery, task submission, and continuation. |
| `talk/session_recommender_tool.py` | Optional example of a normal Strands tool over static JSON. |
| `talk/sample-catalog.json` | Synthetic example data for the optional catalog-search tool. |
| `agentcore/` | Account-free templates for deploying a Strands specialist and LangGraph coordinator to AgentCore Runtime. |
| `presentation/` | Optional presentation materials for explaining the pattern to an audience. |

## Optional local Bedrock mode

The local specialist can use Amazon Bedrock instead of deterministic rehearsal output:

```zsh
uv run python talk/strands_analyst.py --model bedrock
```

This mode uses `global.anthropic.claude-sonnet-4-6`, requires local AWS credentials and model access, and may incur inference charges.

## AgentCore deployment templates

See [`agentcore/README.md`](agentcore/README.md) for account-free templates and deployment guidance. Deployers provide their own target account, Region, specialist runtime ARN, and least-privilege role policy locally.

## Tests

```zsh
uv run python -m unittest discover -s tests -v
```

## Optional sample catalog

The sample catalog is synthetic example data for demonstrating a static tool call. It is not a live service, a recommendation engine, or an event schedule.

## Security

If you discover a potential security issue, follow the process in [CONTRIBUTING.md](CONTRIBUTING.md#security-issue-notifications). Do not create a public issue for a potential vulnerability.

## License

This project is licensed under the [MIT-0 License](LICENSE).
