# OPN408 — cross-framework A2A Code Talk

A small, teaching-first sample for **Connect agents across frameworks live using the A2A open protocol (OPN408)**.

## What this repository teaches

A local LangGraph coordinator discovers a local Strands specialist through an A2A AgentCard, submits a task, receives `input-required`, resumes the **same task and context**, and renders named artifacts.

```text
LangGraph coordinator
  └── AgentCard discovery
      └── A2A task
          └── input-required
              └── same-task resumption
                  └── artifacts + completed
Strands specialist
```

## The public teaching surface

| File | Why it exists |
|---|---|
| `talk/strands_analyst.py` | Agent 2: loopback-only Strands A2A server. Defaults to deterministic rehearsal; optional local Sonnet 4.6 mode. |
| `talk/langgraph_researcher.py` | Agent 1: compact LangGraph workflow for discovery, task submission, and continuation. |
| `talk/session_recommender_tool.py` | Optional static-JSON Strands tool. It is an extension, not the core A2A lesson. |
| `talk/reinvent-2026-curated-sessions.json` | Curated, paraphrased session snapshot for the optional recommendation tool. |
| `talk/run_agentcore_demo.py` | Optional signed invocation script for a separately deployed AgentCore proof. |
| `talk/presenter-guide.md` | Slide-by-slide talk track, Kiro checkpoints, commands, and recovery cues. |
| `agentcore/` | Account-free AgentCore templates for the two managed runtimes. |
| `talk/opn408-10-slide-storyboard.html` | Self-contained visual 10-slide storyboard. |

## Local rehearsal: deterministic A2A

Terminal 1 starts Agent 2:

```zsh
uv sync
uv run python talk/strands_analyst.py --model rehearsal
```

Terminal 2 runs Agent 1:

```zsh
uv run python talk/langgraph_researcher.py \
  --prompt "Design a minimal session-guide retrieval architecture."
```

The default rehearsal requires no AWS credentials and emits visible state transitions:

```text
[discovery] AgentCard retrieved
[task] submitted
[state] working
[state] input-required
[resume] document profile supplied
[artifact] architecture-rationale
[artifact] cdk-guidance
[artifact] decision-summary
[state] completed
```

## Optional local Claude Sonnet 4.6 path

To use a real local Strands model, configure AWS credentials and Bedrock access, then run:

```zsh
uv run python talk/strands_analyst.py --model bedrock
```

This mode uses `global.anthropic.claude-sonnet-4-6`. It can use the optional static session-recommendation tool. It remains loopback-only and may incur Bedrock inference charges.

## Test

```zsh
uv run python -m unittest discover -s tests -v
```

## Public-data note

The session catalog is an unofficial public planner snapshot with paraphrased summaries. Verify schedule, capacity, venue, and availability in the official re:Invent catalog before making recommendations.

## License

This project is licensed under the [MIT-0 License](LICENSE).
