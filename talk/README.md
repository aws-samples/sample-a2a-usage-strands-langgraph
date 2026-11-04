# On-stage code path

Use these files in Kiro—do not scroll through the rest of the repository.

1. `strands_analyst.py` — Agent 2: A2A receiving specialist.
2. `langgraph_researcher.py` — Agent 1: A2A coordinating workflow.
3. `session_recommender_tool.py` — optional extension showing a normal Strands tool over static JSON.
4. `reinvent-2026-curated-sessions.json` — optional static session catalog.

## Primary talk flow: deterministic local A2A

Terminal 1:

```zsh
uv run python talk/strands_analyst.py --model rehearsal
```

Terminal 2:

```zsh
uv run python talk/langgraph_researcher.py \
  --prompt "Design a minimal session-guide retrieval architecture."
```

Narrate the output in this order:

1. AgentCard discovery
2. Task submitted / working
3. `input-required`
4. Same task + context resumes
5. Named artifacts
6. `completed`

## Optional local Sonnet 4.6 practice

```zsh
uv run python talk/strands_analyst.py --model bedrock
```

This is for rehearsal or an optional extension. It remains loopback-only, requires local Bedrock credentials/model access, and may incur inference charges.

## Optional AgentCore proof

For an account-specific, pre-deployed demo environment only:

```zsh
uv run python talk/run_agentcore_demo.py \
  --runtime-prefix "YOUR_LANGGRAPH_RUNTIME_PREFIX" \
  --prompt "Design a secure multi-agent architecture with AgentCore, Strands, LangGraph, and A2A."
```

Do not publish the local `deployments/` directory: it is intentionally Git-ignored because it contains account-bound deployment material.

## Presenter materials

* [Presenter guide](presenter-guide.md) — slide talk track, Kiro checkpoints, commands, and recovery cues.
* [10-slide storyboard](opn408-10-slide-storyboard.html) — self-contained visual deck; open it in a browser or print to PDF.
