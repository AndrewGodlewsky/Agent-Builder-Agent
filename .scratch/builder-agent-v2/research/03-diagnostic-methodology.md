# 03 · Diagnostic methodology — root-cause isolation across five layers

_Research findings — grounded in current (2026) Microsoft Learn documentation (fetched 2026-07-14; doc `ms.date` values Nov 2025 – Jul 2026, noted per source) plus established LLM-agent debugging discipline. Builds on research/01 (building blocks) and research/02 (what makes an agent good)._

> **Purpose.** This is the reasoning procedure the diagnose→revise conversation flow (ticket 06) will encode. Given a **symptom + pasted evidence**, it decides **which of five layers** — instructions · grounding · orchestration · moderation · action — owns the failure *before anything is changed*, then drives a disciplined minimal-change → re-test loop. The five-layer model is our framing; Microsoft's docs describe the same pipeline as orchestrator (planner) → knowledge → tools/actions, wrapped by content moderation, and steered by instructions.

---

## Part A — The five layers and their discriminating symptoms

Every agent turn runs the same pipeline. A failure lives in exactly one layer even when it *presents* as another; the method's whole job is to stop makers from "fixing" the instructions when the real fault is a tool description or a moderation threshold. The general discipline is the standard debugging loop — **reproduce → localize with evidence → form one hypothesis → change one variable → re-test → confirm** — adapted to the fact that agent behavior is probabilistic (run each check 2–3× and look at the majority, per research/02 §5).

| Layer | What it owns | Canonical symptom (how it *looks*) | Primary evidence surface |
|---|---|---|---|
| **Moderation** | Responsible-AI content filtering on input **and** output | Response blocked/blank; `ContentFiltered`; generic safety refusal on *benign* input; jailbreak/injection rejection | CS: `ContentFiltered` error + App Insights KQL + transcript. M365: inherited M365 RAI (not maker-visible) |
| **Action** | Tool/plugin/flow *execution* (params, HTTP, timeout) | Right tool was chosen but errored, returned empty, timed out, or got wrong/missing parameters | M365 dev-mode card *execution details*; CS activity-map action node (highlights missing/invalid input/output params) |
| **Orchestration** | *Selection & sequencing* — which topic/tool/knowledge/agent, in what order (routing) | Wrong tool/topic picked; right one never invoked; multi-intent dropped; bad disambiguation; wrong order | M365 card *Matched / Selected functions*; CS activity map (the plan) + **Rationale** + **Chain of Thought** |
| **Grounding** | Retrieval — did the right evidence come back | Wrong/missing/stale facts; hallucination; "I don't know" when source exists; no/wrong citation | M365 card *executed capability* (search text, #results); CS activity-map **knowledge node** (search phrase, sources used vs. searched-but-unused) |
| **Instructions** | Behavior shaping once data is in hand — rules, tone, format, step order, when to call tools | Correct data present but **shaped wrong**: rule ignored, wrong tone/verbosity/format, step skipped/reordered, tool over- or under-called | The instruction text itself; residual after all machine layers read green |

**Design principle — Instructions are the *residual*, diagnosed last.** The four lower layers emit objective machine signals (a block, an execution error, a selection status, a retrieval result). Instructions have none — they are the default explanation only when moderation, action, orchestration, and grounding all check out but the behavior is still wrong. Makers instinctively rewrite instructions first; the method forces that to be the *last* move, not the first.

---

## Part B — Evidence surfaces (what to paste, per surface)

The isolation procedure is only as good as the evidence read into it. The two surfaces expose very different instrumentation.

### B.1 M365 declarative agent — **Developer Mode** debug card
Source: [Test and debug agents in Microsoft 365 Copilot using Developer Mode](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-copilot-studio) (`ms.date` 2025-11-17) and [Test and debug agents in Microsoft 365 Agents Toolkit](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-vscode) (`ms.date` 2025-05-19).

- Enable in Copilot / Copilot Chat by typing **`-developer on`** (disable with `-developer off`). In **Agents Toolkit**, run **Preview your app (F5)** in VS Code, then `-developer on`; debug info renders in the **Debug panel**.
- A debug card returns **only when the orchestrator actually searched your knowledge / capabilities / actions.** Card fields:
  - **Agent metadata** — Agent ID (title + manifest), Agent version, Conversation ID, Request ID (paste these when flagging).
  - **Capabilities** — configured knowledge scope; execution status; response stats. *(Toolkit adds a downloadable per-capability diagnostic `.txt` log.)*
  - **Actions** — Action ID + version; **Matched functions** (semantically matched in the runtime app-index lookup) and **Selected functions for execution** (chosen by orchestrator reasoning).
  - **Execution** — *Executed capabilities* (search text used, response, #results returned) and *Executed actions* (function status, **latency**, request endpoint/HTTP method/headers, response).
- Diagnostic tells (these ARE the branch conditions):
  - **No debug card** → orchestrator didn't need your data/skills → it answered from **general model knowledge** (grounding never engaged) — *or* capacity throttling (you'll see a try-again error).
  - **"No matched functions"** → the prompt didn't semantically match the action — likely the prompt never named it / the **description** is off (orchestration).
  - **"No functions selected for execution"** → the manifest command description isn't semantically related to the intent (orchestration/description). If it *used* to work → throttling.
  - **Empty/failed function execution details** → parameter-binding failure → unclear action/parameter descriptions, invalid host URL, or a broken OpenAPI definition (action). **Plugin API timeout = 10 s**; message-extension best practice < 9 s.

### B.2 Copilot Studio — **Test your agent** pane + **Activity map** + **App Insights**
Sources: [Test your agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot) (`ms.date` 2026-07-02), [Review agent activity](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-review-activity) (`ms.date` 2026-06-22), [Resolve responsible AI content filter errors](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai) (`ms.date` 2026-06-09).

- **Test your agent** pane (design-time): type a prompt; select any response to **jump to the originating node** (fired nodes get a colored checkmark + bottom border); **Track between topics** (…-menu) follows the flow across topics; **Variables → Test tab** shows live variable values; **Save snapshot** (…-menu) writes `botContent.zip` → **`dialog.json`** (conversational diagnostics incl. detailed error descriptions) + `botContent.yml`. Reset clears the conversation. **Caveat:** the pane is design-time only — timer/background/inactivity triggers may not fire; validate those in a published channel (Teams).
- **Activity map** (generative orchestration only): the visual **plan** the orchestrator generated. Turn on **Show activity map when testing** (…-menu). Node inspection is the core isolation tool:
  - **Knowledge node** — the **search query the agent actually used** (can differ from the user's wording), the response, **sources referenced**, and **other sources it searched but didn't use** (searched, found nothing relevant). This single node separates *grounding* (nothing came back / wrong source) from *instructions* (right source, wrong summary).
  - **Action node** — inputs/outputs; **highlights missing or invalid input/output parameters** and per-step latency → the *action* tell.
  - **Rationale** ("Show rationale") — AI-generated explanation of **why the agent chose a particular tool / filled a parameter** (may be inaccurate — judgment required). This is the *orchestration* tell.
  - **Chain of Thought** ("Reasoning" chevron) — intermediate reasoning steps. **Version flag: only on selected models — GPT-5 Reasoning, Claude Sonnet, Claude Opus.**
  - **Agent status** states: Submitted / In progress / Input required / Auth required / Complete / Canceled / **Failed** / Rejected.
- **Historical Activity page** — Transcript + Map for past runs (test, Teams/M365 Copilot, SharePoint, autonomous triggers); filter by **Failed / Blocked / In progress / Waiting for user / Completed**. **Version flag: requires an Exchange license + mailbox** (data stored in M365 services).
- **Moderation evidence** — the `ContentFiltered` error string, plus **App Insights KQL** (`customEvents | where customDimensions contains "ContentFiltered"`) and downloadable transcripts. **Version flag: App Insights requires an active Azure subscription.**

---

## Part C — The layered isolation procedure (binary search of the AgentSpec)

Read the evidence **from the outside of the pipeline inward**, checking the most objective machine signals first and leaving Instructions (which has no machine signal) for last. Each question has a single discriminating check; a "yes" terminates at a layer, a "no" advances. **Do not change anything until the search terminates.**

```
Q0  REPRODUCE + CAPTURE
    Re-run the exact failing prompt 2–3×. Capture evidence:
      M365 → `-developer on` card (or Toolkit F5 Debug panel + capability .txt log)
      CS   → activity map (+ Rationale/CoT) and/or Save snapshot → dialog.json
    Intermittent across runs? Note it — probabilistic; judge on the majority.

Q1  BLOCKED?  Is the answer filtered/blank, or a generic safety refusal on BENIGN input?
      CS signal: "The content was filtered due to Responsible AI restrictions" /
                 ContentFiltered (App Insights KQL / transcript).
      M365 signal: inherited M365 RAI refusal (no maker knob).
    → YES ............................................. LAYER = MODERATION   ▸ stop
    → NO  → Q2

Q2  EXECUTION ERROR?  Was a component SELECTED but it errored / returned empty /
                      timed out / got missing-or-invalid parameters?
      M365 signal: empty or failed function execution details; latency near/over 10 s.
      CS signal:   action node red / highlighted missing-invalid input-output params;
                   dialog.json error detail; status = Failed.
    → YES ............................................. LAYER = ACTION       ▸ stop
    → NO  → Q3

Q3  SELECTION CORRECT?  Did the orchestrator pick the RIGHT tool/topic/knowledge,
                        and in the right order? (routing)
      M365 signal: "No matched functions" / "No functions selected for execution" /
                   the wrong function selected.
      CS signal:   plan shows wrong/missing node; Rationale explains a wrong choice;
                   multi-intent request only partly planned.
    → WRONG / MISSING SELECTION ...................... LAYER = ORCHESTRATION ▸ stop
    → RIGHT COMPONENT RAN → Q4

Q4  EVIDENCE CORRECT?  Did retrieval return the right facts?
      M365 signal: no debug card at all (answered from general model knowledge);
                   executed-capability shows 0 / irrelevant results.
      CS signal:   knowledge node — empty results, wrong search phrase, or the right
                   source sits under "searched but didn't use."
      Grounding PROBE (see Part D) to confirm.
    → MISSING / WRONG / UNCITED FACTS ................ LAYER = GROUNDING     ▸ stop
    → RIGHT DATA CAME BACK → Q5

Q5  DATA RIGHT, BEHAVIOR WRONG?  Correct facts/tools in hand, but rule ignored,
    wrong tone/verbosity/format, step skipped or reordered, tool over-/under-called?
    → YES (residual) ................................. LAYER = INSTRUCTIONS  ▸ stop
```

**Why this order.** Moderation and Action are terminal, unambiguous machine states — a block or an execution error fully explains the turn, so they gate first. Orchestration (selection) precedes Grounding (retrieval) because a retrieval result is only meaningful once you know the *right* source was even chosen. Instructions is the residual (Part A principle). Two symptoms that fool makers: (a) "it hallucinated" is usually **Grounding** (nothing retrieved) but can be **Instructions** ("Allow ungrounded responses" left ON telling it to fill gaps) — Q4's probe disambiguates; (b) "it ignored my rule" is usually **Instructions** but can be **Moderation** silently overriding — Q1 gates that.

---

## Part D — The grounding probe and other confirm-before-you-change tests

Before editing, run a cheap **A/B probe** that flips exactly one condition to confirm the layer:

- **"Allow ungrounded responses" OFF (Copilot Studio) — the grounding probe.** OFF forces the agent to answer *only* from a tool/knowledge call; any turn that didn't ground now falls back instead. If the failing answer **turns into a fallback with OFF**, retrieval genuinely isn't returning the facts → **Grounding** confirmed. If it still answers correctly, grounding was fine and the fault was elsewhere. (Caveat from research/02: OFF also disables follow-up/clarifying questions, and doesn't *guarantee* zero general knowledge.) Source: [Knowledge sources overview — content moderation & ungrounded responses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio).
- **With / without knowledge (both surfaces).** Remove (or add) the source and re-ask. Invents the answer without the source but gets it right once added → grounding works; over-uses a source it shouldn't → scope or instruction problem. (research/02 §2.)
- **Compare against base Microsoft 365 Copilot (declarative).** Declarative has no strict-grounding toggle, so instead ask base Copilot the same prompt: if the agent adds no value / behaves identically, the added knowledge isn't being used → grounding/orchestration. Source: [debugging-agents-copilot-studio](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-copilot-studio), [declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions).
- **Moderation notch probe.** Drop the moderation level one step (Lowest→Highest, default **High**, per agent/topic/prompt) and re-ask the benign prompt. Unblocks → **Moderation** confirmed; still blocked → not moderation. Source: [agent-response-filtered-by-responsible-ai](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai).

---

## Part E — The minimal-change → re-test loop

Once a layer is isolated, fix with the smallest reversible edit and re-verify against the *same* evidence surface.

1. **One change, one hypothesis.** Change exactly one thing — one instruction line, one tool/topic **description**, one parameter, one moderation notch. Never stack edits; you lose attribution of what worked.
2. **Re-run the identical prompt** in the Test pane 2–3× (probabilistic).
3. **Re-read the same evidence** (dev-mode card / activity-map node / dialog.json) and confirm the *signal* flipped, not just the visible answer — e.g., the function now shows **Selected for execution**, the knowledge node now lists the right **source referenced**, the action node params are now valid.
4. **Revert if no effect.** A change with no measurable signal change is noise — undo it before trying the next hypothesis.
5. **Regression-check** the conversation starters / a couple of adjacent prompts so the fix didn't break a neighbor (research/02 §5 evaluation categories).

### Layer → fix lever → Test-pane mapping

| Isolated layer | Minimal fix lever | Confirm on (M365) | Confirm on (Copilot Studio) |
|---|---|---|---|
| **Instructions** | Tighten one rule; say what to *do*; make the step atomic; for post-model-upgrade step reordering apply the **literal-execution header** (GPT 5.0→5.1 mitigation) | `-developer on` card + built-in test chat / Toolkit F5 | Test pane fired-node trace; re-ask |
| **Grounding** | Scope/refresh the source; fix permissions; narrow to the folder/site; add "use `Source` for X" hint | dev-mode executed-capability (search text, #results); base-Copilot A/B | knowledge node (referenced vs. unused); **Allow ungrounded OFF** probe |
| **Orchestration** | Fix the **name** first (weighs most), then description; remove overlap; add one example utterance to the description | dev-mode Matched / Selected functions | activity-map plan + **Rationale** + **Chain of Thought** |
| **Moderation** | Reinforce RAI with users; drop moderation threshold one notch; add instruction stating the behavior is expected | (inherited M365 RAI — no maker knob) | re-ask; App Insights KQL `ContentFiltered`; transcript |
| **Action** | Fix parameter/description; validate host URL & OpenAPI; ensure < 10 s; add input description/validation (CS) | dev-mode execution details (status, latency, request/response) | activity-map action node params; `dialog.json` |

---

## Part F — How the method differs by surface

The pipeline is identical; the number of **isolatable layers** and the **instrumentation** differ sharply.

### F.1 M365 declarative agent — fixed pipeline, fewer knobs
- **Orchestration collapses to "did a function match/get selected."** The pipeline is Copilot-controlled, sequential grounding-then-tool (research/01 §A.6); you cannot reorder, loop, or add planning. So the orchestration layer isn't *tuned* — it's only *observed* (Matched vs. Selected functions), and the only lever is **description quality**.
- **No moderation knob.** RAI is inherited from M365 and is not maker-configurable; a moderation diagnosis ends in "rephrase / accept," not a threshold change.
- **No strict-grounding toggle.** Agent Builder's "Only use specified sources" merely *prioritizes* (research/01 §A.4) — the grounding probe is the base-Copilot A/B comparison, not an ungrounded-responses switch.
- **Single evidence surface:** the `-developer on` card (or Toolkit Debug panel + per-capability `.txt` log). No activity map, no Rationale, no CoT.
- Net: **fewer places a bug can hide, fewer knobs to turn** — most declarative diagnoses land in Instructions, Grounding, or Action; Orchestration reduces to description tuning; Moderation is non-actionable.

### F.2 Copilot Studio (generative) agent — more layers, richer instrumentation
- **Orchestration is a real, first-class, tunable layer:** the LLM planner selects and sequences topics/tools/knowledge/child agents; the plan is visible in the **activity map**, explained by **Rationale**, and traced by **Chain of Thought**. Names/descriptions are the lever ("names matter more than anything — if the agent chooses the wrong topic, revisit names and descriptions" — [generative-orchestration guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration)).
- **More sub-layers within Action:** connectors, agent flows (deterministic), prompts, MCP tools — each with its own params and the **deterministic / hybrid / AI** control-boundary model (mission-critical steps wrapped in confirmation/approval so the planner can't override them).
- **Moderation is maker-configurable** (Lowest→Highest, per agent/topic/prompt) and independently observable (App Insights, transcripts).
- **Grounding has the strict `Allow ungrounded responses` toggle** + tenant-graph semantic search — a clean, cheap probe.
- **Topics add a control layer declarative lacks:** the **Fallback system topic** owns the "can't help" behavior — a fallback firing is an *orchestration/scope* signal, edited in the topic, **not** in instructions (research/02 §3).
- Net: **more layers to isolate, but far more instrumentation to isolate them with.** The activity map, Rationale, CoT, snapshot, and App Insights make the binary search almost mechanical; the cost is a larger surface (topics, flows, agents) where a fault can originate.

### F.3 Microsoft's own iteration guidance (both surfaces)
- **Iterate from day one; make one small change at a time and watch its effect on the agent's decisions** ([generative-orchestration guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration); declarative: *create → publish → test → iterate*, [declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions)).
- **Instruction tuning:** say what to DO not avoid; atomic steps; always specify tone/verbosity/format; **literal-execution header** as the interim stabilizer when a model auto-upgrade (GPT 5.0→5.1) causes step reordering/added steps (research/02 §1). **Version flag:** model auto-migration is an ongoing moving target — re-test after upgrades.
- **Read the plan:** inspect the activity map after a complex query — which topics/actions fired, in what order, did it ask the right follow-up; wrong pick → refine descriptions ([generative-orchestration guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration)).
- **Grounding probe:** toggle **Allow ungrounded responses** OFF to force grounded answers ([knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)).
- **Don't fix system behavior in instructions:** fallback = Fallback topic; citations are system-controlled; instructions can't override search-retrieval logic (research/02 §1).

---

## Part G — Version-dependent / watch items
- **Chain of Thought** in the Test pane and Activity map is **model-gated** — GPT-5 Reasoning, Claude Sonnet, Claude Opus only. On other models, fall back to Rationale + node inspection.
- **Activity map / Rationale** require **generative orchestration**; classic-orchestration agents rely on the topic-node trace (fired-node checkmarks) + snapshot instead.
- **Historical Activity** needs an **Exchange license + mailbox**; **App Insights** moderation telemetry needs an **active Azure subscription**.
- **Model auto-migration (GPT 5.0→5.1 and onward)** shifts instruction interpretation from literal to intent-first — expect behavior drift and re-run the diagnostic after upgrades.
- **M365 developer-mode card fields** (`ms.date` 2025-11-17) and Toolkit developer mode (`ms.date` 2025-05-19) are the newest-verified; Copilot Studio activity/test docs are Jun–Jul 2026.
- Declarative **plugin API timeout = 10 s** (message-extension best practice < 9 s) — a hard action-layer constant worth encoding as a check.

---

## Part H — The step-by-step diagnostic algorithm (encode this in the flow)

The conversation flow (ticket 06) should walk the maker through these steps, one question at a time, never proposing a fix before **STEP 6**.

```
STEP 1 · INTAKE
  Ask for: (a) the exact prompt, (b) what happened, (c) what was expected,
           (d) which surface (M365 declarative | Copilot Studio).
  Ask the maker to paste EVIDENCE:
     M365 → run `-developer on`, resend the prompt, paste the debug card
            (Toolkit users: F5 Debug panel + capability .txt log).
     CS   → open the activity map (Show activity map when testing) and/or
            Save snapshot (dialog.json); paste the node details / Rationale / CoT.
  If no evidence yet, that IS step one — get it before reasoning.

STEP 2 · REPRODUCE
  Confirm it reproduces (2–3 runs). If intermittent, flag "probabilistic —
  judge on the majority" and, on CS, suspect throttling / model variance.

STEP 3 · BINARY-SEARCH THE LAYER (Part C, in order — CHANGE NOTHING)
  Q1 Blocked / filtered on benign input?          → MODERATION → STEP 4
  Q2 Selected component errored / bad params /
     empty / timeout?                              → ACTION      → STEP 4
  Q3 Wrong or no tool/topic/knowledge selected?    → ORCHESTRATION → STEP 4
  Q4 Right component ran but wrong/empty evidence?  → GROUNDING   → STEP 4
  Q5 Right data, wrong behavior (rule/tone/format/
     step order/over-under-calling)?               → INSTRUCTIONS → STEP 4
  State the isolated layer and the single evidence signal that proves it.

STEP 4 · CONFIRM WITH A PROBE (Part D — still a diagnostic, not a fix)
  GROUNDING     → Allow-ungrounded OFF (CS) or base-Copilot A/B (M365).
  MODERATION    → drop threshold one notch (CS), re-ask benign prompt.
  ACTION        → re-check params/host URL/OpenAPI/latency<10s.
  ORCHESTRATION → read Rationale/CoT for WHY the wrong pick.
  INSTRUCTIONS  → locate the exact rule/line implicated.
  If the probe contradicts the layer, return to STEP 3.

STEP 5 · MINIMAL FIX PROPOSAL (Part E lever table)
  Propose exactly ONE reversible change on the right lever for the layer.
  Instructions: prefer literal-execution header if step reordering followed a
  model upgrade. Orchestration: fix the NAME before the description.
  Moderation/grounding/action: use the platform knob, not an instruction edit.
  Explicitly warn against editing instructions for a non-instruction layer.

STEP 6 · RE-TEST & VERIFY (Part E loop)
  Re-run the identical prompt 2–3× in the Test pane.
  Re-read the SAME evidence surface; confirm the SIGNAL flipped
  (function now Selected; knowledge node now cites right source;
   action params now valid; no ContentFiltered).
  Regression-check the conversation starters / an adjacent prompt.

STEP 7 · ITERATE OR ESCALATE
  Signal flipped + regression clean → done; note the change.
  No change → REVERT, return to STEP 3 with the new evidence.
  Cross-cutting / declarative-ceiling hit (needs loops, autonomy, strict
  grounding, >8k instructions) → recommend the surface switch (research/01 §C.3),
  not another instruction tweak.
```

**One-line invariant:** *Capture evidence → binary-search Moderation → Action → Orchestration → Grounding → Instructions (residual) → probe to confirm → change one lever → re-test the same signal → revert if flat.*

---

## Sources (all fetched 2026-07-14)
- Test and debug agents in Microsoft 365 Copilot using Developer Mode — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-copilot-studio
- Test and debug agents in Microsoft 365 Agents Toolkit (developer mode) — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-vscode
- Review agent activity (activity map, Rationale, Chain of Thought) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-review-activity
- Test your agent (Test pane, node tracing, snapshot) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot
- Apply generative orchestration capabilities (testing & tuning, names/descriptions, control layers) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration
- Resolve responsible AI content filter errors (ContentFiltered, App Insights KQL) — https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai
- Knowledge sources overview (content moderation, Allow ungrounded responses) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- Write effective instructions for declarative agents (iteration, literal-execution header) — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions
- Configure high-quality instructions for generative orchestration — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance
- Orchestrate agent behavior with generative AI — https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions
- Internal: research/01 (building blocks), research/02 (what makes an agent good)
