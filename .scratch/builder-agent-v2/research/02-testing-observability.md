# 02 · Native testing / analytics / observability

_Research findings — grounded in current Microsoft Learn documentation (fetched 2026-07-14). Cited doc `ms.date` values range Nov 2025 – Jul 2026. Preview-only and recently-changed features are flagged inline with **[PREVIEW]** / **[NEW]**._

> **Core asymmetry to hold onto.** Copilot Studio gives a maker a *deep, exportable* observability stack: a live activity/orchestration trace, a full historical Activity page, an Analytics dashboard, downloadable CSV transcripts, and an automated evaluation harness. M365 **declarative agents** give a maker a *thin, ephemeral, mostly un-exportable* surface: a live preview chat, a per-turn debug card (Developer Mode), and effectively **no** maker-facing analytics or transcript export. The diagnostic tool must set expectations accordingly and tell the maker exactly which artifact to grab.

---

## Part A — Copilot Studio (the rich surface)

### A.1 The "Test your agent" pane
Design-time chat panel. Open with **Test** at the top of any page. ([authoring-test-bot](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot))

- Selecting an agent response **jumps to the topic node** that produced it; fired nodes get a colored checkmark + bottom border (classic-topic tracing).
- **Track between topics** (… menu) follows the conversation across topics automatically.
- **Variables** panel → **Test** tab shows live variable values during the conversation (global/environment/system/custom).
- **Reset** clears conversation; **Manage connections** manages the user-auth connections used in test.
- **Important limit:** the test pane is design-time only and **doesn't replicate all published-channel behavior** — timer/inactivity/background triggers may not fire. For those, publish and test in a real channel (e.g., Teams). Analytics does **not** count test-pane activity.

### A.2 The activity map / orchestration trace — the highest-signal artifact
The activity map is the visual orchestration trace. **Only available for agents with generative orchestration enabled.** ([authoring-review-activity](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-review-activity))

**Real-time (during test):** … menu → **Show activity map when testing**. Shows the plan the orchestrator generated, per-step latency, and highlights errors (missing/invalid action input/output params). You can inspect each node's inputs and outputs.

**What each node type reveals (this is the diagnostic gold):**
- **Knowledge node** — the *actual search query* the agent used (can differ from the user's wording or a trigger payload), the response built from sources, **the sources it referenced**, AND **other sources it searched but did NOT use** ("searched but found nothing relevant"). → Directly answers "which knowledge source was hit / why wasn't mine used."
- **Tool / action node** — the tool selected, its **inputs and outputs**, execution status, and latency. → Directly answers "was a tool called, with what parameters, and did it succeed."
- **Rationale** — select **Show rationale** on a Completed knowledge source or connector node to get an AI-generated explanation of *why* the agent chose that tool / filled those parameters. On-demand, based on agent metadata + activity. **Caveat: AI-generated, may be inaccurate.**
- **Chain of Thought (CoT)** — reasoning steps shown before the response in the test pane, and under the **Reasoning** chevron in Map view for historical activities. **Only for selected models: GPT-5 Reasoning, Claude Sonnet, Claude Opus.** ([authoring-review-activity](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-review-activity))

**Gaps to warn the maker about:**
- Activity map is **generative-orchestration only** — classic-mode agents get topic-node tracing in the test pane but no plan map.
- **Generative orchestration activities *within a topic* don't appear** in the map.
- **"Why fallback fired" is not a first-class field** — it's inferred: a knowledge node showing all sources searched-but-unused, or a "no tool selected" plan, plus the Rationale, is how a maker reconstructs why the agent fell back to a generic/ungrounded answer.

### A.3 Historical Activity page — post-hoc trace with transcript
Every activity (including test-pane runs, and Teams/M365 Copilot/SharePoint published channels, and autonomous-trigger runs) is recorded on the **Activity** page. ([authoring-review-activity](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-review-activity))

- **Requires a Microsoft Exchange license + inbox** — historical activity data is stored via M365 services in the maker's Exchange mailbox location. Admins can turn this off in PPAC.
- Only the maker's **own** interactions appear, and the agent must use **Authenticate with Microsoft**.
- List columns: Name (or *Automated*), Channel, Date, Completed steps, Last step, **Status** (Submitted / In progress / Input required / Auth required / Complete / Canceled / **Failed** / Rejected). Filterable/sortable by date, channel, status, errors; filter pills for Failed / Blocked / In progress / Waiting for user / Completed.
- **Transcript + Map view** (default) shows user input, trigger payloads, and agent responses alongside the visual map. **Reasoning** chevron gives CoT (same model restriction).
- **Event-trigger testing:** the test chat surfaces the **trigger payload as a message** (visible only to the maker) — useful for verifying what an autonomous trigger actually delivered.

### A.4 Snapshot & "Flag an issue" — the literal copy-out artifacts
- **Save snapshot** (… menu) → `botContent.zip` containing:
  - `dialog.json` — **conversational diagnostics, including detailed error descriptions** (the paste-worthy artifact for a diagnostic tool).
  - `botContent.yml` — the agent's topics, entities, variables.
  - **Warning:** contains all agent content incl. possibly sensitive data.
- **Flag an issue** sends only the **conversation ID** to Microsoft (not the snapshot) — a support handle, not maker-readable evidence. ([authoring-test-bot](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot))

### A.5 Analytics dashboards — aggregate production behavior
**Analytics** on the top menu bar. Data retained **up to 360 days**; session details + transcripts **last 28 days**; download window **29 days**; UTC stamps; can lag up to ~1 hour. **Does NOT include test-pane activity.** Access can be shared read-only via **Analytics Viewer** role (+ **Bot Transcript Viewer** to see transcript content). ([analytics-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview), [analytics-improve-agent-effectiveness](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness))

Sections and the signal each carries:
- **Summary** — Copilot-generated AI insight summary (themes, engagement, sentiment trends). **Customer comments summary is [PREVIEW].**
- **Overview** — KPIs incl. active users (DAU/MAU; **requires authentication** to be enabled). **Savings** = time/cost.
- **Custom metrics** — up to **3** maker-defined natural-language metrics; drill to sessions (needs Bot Transcript Viewer) with the reasoning + underlying transcript.
- **Effectiveness:**
  - **Conversation outcomes** — Resolved / Escalated / Abandoned / Unengaged, with sub-reasons. **Escalation reasons: System intended** (business-rule threshold, expected), **System unintended** (user stuck / repeated failures — the one to investigate), **User requested**. Resolved = Confirmed vs Implied. **Download CSV** from the chart's menu. → The primary "where does it break down / why does it escalate" signal.
  - **Reactions** — thumbs up/down counts + comments (comments need Bot Transcript Viewer). *Not supported on the M365 Copilot channel.*
  - **Customer satisfaction (CSAT)** — score /5 from end-of-session surveys (1–2 Dissatisfied, 3 Neutral, 4–5 Satisfied); satisfaction-by-session breakdown, drill to sessions.
  - **Sentiment [PREVIEW]** — AI sentiment over a sample; % of sessions with negative sentiment. Toggle in Settings → Advanced.
  - **Agents** — call volume / success rate / status for child & connected agents. → "which sub-agent is failing."
- **Use:**
  - **Themes** — AI clustering of user questions into categories. ([analytics-themes])
  - **Generated answer rate and quality** — answered vs unanswered rate; **Answer quality** (AI-sampled) labels answers **Good/Poor** on completeness, relevance, **groundedness**, with a reason per Poor answer; drill to the filtered question list. → "is the agent grounding, and why are answers poor."
  - **Tool use** — how often each tool is invoked and its **success rate** (top 5 charted). → "is my tool being called and is it erroring."
  - **Knowledge source use** — per-source usage frequency and **error rate**. → "is my knowledge source actually being used / returning errors."

**Topic usage analytics** (Topics page → topic → More … → Analytics) gives per-topic outcomes/CSAT — but **classic-mode only**. Generative agents must use conversation outcomes + themes instead.

### A.6 Downloadable transcripts (CSV) — the paste-friendly production evidence
Two paths: **Power Apps / Dataverse** (full) and **Copilot Studio app** (a subset, CSV). Requires **Bot Transcript Viewer** security role + transcript recording enabled (on by default in new environments). Analytics page → pick date range → **Download Sessions** → pick a row (1-day increments, ≤50,000 sessions each). ([analytics-transcripts-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-transcripts-studio))

CSV fields (high diagnostic value, and a maker can paste one row):
`SessionID`, `StartDateTime`, `SessionOutcome` (Resolved/Escalated/Abandoned/Unengaged), `OutcomeReason`, `IsResolvedImplied`, `Turns`, `ChatTranscript` ("User says…; Agent says…;"), `InitialUserMessage`, `TopicName`, `TopicId`, `ChannelId` (directline/msteams/facebook/conversationconductor…), `CSAT`, `Comments`.

**Sharp limits the diagnostic tool must know:**
- **512-char cap per bot response** in `ChatTranscript` (truncated).
- **SharePoint-grounded answers are `REDACTED`** — the transcript keeps the question + the `search_results` source content but **not the actual answer**. (Big blind spot for SharePoint-knowledge agents.)
- **Transcripts are NOT written for M365 Copilot agents**, Dataverse-for-Teams, or Dataverse developer environments.

### A.7 Agent evaluation (automated test sets) — repeatable QA harness
**[PREVIEW]** feature (labeled "Create test cases to evaluate your agent (preview)"). Launched via the **Evaluate** icon in the test chat, or the **Evaluation** page. ([analytics-agent-evaluation-intro](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-intro), [-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview), [-results](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-results))

- **Test set** = up to **100** test cases; each a single Q→A or a whole conversation, optionally with an expected answer. Generate from knowledge/topics (AI), import from spreadsheet, or hand-write. Can seed from Analytics themes. Can pick a **user profile [PREVIEW]** to simulate different users.
- **Test methods** (mix per set):
  - **General quality** (default, LLM) — scores /100 on Relevance, **Groundedness**, Completeness, Abstention; must meet all to be high quality. No expected answer needed.
  - **Compare meaning** — intent similarity vs expected (pass score, default 50).
  - **Tool use** — pass/fail on whether **expected tools/topics were used**. → programmatic "did it call the right tool."
  - **Keyword match**, **Text similarity** (cosine 0–1), **Exact match**, **Custom** (your own labels + pass/fail rubric, e.g. compliance).
- **Results:** live line-by-line; each case gets **Pass/Fail/Invalid/Error**; set gets a **Pass rate**. Per-case detail shows expected vs actual response, **the reasoning behind the result**, **the knowledge/topics/tools the agent used**, and a **Show activity map** button (same trace as A.2). **Compare with** diffs two runs (improved↔declined arrows). **Export test results → CSV** (question, expected, method, pass score, agent response, result, analysis). Results kept **89 days** in-product.
- Also runnable via **Power Platform REST API / connectors** for CI/CD. GCC limits: no user profile, no text-similarity. Doesn't support **Fabric data agents**. Measures correctness/performance, **not** safety/RAI.

---

## Part B — M365 declarative agents (the thin surface)

### B.1 Agent Builder live preview / test pane
Low-code authoring in microsoft365.com/chat, office.com/chat, or Teams (Work or Web; **not mobile**). The right pane is a **live preview chat** — test conversation starters and sample prompts frequently. ([agent-builder](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder))

- **No activity map, no orchestration trace, no analytics** in Agent Builder.
- **`/debug`** typed in the preview/Describe chat box surfaces support diagnostics — Microsoft documents it only as "type `/debug` and include the contents in your support ticket," i.e. it's a copy-out blob for support, not a documented maker-readable trace.
- Support identifiers a maker can copy (Help → **Get support**): agent ID, tenant ID, environment ID, session ID.
- **Grounding caveat carried from ticket 01:** Agent Builder can't fully block general model knowledge, and web-search UI toggle can be overridden by the admin web-search policy — behavior a maker sees in preview may not match what the tool expects.

### B.2 Developer Mode (`-developer on`) — the one real trace for declarative agents
In Microsoft 365 Copilot Chat, select the agent, then type **`-developer on`** (`-developer off` to disable). While on, a **debug info card** is returned **whenever the orchestrator searches your enterprise knowledge, capabilities, or actions**. ([debugging-agents-copilot-studio](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-copilot-studio))

Card fields (this is the maker's richest declarative-agent evidence):
- **Agent metadata** — Agent ID (title ID + manifest ID), Agent version, **Conversation ID**, **Request ID**.
- **Capabilities** — which are configured (note: "WebSearch enabled" reflects the manifest, **not** the admin web-search policy).
- **Actions** — action ID + version; **Matched functions** (semantically matched in the app-index lookup) vs **Selected functions for execution** (chosen by orchestrator reasoning).
- **Execution details** — executed **capabilities** (search text used, response, # results) and executed **actions** (function status, **latency, request endpoint/HTTP method/headers, and the response**).

**Diagnostic decode table the tool can apply directly:**
- *No debug card* → orchestrator didn't need your data/skills (or capacity throttling). → your knowledge/action wasn't even considered.
- *No matched functions* → prompt didn't semantically hit the action name/description. → fix action/function descriptions.
- *No functions selected for execution* → same root cause; or, if it used to work, **throttling**.
- *Empty/failed function execution details* → parameter-binding failure → unclear action/param descriptions, invalid host URL, or broken OpenAPI. Plugin API **timeout is 10s**.

**Limits:** ephemeral (per-turn card, no history, no export beyond copy/paste), individual, and there is no "why fallback" field — you infer it from "no card" / "no functions selected."

### B.3 Agents Toolkit (pro-code) — same trace, better packaging
For pro-code makers: **Preview your app (F5)** in Microsoft 365 Agents Toolkit (VS Code) launches the agent in browser Copilot Chat; `-developer on` works there too, and debug info renders in a **Debug panel**. ([debugging-agents-vscode](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-vscode))
- Adds a capability-level **Summary** and — notably — a **downloadable diagnostic log `.txt`** per capability (success/failure detail). This is the **only real file a declarative-agent maker can attach**, and it's pro-code only.
- Same matched-vs-selected function breakdown and execution/request detail as B.2.

### B.4 What declarative agents simply do NOT give a maker
- **No Copilot Studio Analytics page, no conversation outcomes / CSAT / escalation dashboards** for the agent as an artifact.
- **No downloadable session transcripts** — the transcript CSV explicitly excludes "Microsoft 365 Copilot agents." Tenant-/admin-level Copilot usage reporting exists (Copilot dashboard / Viva Insights, admin-scoped) but is **org analytics, not a maker's per-agent behavioral trace**, and is out of a maker's paste-reach.
- **No activity map / plan trace** (that's a generative-orchestration Copilot Studio feature).
- **No automated evaluation harness** in Agent Builder (agent evaluation is a Copilot Studio feature; a declarative agent authored *in Copilot Studio* could use it, but Agent Builder alone can't).

---

## Part C — Evidence-type → signal → capture → limit (the interpreter's cheat sheet)

| Surface | Evidence artifact | Signal it carries | Capture click-path | Key limit |
|---|---|---|---|---|
| CS test | **Activity map node** (knowledge/tool) | Which source hit, search query used, sources used vs searched-unused, tool inputs/outputs, latency | Test → … → Show activity map; click a node | Generative orch. only; in-topic gen steps hidden; not exportable directly |
| CS test | **Rationale** | AI explanation of *why* a tool/params chosen | Node → Show rationale | AI-generated, may be wrong |
| CS test | **Chain of Thought** | Reasoning steps | Test pane / Activity Map → Reasoning chevron | GPT-5 Reasoning, Claude Sonnet/Opus only |
| CS test | **Snapshot `dialog.json`** | Detailed error descriptions + diagnostics | … → Save snapshot → `botContent.zip` | May contain sensitive data |
| CS prod | **Session transcript CSV** | Outcome, reason, turns, transcript, topic, channel, CSAT, comments | Analytics → Download Sessions → row | 512-char/response cap; SharePoint answers REDACTED; not for M365 Copilot agents |
| CS prod | **Conversation outcomes** | Resolved/Escalated/Abandoned + escalation reason (esp. System **unintended**) | Analytics → Effectiveness → outcomes → Download CSV | Aggregate; sessions drill needs Bot Transcript Viewer |
| CS prod | **Answer quality / Knowledge & Tool use** | Grounding quality, per-source error rate, per-tool success rate | Analytics → Use section | AI-sampled, not exhaustive |
| CS eval | **Evaluation result CSV / test-case detail** | Pass/fail per method incl. **Tool use** & groundedness, expected vs actual, activity map, resources used | Evaluate → test set → run → Export CSV | **[PREVIEW]**; 100 cases/set; results 89 days |
| DA (Agent Builder) | **`/debug` blob**, support IDs | Support-ticket diagnostics; agent/session IDs | `/debug` in preview; Help → Get support | For support, not maker-readable trace |
| DA (Copilot Chat) | **Developer Mode card** | Matched vs selected functions, executed capability/action, request+response, latency, IDs | `-developer on` | Ephemeral per-turn; copy/paste only; no history/export |
| DA (Agents Toolkit) | **Capability diagnostic log `.txt`** | Per-capability success/failure detail | F5 preview → Debug panel → download log | Pro-code only |

---

## Part D — Preview / recently-changed flags (verify before relying)
- **Agent evaluation** — labeled **preview**; user profiles/connections sub-feature also preview; results retained 89 days; REST/connector automation available. ([analytics-agent-evaluation-intro])
- **Sentiment** analysis and **customer comments summary** in Analytics — **preview**. ([analytics-improve-agent-effectiveness])
- **Chain of Thought** in test/activity — gated to specific reasoning models (GPT-5 Reasoning, Claude Sonnet, Claude Opus); expect model list to shift.
- **Rationale** — AI-generated, explicitly "may not be accurate."
- Copilot Studio "**new experience**" has its own **Preview and test** + **Activity trace** pages (`agents-experience/preview-overview`) that partly overlap the classic pages cited here — watch which experience a maker is in. ([preview-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/preview-overview))
- Activity/historical data now **requires an Exchange mailbox** and is stored under M365 (not Azure) terms — a recent governance change admins can disable.
- Transcript **512-char truncation** and **SharePoint-answer REDACTED** behaviors are current and easy to mistake for "the agent gave a blank answer."

---

## Part E — "How to get me evidence" playbooks (speak these to a maker)

### E.1 Copilot Studio agent — live/design-time issue
1. Open the agent → **Test**. Turn on **… → Show activity map when testing** (generative) or **Track between topics** (classic).
2. Reproduce the bad turn. Click the agent's response.
3. On the map, open the **knowledge node** (copy: search query, sources used vs searched-unused) and any **tool node** (copy: inputs, outputs, status, latency). Hit **Show rationale**.
4. If there's an error or crash: **… → Save snapshot** and send me **`dialog.json`** from `botContent.zip`.
5. Paste the node details + rationale (+ CoT if your model supports it). That tells me whether it was a grounding miss, a wrong/failed tool call, or a fallback.

### E.2 Copilot Studio agent — production / "it works in test but not live"
1. Go to **Analytics** (you need Analytics Viewer; add **Bot Transcript Viewer** to see transcript text).
2. **Effectiveness → Conversation outcomes → See details**; note Escalated split — **System unintended** = users getting stuck. **Download CSV**.
3. **Use → Knowledge source use** and **Tool use** — send me any source with high error rate or a tool with low success rate.
4. Pick the failing date range → **Download Sessions** → send the CSV row(s). Tell me if any answer shows `REDACTED` (SharePoint) or got cut at 512 chars, so I don't misread a truncation as an empty answer.

### E.3 Copilot Studio agent — prove a fix / regression-test
1. **Evaluate** (test chat icon) or **Evaluation** page → build a test set (generate from your knowledge, or import a spreadsheet of Q + expected A).
2. Add **Tool use** (expected tools) and **General quality/Compare meaning** methods.
3. Run, then **Export test results → CSV**; after your change, rerun the same set and use **Compare with**. Send me both CSVs / the pass-rate diff.

### E.4 M365 declarative agent (Agent Builder / Copilot Chat)
1. In Microsoft 365 Copilot Chat, select the agent, type **`-developer on`**, reproduce the prompt.
2. Copy the whole **debug card**: Capabilities, **Actions → Matched vs Selected functions**, and **Execution details** (search text / request endpoint+method+headers / response / latency). Also copy Agent ID, Conversation ID, Request ID.
3. If you see *No matched functions* or *No functions selected* — that's the finding (description/semantic-match problem or throttling); paste it verbatim.
4. If you're in **Agent Builder** and there's no card, type **`/debug`** in the preview chat and paste that, plus the **Help → Get support** IDs.
5. Pro-code (Agents Toolkit): F5 → Debug panel → **download the capability diagnostic `.txt`** and send it.
6. Set expectations: there is **no analytics dashboard or transcript export** for a declarative agent — the Developer Mode card (or the toolkit log) is the evidence; grab it while the bug is on screen because it's per-turn and disappears.

---

## Key source URLs
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-review-activity
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-transcripts-studio
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-intro
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-results
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-copilot-studio
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/debugging-agents-vscode
