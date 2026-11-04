# Facilitator guide: cross-framework A2A

This optional guide helps a presenter explain the sample in a live session. Use any editor and terminal. Keep the slides short and spend most of the time on the runnable source and visible protocol state.

## Outcome to state first

> A LangGraph coordinator discovers a Strands specialist through an A2A AgentCard, submits a task, receives `input-required`, resumes the same task and context, and receives named artifacts.

## Suggested flow

### 1. The roles

Show the two responsibilities before code:

- **LangGraph coordinator**: discovers a specialist, submits work, provides missing context, and renders results.
- **Strands specialist**: owns the domain decision and can use private tools.
- **A2A**: the shared contract for discovery, tasks, state updates, and artifacts.

Say: “The agents do not share prompts, tools, memory, or framework internals. They share a protocol.”

### 2. The local protocol proof

Start the specialist:

```zsh
uv run python talk/strands_analyst.py --model rehearsal
```

Run the coordinator:

```zsh
uv run python talk/langgraph_researcher.py \
  --prompt "Design a document retrieval architecture for a curated knowledge catalog."
```

Narrate the terminal output in order:

```text
[discovery]
[task]
[state] input-required
[resume]
[artifact]
[state] completed
```

### 3. Source checkpoints

| Source | What to point out |
|---|---|
| `talk/strands_analyst.py` | The `DeterministicA2AExecutor` makes task states and artifacts visible without model variability. |
| `talk/strands_analyst.py` | `TaskState.input_required` shows a specialist requesting missing requirements instead of guessing. |
| `talk/strands_analyst.py` | The `AgentCard` exposes capability, not the specialist's private implementation. |
| `talk/langgraph_researcher.py` | The `StateGraph` models discovery → submit → resume. |
| `talk/langgraph_researcher.py` | Reusing `task_id` and `context_id` turns the follow-up into continuation. |

### 4. Optional model-backed path

```zsh
uv run python talk/strands_analyst.py --model bedrock
```

This uses a real Strands agent with Claude Sonnet 4.6 through Amazon Bedrock. It is optional, requires credentials and model access, and may incur inference charges.

### 5. Optional managed-runtime proof

Use an already prepared runtime environment. Do not depend on live console navigation.

```zsh
uv run python talk/run_agentcore_demo.py \
  --runtime-prefix "YOUR_RUNTIME_PREFIX" \
  --prompt "Design a secure cross-framework agent architecture."
```

Say: “The local run proves the protocol behavior. The managed run proves that independently deployed agents can use the same contract through an authenticated service boundary.”

## Presentation gotchas

- Do not call AgentCard discovery authentication. Discovery and authorization are separate.
- Do not call the deterministic rehearsal output an LLM response.
- Do not describe the optional sample catalog as RAG or as a live recommendation service.
- Do not wait silently for a state transition. Read the visible `[state]` lines aloud.
- If the managed proof fails, return to the working local protocol proof and use a prepared screenshot or recording for the deployment view.
