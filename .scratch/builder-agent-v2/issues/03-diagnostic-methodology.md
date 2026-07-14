# 03 · Diagnostic methodology — root-cause isolation

Type: research
Status: resolved
Blocked by: none

## Question

Define the disciplined **method** for isolating an agent failure to its layer — **instructions vs. grounding vs. orchestration vs. moderation vs. action** — adapted from general LLM/agent debugging to these two Microsoft surfaces. This is the reasoning procedure the diagnose→revise flow will encode.

Resolve, grounded in current (2026) Microsoft Learn guidance + established LLM-agent debugging practice:

- A **layered isolation procedure**: given a symptom + pasted evidence, how to decide *which layer* is responsible before touching anything — the ordered questions / checks that binary-search the AgentSpec (is it grounding? instructions? orchestration? moderation? the action?).
- The **minimal-change → re-test** loop: change one thing, ask the maker to re-run, confirm — and how that maps to the surfaces' Test panes.
- Microsoft's own recommended debugging/iteration guidance (e.g., instruction-tuning advice, the GPT 5.0→5.1 literal-execution mitigation, orchestration-trace reading, "allow ungrounded responses" as a grounding probe).
- How the method differs by surface (declarative's fixed pipeline gives fewer knobs; Copilot Studio's generative orchestration + topics + flows give more layers to isolate).
- Output a **step-by-step diagnostic algorithm** the flow-design ticket (06) can turn into conversation steps.

Capture findings to `.scratch/builder-agent-v2/research/03-diagnostic-methodology.md` with source links.

## Answer

Full write-up: `.scratch/builder-agent-v2/research/03-diagnostic-methodology.md`.

- **Five layers, one pipeline.** Every turn runs Moderation → Action → Orchestration → Grounding → Instructions. A bug lives in exactly one layer even when it *presents* as another; the method's job is to stop makers rewriting instructions when the fault is a tool description or a moderation threshold. **Instructions are the residual — diagnosed LAST**, because the four lower layers emit objective machine signals and instructions do not.
- **Binary-search order (change nothing until it terminates):** Q1 Blocked on benign input? → *Moderation*. Q2 Selected component errored / bad params / timeout? → *Action*. Q3 Wrong or no tool/topic/knowledge selected? → *Orchestration*. Q4 Right component ran but empty/wrong evidence? → *Grounding*. Q5 Right data, wrong behavior (rule/tone/format/step order/over-under-calling)? → *Instructions*. Objective signals gate first; retrieval is only meaningful once the right source was even selected.
- **Evidence surfaces to paste in.** M365 declarative: **`-developer on`** debug card (Agent metadata; Capabilities; *Matched* vs *Selected functions*; Execution details w/ latency + request/response) or Toolkit **F5 Debug panel** + per-capability `.txt` log. Copilot Studio: **Test pane** (fired-node checkmarks, Track between topics, Variables Test tab, **Save snapshot → dialog.json**) + **Activity map** knowledge/action nodes + **Rationale** + **Chain of Thought** + **App Insights KQL** (`ContentFiltered`) + transcripts.
- **Confirm-before-you-change probes.** Grounding = **Allow ungrounded responses OFF** (CS) or base-Copilot A/B (declarative); Moderation = drop threshold one notch and re-ask; Action = re-check params/host-URL/OpenAPI/<10 s; Orchestration = read Rationale/CoT for *why* the wrong pick.
- **Minimal-change → re-test loop.** One reversible change on the right lever → re-run the identical prompt 2–3× (probabilistic) → confirm the *signal* flipped (function now Selected, node now cites right source, params now valid, no ContentFiltered), not just the visible answer → regression-check starters → **revert if flat**. Lever per layer: Instructions=one rule / literal-execution header; Orchestration=**name first**, then description; Grounding=scope/permissions/freshness; Moderation=threshold notch; Action=param/OpenAPI/timeout.
- **Declarative = fewer knobs.** Fixed sequential Copilot pipeline: Orchestration collapses to "did a function match/get selected" (description-only lever, no reorder/loop), **no moderation knob** (inherited M365 RAI), **no strict-grounding toggle** (Agent Builder only *prioritizes*), single evidence surface (the dev-mode card). Most diagnoses land in Instructions / Grounding / Action.
- **Copilot Studio generative = more layers, richer instrumentation.** Orchestration is first-class and tunable (visible plan + Rationale + CoT), Action spans connectors/flows/prompts/MCP with deterministic/hybrid/AI control boundaries, Moderation is maker-configurable (Lowest→Highest, default High), grounding has the clean ungrounded-OFF probe, and the **Fallback system topic** owns "can't help" (edit the topic, not instructions). More places to hide, far more instrumentation to find them.
- **Microsoft's own iteration guidance:** iterate day one, **one small change at a time**; instruction-tune (say what to DO, atomic steps, always set tone/format); **literal-execution header** as interim stabilizer after GPT 5.0→5.1 auto-migration causes step reordering; read the activity-map plan for wrong picks; don't fix system behavior (fallback, citations, retrieval) in instructions.
- **Version flags:** Chain of Thought is model-gated (GPT-5 Reasoning, Claude Sonnet/Opus); activity map + Rationale need generative orchestration; historical Activity needs Exchange license, App Insights needs an Azure subscription; declarative plugin API timeout = 10 s; re-run the whole diagnostic after model auto-upgrades.
- **Step-by-step algorithm for the flow (ticket 06):** Intake+evidence → Reproduce → Binary-search the layer (change nothing) → Confirm with a probe → Propose ONE minimal fix on the right lever → Re-test the same signal → Iterate or revert; escalate to a surface switch when a declarative ceiling (loops/autonomy/strict grounding/>8k) is hit rather than tweaking again.
