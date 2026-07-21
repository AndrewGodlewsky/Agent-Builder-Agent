# Diagnostics Reference for Improving and Fixing an Existing Agent (Improve/Fix Mode)

This document is the diagnostic and improvement reference for an *already-built* Microsoft 365 (M365) declarative agent (DA) or Copilot Studio (CS) agent — not for building a new one. It covers how to diagnose and improve an existing agent through the five-layer isolation method (Moderation → Action → Orchestration → Grounding → Instructions), how to capture evidence on each surface, an entitlement pre-check, a failure taxonomy, a Copilot Studio error-code decoder, and goal-first improvement levers. Consult it whenever the agent operates in **improve/fix mode**: diagnosing wrong behavior (troubleshoot) or closing a quality gap (improve) on a deployed agent.

**The one core discipline:** *isolate the layer, change nothing until it is isolated, and verify by signal — not vibe.* Read the most objective machine signals first (a block, an execution error, a selection status, a retrieval result), leave **Instructions** for last because it has no machine signal, and confirm every fix by an objective signal that must flip — never "the answer looks better." Makers instinctively rewrite instructions first; this mode forces that to be the *last* move. The order of the five layers is load-bearing and must stay exact everywhere: **Moderation → Action → Orchestration → Grounding → Instructions.**

---

## The diagnostic domain model (ubiquitous language)

This diagnostic domain model is the shared vocabulary for improve/fix mode. Use these terms exactly; the diagnose-and-revise flow encodes a single-Finding loop over them.

| Term | Definition |
|---|---|
| **Agent-under-repair** | The maker's existing deployed agent being diagnosed. |
| **Artifact** | The agent's own config + instructions — `declarativeAgent.json` / instruction body / Copilot Studio exported-or-described config. The **required anchor**: reconstruction starts here, and without it you cannot emit a full revised artifact. |
| **Symptom** | The observed wrong behavior (troubleshoot, symptom-first) or the gap to close (improve, goal-first). |
| **Evidence** | Observed-behavior signal the maker pastes, **tiered**: *Machine signal* (dev-mode card / activity-map node / error code) **>** *Transcript* (real conversation / test-run output) **>** *Self-report* (artifact-only / described symptom). The tier sets the **confidence ceiling**. |
| **Diagnostic layer** | The pipeline stage a fault lives in — exactly **five, isolation-ordered: Moderation → Action → Orchestration → Grounding → Instructions.** Instructions is the **residual**, diagnosed last. |
| **Root cause** | The specific reason expressed in **AgentSpec terms** — a zone/field — within one layer. |
| **Finding** | The core unit: `{symptom, isolated layer, root cause, confidence, proposed Change OR Probe}`. |
| **Confidence** | High / Med / Low = *f(evidence tier, isolation cleanliness)*. Gates behavior. |
| **Probe** | A confirm-before-change action that raises confidence **without editing config** (Allow-ungrounded OFF, drop moderation a notch, re-check action params, base-Copilot A/B). The Med/Low move. |
| **Change** | The atomic fix for one Finding: `{layer, zone(s), before → after, rationale, verify-signal}`. **One per re-test cycle.** May span >1 AgentSpec zone only when it is one logical fix (e.g. add a `knowledge` source *and* reference it in `# CAPABILITIES & KNOWLEDGE`). |
| **Verify-signal** | The **objective signal that must flip** to confirm a Change worked — function now *Selected*, knowledge node now cites the right source, no `ContentFiltered`. Never "the answer looks better." |
| **Backlog** | Suspected Findings surfaced (named) but not yet worked — fixed one at a time so re-test attribution is never lost. |
| **Reconstruction** | Parsing the Artifact into the AgentSpec model; unparseable/absent fields → marked **`unknown`** (lowers confidence). |
| **Revised artifact** | Reconstructed spec + accumulated Changes, rendered back to the surface. |

### The five diagnostic layers and what each layer owns

The five diagnostic layers map onto Microsoft's own pipeline — orchestrator/planner → knowledge → tools/actions, wrapped by content moderation, steered by instructions. The isolation order is fixed: **Moderation → Action → Orchestration → Grounding → Instructions.**

| Layer | Owns | How it *looks* (canonical symptom) |
|---|---|---|
| **Moderation** | Responsible-AI (RAI) content filtering on input **and** output | Response blocked/blank; `ContentFiltered`; safety refusal on *benign* input |
| **Action** | Tool/plugin/flow **execution** — params, HTTP, timeout | Right tool chosen but errored, returned empty, timed out, or got missing/invalid params |
| **Orchestration** | **Selection & sequencing** — which topic/tool/knowledge/agent, in what order (routing) | Wrong tool/topic picked; right one never invoked; multi-intent dropped; wrong order |
| **Grounding** | Retrieval — did the right evidence come back | Wrong/missing/stale facts; hallucination; "I don't know" when a source exists; no/wrong citation |
| **Instructions** | Behavior shaping once data is in hand — rules, tone, format, step order, when to call tools | Correct data present but **shaped wrong**: rule ignored, wrong tone/verbosity/format, step skipped/reordered, tool over- or under-called |

**Design principle — Instructions is the residual, diagnosed last.** The four lower layers (Moderation, Action, Orchestration, Grounding) emit objective machine signals; Instructions has none. Instructions is the default explanation only when Moderation, Action, Orchestration, and Grounding all read green but behavior is still wrong.

### The reconstruction rule and the AgentSpec zones a root cause names

Reconstruction parses the Artifact into the AgentSpec model. Reconstruct the *whole* Artifact into the same AgentSpec model the build flow uses (so you can render a full revised artifact), but **zoom** the diagnosis onto the suspected layer's zone. A partial or malformed paste → parse what's there, mark gaps `unknown`, and let that lower the confidence.

The AgentSpec zones a root cause names: `# ROLE` / `# OBJECTIVE` / `# SCOPE & GROUNDING` / `# RESPONSE RULES` / `# OUTPUT FORMAT` / `# CAPABILITIES & KNOWLEDGE` / `# WORKFLOW` / `# GUARDRAILS & FALLBACK` / `# SELF-CHECK`, plus config `knowledge[]` / `actions[]` and surface settings **orchestration mode**, **Allow ungrounded responses**, **moderation level**, **tenant-graph grounding**, and **web search scope** (see the AgentSpec skeleton reference).

---

## Evidence and capture playbooks per surface

The isolation procedure is only as good as the evidence read into it, and the two surfaces expose sharply different instrumentation. **Core asymmetry:** Copilot Studio (CS) gives a deep, exportable observability stack (live activity trace, historical Activity page, Analytics, transcript CSV, automated evaluation). M365 declarative agents (DAs) give a thin, ephemeral, largely un-exportable surface (live preview, a per-turn debug card, effectively no analytics or transcript export). Tell the maker exactly which artifact to grab, and grab it **while the bug is on screen** for declarative — it disappears per turn.

### Copilot Studio evidence artifacts (the rich surface)

Copilot Studio is the rich surface: it exposes exportable observability artifacts. This table lists each evidence artifact, the signal it carries, its capture click-path, and its limit.

| Evidence artifact | Signal it carries | Capture click-path | Limit |
|---|---|---|---|
| **Activity-map node** (knowledge / tool) | Which source hit, the **actual search query** used, sources used vs. searched-but-unused, tool inputs/outputs, status, latency | Test → **… → Show activity map when testing** → click a node | Generative orchestration **only**; in-topic generative steps hidden; not directly exportable |
| **Rationale** | AI explanation of *why* a tool/params were chosen | Node → **Show rationale** | AI-generated, **may be inaccurate** |
| **Chain of Thought (CoT)** | Intermediate reasoning steps | Test pane / map → **Reasoning** chevron | GPT-5 Reasoning, Claude Sonnet/Opus **only** |
| **Snapshot `dialog.json`** | **Detailed error descriptions** + conversational diagnostics | **… → Save snapshot** → `botContent.zip` | May contain sensitive data |
| **Session transcript CSV** | Outcome, reason, turns, transcript, topic, channel, CSAT, comments | Analytics → **Download Sessions** → row | **512-char/response cap**; **SharePoint answers `REDACTED`**; **not written for M365 Copilot agents** |
| **Conversation outcomes** | Resolved/Escalated/Abandoned + escalation reason — **System *unintended*** = users stuck | Analytics → Effectiveness → outcomes → Download CSV | Aggregate; session drill needs **Bot Transcript Viewer** |
| **Answer quality / Knowledge & Tool use** | Grounding quality, per-source **error rate**, per-tool **success rate** | Analytics → Use section | AI-sampled, not exhaustive |
| **Evaluation result CSV** | Pass/fail per method incl. **Tool use** & groundedness, expected vs. actual, activity map, resources used | **Evaluate** icon → test set → run → Export CSV | **[PREVIEW]**; 100 cases/set; results 89 days |

> **The activity-map knowledge node is the single highest-signal artifact:** it separates *grounding* (nothing came back / wrong source) from *instructions* (right source, wrong summary) in one glance, because it shows both the sources referenced **and** other sources it "searched but found nothing relevant." **Caveat:** "why fallback fired" is *not* a first-class field — infer it from a knowledge node with all sources searched-but-unused, or a "no tool selected" plan, plus the Rationale. The **test pane is design-time only** — timer/inactivity/background triggers may not fire; validate those in a published channel (Teams). Analytics does **not** count test-pane activity.

### M365 declarative Developer Mode card (the thin surface)

M365 declarative agents are the thin surface: the **Developer Mode `-developer on` card** is the one real trace. In Microsoft 365 Copilot Chat, select the agent, type **`-developer on`**, resend the prompt. A debug card returns **only when the orchestrator actually searched your knowledge / capabilities / actions.**

Card fields:

- **Agent metadata** — Agent ID, version, Conversation ID, Request ID (paste these when flagging).
- **Capabilities** — configured scope; note "WebSearch enabled" reflects the *manifest*, not the admin web-search policy.
- **Actions** — **Matched functions** (semantically matched in the app-index lookup) vs. **Selected functions for execution** (chosen by orchestrator reasoning).
- **Execution details** — executed capabilities (search text, response, #results) and executed actions (status, **latency**, request endpoint/method/headers, response).

### M365 declarative Developer Mode card decode table (these ARE the branch conditions)

This decode table interprets the Developer Mode card state; each row is a branch condition in the five-layer isolation search.

| Card state | Means | Points to |
|---|---|---|
| **No debug card** | Orchestrator didn't need your data/skills → answered from general model knowledge (**or** capacity throttling → try-again error) | Grounding never engaged |
| **No matched functions** | Prompt didn't semantically hit the action name/description | Orchestration / description |
| **No functions selected for execution** | Same root cause; or, if it *used* to work → throttling | Orchestration / description |
| **Empty/failed function execution details** | Parameter-binding failure — unclear action/param descriptions, invalid host URL, or broken OpenAPI. **Plugin API timeout = 10 s** | Action |

### M365 declarative: Agents Toolkit, Agent Builder, and what the surface does NOT give

**Agents Toolkit (pro-code):** Preview (F5) in VS Code → `-developer on` renders in a **Debug panel**, and adds a downloadable per-capability **diagnostic `.txt` log** — the *only* real file a declarative-agent maker can attach. In **Agent Builder** itself there is no card — type **`/debug`** in the preview chat (a copy-out blob for support) and grab Help → **Get support** IDs.

**What declarative simply does NOT give:** no activity map / plan trace, no Analytics page, no conversation-outcome/CSAT dashboards, no downloadable session transcripts (the CSV explicitly excludes M365 Copilot agents), no automated evaluation harness in Agent Builder. Set the maker's expectations: the Developer Mode card (or Toolkit `.txt`) *is* the evidence.

**Universal runtime tell (declarative):** the generic **"Sorry, I wasn't able to respond."** almost always means a **silent grounding failure** (license/auth/permission) — run the Entitlement pre-check first.

---

## The Entitlement pre-check (runs BEFORE the five-layer isolation search)

The Entitlement pre-check runs before the five-layer isolation search. Silent license / permission / auth gaps **masquerade as Grounding or Instructions problems** and are a top declarative root cause — so rule them out *first*, before touching the five-layer search. If a gap is the likely cause, that **is** the Finding (fix access); don't rewrite instructions for a permissions gap.

| Gap (all **silent** — no error) | Why it fails | Fix |
|---|---|---|
| **No Copilot license** | SharePoint/OneDrive grounding **requires an active Copilot license**. Without it (e.g. CDX demo tenants) the agent provisions fine but grounded retrieval **fails silently** → generic "Sorry, I wasn't able to respond." | Assign a Copilot license, or a **Microsoft 365 Copilot Developer License** for test tenants |
| **Wrong auth / missing permission** | SharePoint grounding needs **User authentication** (service principals unsupported); the signed-in user must have **≥Read** on the site; the URL in `items_by_url` must be reachable | Switch connection to User auth; confirm the user's Read access; verify the URL |
| **Action auth/consent not granted** | Authenticated custom actions fail without consent/roles | Grant roles/consent; recreate the connection |
| **Source not in-tenant / unsupported** | Embedded files aren't in GCC; **authenticated custom actions, usage-billing extensibility, and Agents-Toolkit publishing are unsupported in M365 Government** — a whole class of "action doesn't work" that is tenant-type, not config | Confirm tenant type and feature support |
| **Data defect** | A **SharePoint file with null characters in its filename returns no results** | Rename the file |

Ask the maker plainly: *is the source shared with the agent, and can the affected user open it themselves?* If yes, and it answers *some* questions fine → not a permissions gap → proceed to the five-layer isolation search.

---

## The five-layer isolation algorithm (Moderation → Action → Orchestration → Grounding → Instructions)

The five-layer isolation algorithm reads the evidence **from the outside of the pipeline inward** — most objective machine signals first, Instructions last. Each question has one discriminating check; a "yes" terminates at a layer, a "no" advances. **Do not change anything until the search terminates.** Because agent behavior is probabilistic, re-run each check 2–3× and judge on the majority.

```
Q0  REPRODUCE + CAPTURE — re-run the exact failing prompt 2–3×.
      M365 → -developer on card (or Toolkit F5 Debug panel + .txt log)
      CS   → activity map (+ Rationale/CoT) and/or Save snapshot → dialog.json
    Intermittent? Note it — probabilistic; on CS suspect throttling / model variance.

Q1  BLOCKED?  Filtered/blank, or a generic safety refusal on BENIGN input?
      CS: "content filtered due to Responsible AI" / ContentFiltered (App Insights KQL / transcript)
      M365: inherited M365 RAI refusal (no maker knob)
    → YES ....................................... MODERATION      ▸ stop
    → NO → Q2

Q2  EXECUTION ERROR?  A component was SELECTED but errored / returned empty /
                      timed out / got missing-or-invalid params?
      M365: empty or failed function execution details; latency near/over 10 s
      CS:   action node red / highlighted invalid params; dialog.json error; status = Failed
    → YES ....................................... ACTION          ▸ stop
    → NO → Q3

Q3  SELECTION CORRECT?  Right tool/topic/knowledge picked, in the right order? (routing)
      M365: "No matched functions" / "No functions selected" / wrong function selected
      CS:   plan shows wrong/missing node; Rationale explains a wrong choice; multi-intent half-planned
    → WRONG / MISSING ........................... ORCHESTRATION   ▸ stop
    → RIGHT COMPONENT RAN → Q4

Q4  EVIDENCE CORRECT?  Did retrieval return the right facts?
      M365: no debug card at all (general model knowledge); executed-capability 0 / irrelevant results
      CS:   knowledge node — empty results, wrong search phrase, or right source under "searched but didn't use"
      → run the GROUNDING PROBE to confirm.
    → MISSING / WRONG / UNCITED ................. GROUNDING       ▸ stop
    → RIGHT DATA CAME BACK → Q5

Q5  DATA RIGHT, BEHAVIOR WRONG?  Correct facts/tools in hand, but rule ignored,
    wrong tone/verbosity/format, step skipped/reordered, tool over-/under-called?
    → YES (residual) ........................... INSTRUCTIONS    ▸ stop
```

**Why this order.** Moderation and Action are terminal, unambiguous machine states — a block or an execution error fully explains the turn, so they gate first. Orchestration (selection) precedes Grounding (retrieval) because a retrieval result is only meaningful once you know the *right* source was even chosen. Two traps: (a) "it hallucinated" is usually **Grounding** (nothing retrieved) but can be **Instructions** (Allow-ungrounded ON telling it to fill gaps) — Q4's probe disambiguates; (b) "it ignored my rule" is usually **Instructions** but can be **Moderation** silently overriding — Q1 gates that.

### Confirm-before-change probes (still diagnostics, not fixes)

These probes confirm a suspected layer before any config edit. They are still diagnostics, not fixes.

- **Grounding probe — Allow-ungrounded responses OFF (Copilot Studio).** OFF forces the agent to answer *only* from a tool/knowledge call; any ungrounded turn falls back instead. If the failing answer **turns into a fallback with OFF**, retrieval genuinely isn't returning the facts → **Grounding confirmed**. If it still answers correctly, grounding was fine. Caveat: OFF also disables follow-up/clarifying questions and doesn't *guarantee* zero general-knowledge blending.
- **With / without knowledge (both surfaces).** Remove or add the source and re-ask. Invents the answer without it but gets it right once added → grounding works; over-uses a source it shouldn't → scope/instruction problem.
- **Base-Copilot A/B (declarative).** Declarative has no strict-grounding toggle, so ask *base* M365 Copilot the same prompt: if the agent adds no value / behaves identically, the added knowledge isn't being used → grounding/orchestration.
- **Moderation notch probe (Copilot Studio).** Drop moderation one step (Lowest→Highest, default **High**, per agent/topic/prompt) and re-ask the benign prompt. Unblocks → **Moderation confirmed**.

### The minimal-change → re-test loop (keyed to verify-signals)

The minimal-change → re-test loop applies exactly one Change per cycle and confirms it by a verify-signal.

1. **One change, one hypothesis.** Change exactly one thing — one instruction line, one tool/topic **description**, one param, one moderation notch. Never stack edits; you lose attribution.
2. **Re-run the identical prompt** 2–3× (probabilistic).
3. **Re-read the *same* evidence** and confirm the **verify-signal flipped**, not just the visible answer — function now **Selected**, knowledge node now cites the right **source**, action params now valid, no `ContentFiltered`.
4. **Revert if flat.** A change with no measurable signal change is noise — undo before the next hypothesis.
5. **Regression-check** the conversation starters + a couple of adjacent prompts.

### Minimal fix lever and verify-signal per isolated layer

Once a layer is isolated, this table gives the minimal fix lever and the objective signal to confirm it on each surface.

| Isolated layer | Minimal fix lever | Confirm on (M365) | Confirm on (Copilot Studio) |
|---|---|---|---|
| **Instructions** | Tighten one rule; say what to *do*; make the step atomic; post-model-upgrade step reordering → **literal-execution header** | `-developer on` card + test chat | Test-pane fired-node trace; re-ask |
| **Grounding** | Scope/refresh the source; fix permissions; narrow to folder/site; add "use `Source` for X" hint | executed-capability (search text, #results); base-Copilot A/B | knowledge node (referenced vs. unused); **Allow-ungrounded OFF** probe |
| **Orchestration** | Fix the **name** first (weighs most), then description; remove overlap; add one example utterance | Matched / Selected functions | activity-map plan + **Rationale** + **CoT** |
| **Moderation** | Drop moderation one notch; state the behavior is expected in instructions | (inherited M365 RAI — no maker knob) | re-ask; App Insights KQL `ContentFiltered`; transcript |
| **Action** | Fix param/description; validate host URL & OpenAPI; ensure < 10 s | execution details (status, latency, request/response) | activity-map action node params; `dialog.json` |

---

## Failure taxonomy (symptom → likely layer → root cause zone → fix)

The failure taxonomy maps a symptom to its likely layer, root-cause zone, and fix. Same symptom, **different likely layer per surface** — this is the surface-asymmetry insight. **Declarative skews Instructions / Knowledge / Licensing** (thin instrumentation, silent failures, hard ceilings); **Copilot Studio exposes error codes + activity map** (settings-level fixes are available).

| # | Symptom | Likely layer | Root cause (AgentSpec zone) |
|---|---|---|---|
| 1 | Over-declines / refuses valid queries | Instructions (+ Moderation/Grounding) | `# SCOPE & GROUNDING` too narrow; **Allow-ungrounded OFF**; moderation too High; over-restrictive `# GUARDRAILS` |
| 2 | Hallucinates / ungrounded answers | Grounding | `Allow ungrounded` posture; missing `knowledge` source; no "don't invent" rule; citation-tampering in instructions |
| 3 | Ignores / under-uses knowledge | Grounding / **Entitlement** | **Licensing/auth/permission** (silent); source unreferenced in instructions; too many sources dilute selection |
| 4 | Retrieves the *wrong* knowledge | Grounding / Orchestration | Overlapping sources / weak descriptions; `# SCOPE & GROUNDING` too broad; low retrieval precision |
| 5 | Wrong / failed / skipped tool call | Action / Orchestration | Weak `actions` metadata; tool not agent-level / "decide dynamically" off; too many tools; schema/auth defect |
| 6 | Generative orchestration loops / stalls | Orchestration | Topic never reaches a terminal node; re-asks filled slots; too many consecutive actions; over-complex instructions |
| 7 | Moderation over-blocks / fallback fires too often | Moderation | Moderation too High; knowledge looks like an injection (`OpenAIndirectAttack`); misrouted fallback |
| 8 | Tone / format / output drift | Instructions | Missing output contract; **model auto-upgrade** drift (GPT 5.0→5.1); non-atomic tasks |
| 9 | Instructions ignored near the end | Instructions (declarative) | Body over the **8,000-char** hard limit; logic that belongs in topics/flows |
| 10 | Latency / Copilot-Credit blowout | Action / orchestration | Synchronous flow overhead; metered features; generative-everywhere; overage |
| 11 | Hits a wall no tuning fixes | *whole surface* | Declarative ceiling — can't loop, act autonomously, strictly ground, or reach external channels |

### Failure taxonomy — the fix per symptom

This table gives the fix for each numbered symptom in the failure taxonomy above.

| # | Symptom | Fix |
|---|---|---|
| 1 | Over-declines / refuses valid queries | Broaden/enumerate in-scope topics; add a Valid few-shot; re-enable ungrounded/follow-ups if grounding was forced off; lower moderation a notch |
| 2 | Hallucinates / ungrounded answers | Set **Allow-ungrounded OFF** (Studio); add/scope the authoritative source; add an uncertainty rule; remove citation-shaping language |
| 3 | Ignores / under-uses knowledge | Fix license/auth/permission first (Entitlement pre-check); name the source in `# CAPABILITIES & KNOWLEDGE`; prune to needed sources |
| 4 | Retrieves the *wrong* knowledge | Distinct source name+description; scope to folders/sites/channels; enable **tenant-graph semantic search** (Studio) |
| 5 | Wrong / failed / skipped tool call | Sharpen name+description; add at agent level + enable dynamic use; cut tool count; fix OpenAPI/auth; **read the error code** |
| 6 | Generative orchestration loops / stalls | Ensure topics end (link to **Escalate**); bind captured values to inputs; cap chain <15; **bisect** instructions |
| 7 | Moderation over-blocks / fallback fires too often | Lower moderation (agent/topic); clean injection-looking knowledge; edit the **Fallback system topic**, *not* instructions |
| 8 | Tone / format / output drift | Add explicit tone/verbosity/format contract to `# OUTPUT FORMAT`; add **literal-execution header** after upgrades; split tasks atomic |
| 9 | Instructions ignored near the end | Consolidate/Simplify/Prioritize; never offload to knowledge (XPIA); re-platform if logic needs it |
| 10 | Latency / Copilot-Credit blowout | HTTP node instead of flow; cache in variables; avoid tenant-graph/premium tools on hot paths; classic orchestration; cap spend |
| 11 | Hits a wall no tuning fixes | **Surface-flip escalation** — re-platform, not a field edit |

---

## Copilot Studio error-code → zone decoder

The Copilot Studio error-code decoder maps a code (read in the test pane / topic checker) straight to the layer and its fix. XPIA = cross-prompt injection attack; RAI = Responsible AI.

### Error codes pointing to Moderation

Moderation error codes indicate the RAI content filter tripped (all surface as `ContentFiltered`).

| Code(s) | Zone / meaning | Fix |
|---|---|---|
| `OpenAIHate` · `OpenAIJailBreak` · `OpenAIndirectAttack` · `OpenAISelfHarm` · `OpenAISexual` · `OpenAIViolence` (all `ContentFiltered`) | **Moderation** — RAI content filter tripped | Lower moderation a notch; state expected behavior; clean injection-looking knowledge |

### Error codes pointing to Action

Action error codes indicate a tool/plugin/flow execution failure — malformed requests, auth, permission, throttling, timeouts, oversized output, or flow-binding faults.

| Code(s) | Zone / meaning | Fix |
|---|---|---|
| `HTTP400BadRequest` / `HTTP422` | **Action** — malformed/invalid request | Validate params/types before the call |
| `HTTP401` / `InvalidAuthenticationToken` / `MsalUiException` | **Action** — missing/expired/interactive-auth token | Reauthenticate; recreate connection |
| `HTTP403Forbidden` | **Action** — authenticated but lacks permission | Grant roles/consent; check delegation |
| `HTTP404NotFound` | **Action** — bad resource id/URL | Prefer dynamic resource selection over typed IDs |
| `HTTP429TooManyRequests` / `QuotaExceeded` | **Action** — throttling / quota | Backoff + retry; reduce volume; upgrade quota |
| `HTTP5xx` / `ExecutionTimeout` / `OperationTimeout` / `HTTP408/504` | **Action** — service-side / timeout | Retry with backoff; narrow/paginate |
| `FlowActionTimedOut` (>100 s) · `FlowActionBadRequest` / `FlowActionException` / `BindingKeyNotFoundError` · `FlowMakerConnectionBlocked` | **Action** — agent-flow timeout / input-output mismatch / blocked maker creds | Optimize flow; only Text/Boolean/Number params; **remove & re-add the flow** to refresh bindings; share flow run-only |
| `AsyncResponsePayloadTooLarge` / `TooMuchDataToHandle` | **Action** — tool output too big for context | Scope output to needed fields; use connector filters |

### Error codes pointing to Grounding

Grounding error codes indicate a knowledge-retrieval error from a backing source.

| Code(s) | Zone / meaning | Fix |
|---|---|---|
| `SharePointSearchFailed` · `SharePoint429/500/503` · `DataverseSearchFailed` · `Dataverse...401/429/500/503` · `FoundryIQSearchFailed` · `BingSearchFailed` | **Grounding** — knowledge retrieval error | 401 = reauth/permission; 429 = throttling (backoff); 5xx = service-side (retry) |

### Error codes pointing to Orchestration

Orchestration error codes indicate a sub-agent selection/sequencing fault or a cycle/turn-cap breach.

| Code(s) | Zone / meaning | Fix |
|---|---|---|
| `ConnectedAgent*` | **Orchestration** — sub-agent not found/not published/auth mismatch/**chaining unsupported** | Publish sub-agent; match auth; flatten (no multi-level chaining) |
| `InfiniteLoopInBotContent` · classic `2000` / `2021` (>50 dialogs/turn) / `2022` (>30 messages/turn) | **Orchestration** — cycle / turn cap | Ensure topics end correctly; link to Escalate; cap chain length |

### Error codes pointing to cost/quota

Cost/quota error codes indicate a generative/orchestration rate limit or overage.

| Code(s) | Zone / meaning | Fix |
|---|---|---|
| `GenAIToolPlannerRateLimitReached` · `GenAISearchandSummarizeRateLimitReached` · `OpenAIRateLimitReached` · `EnforcementMessageC2` | **cost/quota** — generative/orchestration rate limit or overage | Retry; add capacity packs / PAYG; reduce tool calls |

---

## Improvement levers (goal-first "improve" mode)

Improvement levers apply when the agent *works* but could be *better*. Frame each lever as **goal the maker states → lever → AgentSpec zone → verify**. The governing contract is **`change X → rerun Y → expect Z`**: no lever is applied without a test proving it moved the number.

### The eval loop gates every improvement lever

The eval loop gates everything: no lever is applied without a test set proving the change moved the number.

- **Build a small test set first, then grow it.** A test set = test cases; a test case = prompt + optional expected response (assertion) + acceptance criteria + grader. Stage 1: one prompt per key scenario (both "should answer" and "should refuse/route"). Stage 3 expands across **Foundational core · Robustness · Architecture · Edge cases**. Outputs are probabilistic — **run each set multiple times and average.**
- **Targets / readiness gates:** **Safety & compliance < 95 % = BLOCK** (triage safety first); **Core business < 80 % = iterate**; all above threshold = deploy. **Aim for an 80–90 % pass rate** on quality.
- **Category signal → which lever:** Core fail = something broke (check recent changes); **Robustness fail = too strict**; Architecture fail = a component/workflow bug; Edge-case fail = guardrails need strengthening.
- **Fix by pattern, not one-by-one:** with >15 failures, start with the lowest-scoring set; if ≥80 % share a root cause, one fix clears many. Scores flat after a fix → wrong root cause, re-triage. One score up + another down → **instruction conflict**.
- **Surface caveat:** M365 declarative has **no built-in Evaluate tab** — the loop there is the manual **Create → Publish (RAI) → Test → Iterate** cycle, run by hand in Copilot/Teams.

### The lever catalog (goal → lever → zone → verify)

The lever catalog maps a goal the maker states to its improvement lever, the AgentSpec zone it edits, and how to verify it.

| Goal the maker states | Lever | AgentSpec zone | Verify |
|---|---|---|---|
| "Is it good enough / push the number up" | Small test set → baseline → expand → rerun-avg | *(meta)* attach `change X→rerun Y→expect Z` to every edit | Pass 80–90 %; safety ≥95 % |
| "Answers from the wrong doc" | Curate/rescope corpus; align source vocab to how users ask; tighten descriptions | prune `knowledge[]`; `# SCOPE & GROUNDING` "use `<section>` of `<source>`" | Rerun grounding set |
| "Makes things up / uses general knowledge" | Strict grounding | **Allow ungrounded = OFF** + `# SCOPE & GROUNDING` "only answer from sources" (Studio; declarative can't hard-block) | Rerun grounding set |
| "Pulls stale / open-web noise" | Scope web search | Web Search off, or add specific site URLs to `knowledge[]` | Rerun freshness cases |
| "SharePoint retrieval imprecise" | Tenant-graph semantic search (cost/latency trade) | enable tenant-graph grounding (**+10 credits/msg**, small latency) | Rerun; watch latency |
| "Too long / wrong tone / inconsistent" | Output contract + tone/verbosity spec | `# OUTPUT FORMAT` contract; consolidate tone into one block | Rerun response-quality set |
| "Over-eager / wrong tool" | Gate tool use; sharpen tool descriptions + negative examples | `# RESPONSE RULES` gate; `actions[]` description edits | Rerun tool-invocation set |
| "Prompt maxed at 8k / edits regress others" | **Instruction-budget hygiene** | Consolidate / Prioritize (first+last) / Simplify / **Externalize** static reference lists to `knowledge[]` | **Full-suite** rerun |
| "Regressed after a model upgrade" | Literal-execution header → structural audit | prepend stabilizing header; then rewrite riskiest step | Rerun full suite |
| "Too expensive / slow" | Downgrade answer type; avoid tenant-graph/reasoning by default; cap spend; cheaper surface/orchestration | classic answers/topics; minimal-reasoning `# RESPONSE RULES`; per-agent cap; orchestration/surface flip | Estimator + rerun |

### The 8,000-character instruction-budget trap

The 8,000-character instruction-budget trap is the sharpest improve-mode insight: remediation *adds* instructions, and the prompt has finite capacity. Symptoms of **overload** (not missing guidance): previously-passing cases fail after unrelated edits; some rules followed, others ignored; a fix for one scenario regresses another; **a new, clear instruction has no effect.** The only legitimate moves on a maxed-out prompt are **Consolidate / Prioritize / Simplify / Externalize** — never offload governing instructions into a knowledge doc (untrusted, XPIA-sanitized, not honored as system instructions).

### Cost levers (Copilot Studio)

Cost levers (Copilot Studio) address a Copilot-Credit blowout. Billing is per event: classic answer **1** · generative **2** · agent action **5** · tenant-graph grounding **10** · agent-flow **13/100 actions** · AI tools basic/standard/premium **1/15/100** per 10 responses; reasoning models add a premium token meter *on top*. M365-Copilot-licensed users incur **no charge** for core B2E usage — **unlicensed users and metered features are what generate the bill.** Downgrade answer type where possible (5× spread classic→action), turn off tenant-graph where standard grounding suffices, and cap per-agent monthly spend in PPAC before the **125%-of-prepaid overage** disables the agent.

---

## Surface-flip escalation (re-platform declarative to Copilot Studio)

Surface-flip escalation applies when a Finding can't be fixed with a field edit — the agent has hit the **declarative surface ceiling**. This is a **meta-symptom**: several taxonomy rows (#2 hallucination ceiling, #5 multi-tool truncation, #6 "can't loop," #9 truncation) are the ceiling manifesting. The fix is **re-platforming to Copilot Studio**, presented as a distinct **escalation**, not an in-place Change — a migration has no single verify-signal.

| Trigger observed | Declarative limit hit | Re-platform because |
|---|---|---|
| Needs iterative / looped / multi-step orchestration | Sequential pipeline, no loops ("not suitable for complex multistep operations") | Copilot Studio generative orchestration chains topics/tools/agents |
| Needs autonomous / event-triggered / proactive behavior | Declarative is **user-initiated only** | Studio event triggers + generative orchestration |
| Needs **strict grounding** (block general knowledge) | Agent Builder can't fully block model knowledge | Studio **Allow-ungrounded OFF** |
| Needs deterministic automation | Only single-step API plugins | Studio **agent flows** |
| Needs multi-agent / external channels / group use | Declarative is individual, M365 channels only | Studio A2A/connected agents + web/WhatsApp/Slack/SMS/voice |
| Instruction logic exceeds 8,000 chars | Hard cap | Logic moves to topics/flows/triggers |

**Diagnostic tell:** the agent does *part* of a multi-step task then stops, or invents answers only strict grounding would prevent, and the scenario matches a re-platform trigger. **How the flow presents it:** name the ceiling ("declarative can't do this, here's why"), then **carry the reconstructed AgentSpec into the *build* flow on Copilot Studio** — no re-interview, since the spec is surface-agnostic. Copilot Studio is the superset surface (it can even emit a declarative agent), so the framing is "does the scenario need capabilities only the custom-engine runtime provides." Note any **Copilot-Credit** implication before the maker commits (the flip changes metering).

---

## Sources

- Understand error codes (Copilot Studio) — https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes
- Resolve responsible AI content filter errors — https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai
- Known issues in M365 Copilot extensibility — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues
- Test and debug agents using Developer Mode — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-copilot-studio
- Test and debug agents in Agents Toolkit — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-vscode
- Review agent activity (activity map, Rationale, Chain of Thought) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-review-activity
- Test your agent (test pane, snapshot / dialog.json) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot
- Analytics overview — https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
- Download session transcripts — https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-transcripts-studio
- Agent evaluation (overview) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview
- Knowledge sources overview (Allow ungrounded, tenant-graph, moderation) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- Write effective instructions for declarative agents (8k limit, literal-execution header, budget hygiene) — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions
- Orchestrate agent behavior with generative AI — https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions
- Review the agent evaluation checklist — https://learn.microsoft.com/en-us/agents/agent-evaluation/evaluation-checklist
- Evaluation-driven triage & remediation (overview / remediation / quick reference) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-overview
- Billing rates and management (Copilot Credits) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management
- Apply generative orchestration capabilities (names/descriptions, testing & tuning) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration
