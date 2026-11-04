# Local A2A example

This directory contains the smallest runnable example in the repository. You can use any editor and two terminals.

## Run the deterministic protocol example

Terminal 1 starts the Strands specialist:

```zsh
uv run python talk/strands_analyst.py --model rehearsal
```

Terminal 2 runs the LangGraph coordinator:

```zsh
uv run python talk/langgraph_researcher.py \
  --prompt "Design a document retrieval architecture for a curated knowledge catalog."
```

The coordinator discovers the AgentCard, submits an A2A task, handles `input-required`, resumes the same task and context, and prints the returned artifacts.

## Optional local Bedrock mode

```zsh
uv run python talk/strands_analyst.py --model bedrock
```

This uses a real Strands agent backed by Claude Sonnet 4.6 through Amazon Bedrock. It remains loopback-only, requires local AWS credentials and model access, and may incur inference charges.

## Optional extensions

- `session_recommender_tool.py` demonstrates a Strands tool over static JSON.
- `sample-catalog.json` is synthetic catalog example data, not a prerequisite for A2A.
- `run_agentcore_demo.py` is a generic, signed invocation helper for a separately deployed AgentCore runtime. Pass the target at runtime:

```zsh
uv run python talk/run_agentcore_demo.py \
  --runtime-prefix "YOUR_RUNTIME_PREFIX" \
  --prompt "Design a secure cross-framework agent architecture."
```

## Presentation materials

Presentation-specific assets are optional and are not required to reuse the pattern:

- [Presentation guide](../presentation/presenter-guide.md)
- [10-slide storyboard](../presentation/10-slide-storyboard.html)
