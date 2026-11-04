# OPN408 presenter guide

This guide is the talk track for the 60-minute Code Talk. Keep the slides short. Spend most of the session in Kiro and the terminal.

## Speaker principle

Tell the audience the victory condition before you type:

> A LangGraph coordinator will discover a Strands specialist through an A2A AgentCard, submit a task, receive `input-required`, resume the same task and context, and receive named artifacts.

The local demo proves the protocol deterministically. The managed-runtime proof shows the same collaboration through an authenticated runtime boundary.

## Slide 1 — hook and QR code

**Show:** title, victory condition, and QR code for the repository.

**Say:**

> “This is not a framework comparison. It is a collaboration boundary. The two agents share no code, tools, prompt, memory, or framework internals. They only share A2A.”

Ask: “Who already has more than one agent framework, or expects to?”

## Slide 2 — draw Agent 2 first

**Show:** Strands specialist.

**Say:**

> “Agent 2 owns specialist knowledge. It is the right place to make architecture decisions and, optionally, use focused tools.”

**Kiro checkpoint:** `talk/strands_analyst.py`, lines 38–61.

Point at `BEDROCK_MODEL_ID` only when discussing optional local Sonnet 4.6 practice. The primary local demo uses `--model rehearsal`.

## Slide 3 — draw the A2A boundary

**Show:** Agent 1 ↔ A2A contract ↔ Agent 2.

**Say:**

> “A2A is the common wire contract. Agent 2 keeps its prompt, model, tools, and memory private. Agent 1 relies on published capabilities, task state, and artifacts.”

Do not say AgentCard discovery is authentication. Discovery and authorization are separate.

## Slide 4 — draw Agent 1

**Show:** LangGraph coordinator.

**Say:**

> “Agent 1 owns the user journey: discover a specialist, submit work, provide missing context, and display results. It does not need to be the specialist.”

**Kiro checkpoint:** `talk/langgraph_researcher.py`, lines 100–115.

Point at the explicit graph: `discover → submit_task → resume_task`.

## Slide 5 — narrate the lifecycle

**Show:** user → LangGraph → Strands → artifacts.

**Say:**

> “A task is a collaborative work item, not one opaque chat completion. The specialist can move it to `input-required` rather than guessing.”

Ask: “What document details would you need before choosing a retrieval architecture?”

If the room is quiet: formats, corpus size, update cadence, and metadata quality.

## Slide 6 — show the Strands A2A server

**Kiro checkpoint:** `talk/strands_analyst.py`, lines 64–138.

**Say:**

> “The rehearsal executor makes the lifecycle visible. It is deliberately deterministic so we can rehearse without credentials, latency, or model variability.”

Point at:

- task creation/resumption;
- the `working` state;
- `TaskState.input_required` on lines 89–99;
- the three named artifacts;
- `completed`.

**Gotcha:** do not call fixed rehearsal artifacts an LLM result or a RAG result.

## Slide 7 — show the AgentCard

**Kiro checkpoint:** `talk/strands_analyst.py`, lines 141–183.

**Say:**

> “This is the public contract. LangGraph can discover the agent’s name, endpoint, skill, and streaming capability without importing Strands.”

Point at `AgentCard(...)`, then explain that the server binds to `127.0.0.1` for local rehearsal only.

## Slide 8 — live local protocol proof

Terminal 1:

```zsh
uv run python talk/strands_analyst.py --model rehearsal
```

Terminal 2:

```zsh
uv run python talk/langgraph_researcher.py \
  --prompt "Design a minimal session-guide retrieval architecture."
```

Narrate the visible output:

```text
[discovery]
[task]
[state] input-required
[resume]
[artifact]
[state] completed
```

**Scripted live-coding segment:** reveal or type the `TaskState.input_required` block. Explain that the specialist asks for an engineering constraint instead of silently guessing.

## Slide 9 — show LangGraph continuation

**Kiro checkpoint:** `talk/langgraph_researcher.py`, lines 116–151.

**Say:**

> “The crucial line is not a framework adapter. It is reuse of the same task ID and context ID. That makes the document profile a continuation of work rather than a fresh request.”

Point at `streaming_request(... task_id, context_id)`.

## Slide 10 — managed proof and survey close

**Show:** pre-captured AgentCore screenshot or short recording. Do not navigate the console live.

**Say:**

> “The local demo proves the A2A lifecycle. The managed proof runs the coordinator and specialist independently with the deployment boundary handling authentication and service-to-service authorization.”

For a prepared environment, run:

```zsh
uv run python talk/run_agentcore_demo.py \
  --runtime-prefix "YOUR_LANGGRAPH_RUNTIME_PREFIX" \
  --prompt "Design a secure multi-agent architecture with AgentCore, Strands, LangGraph, and A2A."
```

Close with:

> “Before you leave, open the re:Invent mobile app, find OPN408, and complete the session survey.”

## Optional extension: local Sonnet 4.6 and static session tool

Use this only after the core A2A proof lands:

```zsh
uv run python talk/strands_analyst.py --model bedrock
```

This mode can call `recommend_reinvent_sessions` over the static curated JSON snapshot. State clearly:

> “This catalog is an unofficial static snapshot. Verify timing and availability in the official event catalog.”

RAG, embeddings, and live catalog refresh are future work, not the core OPN408 lesson.

## Recovery

| Situation | Move |
|---|---|
| Local server is not responding | Confirm terminal 1 is running and bound to `127.0.0.1:9000`. |
| Audience cannot read the code | Increase editor/terminal zoom and rerun the one command. |
| `input-required` is confusing | Re-state that it is a valid task state, not an error. |
| Managed proof is unavailable | Use the pre-captured screenshot/recording, then return to the working local protocol flow. |
| Session search is off-topic | Leave the tool as an extension and return to AgentCard/task/context/artifacts. |
