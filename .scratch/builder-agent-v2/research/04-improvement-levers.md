# 04 · Improvement / optimization levers

**Question:** For agents that already *work* but could be *better*, catalog the optimization levers the "improve" (goal-first) framing pulls on — quality eval loop, grounding precision, instruction/output tuning, and cost/latency/Copilot-Credit optimization — each framed as **goal the maker states → lever → the AgentSpec change it implies** so it plugs into the same change-set output as troubleshooting.

**Status:** Resolved · **Date:** 2026-07-14 · Grounded in current Microsoft Learn docs (pages dated **Feb–Jul 2026**, `ms.date` cited per source) plus the credit rates verified live. Extends v1 research/01 (Copilot Credits) and research/02 (eval-loop / 80–90% pass rate) rather than repeating them.

> **AgentSpec vocabulary** (from tickets 01/05/06). The change-set targets the hybrid spec: the instruction body zones **`# ROLE` / `# OBJECTIVE` / `# SCOPE` / `# RESPONSE RULES` / `# OUTPUT FORMAT` / `# WORKFLOW` / `# GUARDRAILS` / `# SELF-CHECK`**, plus the config envelope **`KNOWLEDGE`**, **`ACTIONS`/tools**, and surface settings **orchestration mode**, **Allow ungrounded responses**, **moderation level**, **tenant-graph grounding**, **web search scope**. Every lever below names the zone(s) it edits.

---

## 0. The big shift since v1: an official "improve" framework now exists

The single most important 2026 change for this ticket is that Microsoft shipped a dedicated **evaluation-driven triage and remediation** guidance set — the exact goal-first "improve" loop this effort needs — and moved the core eval methodology into a **cross-product Agents hub** (`learn.microsoft.com/en-us/agents/agent-evaluation/`, `ms.date 2026-02-10`), separate from the Copilot-Studio-specific pages. ([evaluation-checklist](https://learn.microsoft.com/en-us/agents/agent-evaluation/evaluation-checklist), [evaluation-triage-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-overview))

The triage framework has **four layers** ([evaluation-triage-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-overview), `ms.date 2026-03-30`):

- **Layer 1 — Interpret scores / assess readiness:** what do results mean, is it shippable?
- **Layer 2 — Triage failures:** why did this fail, who acts? (evaluation setup vs. agent config vs. platform limitation)
- **Layer 3 — Map failure patterns to remediation:** what specifically to change, and where.
- **Layer 4 — Analyze patterns and improve:** what *systemic* issue do the failures reveal?

The governing remediation contract is **`change X → rerun Y → expect Z`** — "avoids trial-and-error tuning and supports intentional, testable improvements." ([evaluation-triage-remediation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-remediation)) This is the spine the whole "improve" mode should adopt: **no lever is applied without a test to prove it moved the number.**

---

## 1. The quality eval loop — iterate to a good pass rate

**Goal the maker states:** "It mostly works, but I want it *reliably* good — how do I know it's good enough, and how do I push the number up?"

### 1.1 Build a small test set first, then grow it (four stages)
Source: [evaluation-checklist](https://learn.microsoft.com/en-us/agents/agent-evaluation/evaluation-checklist).

- A **test set** = a group of **test cases**; a **test case** = a prompt + optional **expected response (assertion)** + **acceptance criteria** + **test method (grader)**.
- **Stage 1 — Foundational set:** start with **one test prompt per key scenario** (both "should answer" and "should refuse/route" cases). Keep it small; iterate.
- **Stage 2 — Baseline + root-cause:** run it, record pass/fail, compute overall pass rate, tag the agent version + date. For each fail, split cause into **test-case issue** (bad prompt/expected/criteria) vs. **agent-design issue** (instruction/knowledge/tool flaw).
- **Stage 3 — Systematic expansion** across four quality categories: **Foundational core** (must-pass, regression detection), **Robustness** (paraphrase / rich context / multi-intent / user-specific), **Architecture** (tool call, knowledge retrieval + citation, routing, handoff), **Edge cases** (boundary conditions, out-of-scope, guardrails).
- **Stage 4 — Continuous ops:** scheduled reruns triggered by **model change, major knowledge update, new tool/connector, or production incident.**

### 1.2 Measure honestly, target 80–90 %
- Outputs are probabilistic — **run each set multiple times and average.** "**Aim for a realistic pass rate of 80–90 %, based on your business needs.**" ([evaluation-checklist](https://learn.microsoft.com/en-us/agents/agent-evaluation/evaluation-checklist)) (This confirms the v1 research/02 §5 target against the current page.)
- **Category signal → what a failing category means** (drives which lever to pull): **Core fail = something broke** (check recent changes); **Robustness fail = agent too strict** (over-focused on phrasings); **Architecture fail = a component/workflow needs debugging**; **Edge-case fail = guardrails need strengthening.**

### 1.3 Readiness thresholds — when to ship vs. keep iterating
The **quick reference** gives hard decision gates ([evaluation-triage-quick-reference](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-quick-reference), `ms.date 2026-03-30`):

| Category | Threshold | Decision |
|---|---|---|
| **Safety & compliance** | **< 95 %** | **Block** — triage safety failures first |
| **Core business** | **< 80 %** | **Iterate** — triage the lowest-scoring set |
| Capabilities | below threshold | Conditional deploy — document gaps |
| All scores above threshold | — | Deploy |

### 1.4 Prioritize fixes by pattern, not one-by-one
Source: [evaluation-triage-remediation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-remediation), [evaluation-triage-quick-reference](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-quick-reference).

- With **>15 failures, don't triage each individually** — start with the **lowest-scoring evaluation set**, review a few, and if they **share a root cause, one fix clears many.**
- Pattern table: **≥80 % of fails share a root cause → systemic issue, fix the category**; **scores flat after a fix → wrong root cause, re-triage**; **one score up + another down → instruction conflict, resolve it.**
- **Efficient rerun strategy** (saves credits + time): single test-case fix → rerun only that case; agent-config change → affected set + spot-check one unrelated set for regressions; **system-prompt change → full suite** (broad impact); knowledge update → grounding + factual-accuracy sets; baselines → full suite ×3.

**AgentSpec change implied:** the eval loop is *meta* — it doesn't edit a zone directly, it **produces the change-set and gates it.** The builder's "improve" mode should: (a) reconstruct or ask for a **test set** (min one case per SCOPE scenario + the adversarial "always-fail" safety cases), (b) attach a **verification step** (`rerun Y → expect Z`) to every proposed edit, and (c) **refuse to declare "improved" without a measured before/after.** M365 declarative agents have no built-in Evaluate tab, so for that surface the loop is the manual **Create → Publish (RAI) → Test → Iterate** cycle ([declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions)); the test set is run by hand in Copilot/Teams.

---

## 2. Grounding precision — curate, narrow, and lock down retrieval

**Goal the maker states:** "It answers, but sometimes from the wrong doc, or it makes things up, or it pulls stale/general info instead of my source."

### 2.1 "Less is more" — curate and scope the corpus
Source: [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio) (`ms.date 2026-06-23`), [declarative-agent-best-practices], v1 research/02 §2.

- Add **only** sources needed for expected questions; over-broad sources add noise and cause wrong-source retrieval. Prefer **specific SharePoint sites/folders and specific Teams channels** over "all."
- In **generative orchestration**, an internal GPT model **filters sources when there are >25** (uploaded files are exempt from the 25 cap). Beyond that count, **description quality of each source is the selection lever** ([advanced-generative-actions] authoring-descriptions).
- **Wrong-source retrieval fix** (from the remediation map): "Verify source names and indexing. **Check if source content vocabulary matches how users ask questions.**" ([evaluation-triage-remediation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-remediation)) → **restructure docs into shorter sections with clear headings that mirror user phrasing**, and duplicate critical answers across sections (the "retrieval ranking" workaround).
- **AgentSpec change:** prune/rescope `KNOWLEDGE[]` entries; tighten each source's **name + description**; add a `# GROUNDING` line "When answering about `<topic>`, use `<specific section>` of `<specific source>`" (the *correct-source-wrong-extraction* remediation).

### 2.2 Strict grounding — turn "Allow ungrounded responses" OFF
Source: [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio).

- **OFF** = the agent **blocks any turn where it didn't call a knowledge source or tool**; the fallback topic fires instead. Requires **generative orchestration** on.
- **Two documented caveats** (flag both to the maker):
  1. OFF **doesn't guarantee zero general knowledge** — "the model might still incorporate general knowledge when it **combines** it with retrieved content." It only blocks turns that used *no* source/tool at all.
  2. OFF **breaks legitimate follow-ups** — a context-only answer from conversation history (e.g. "Does that apply to sale items too?") gets **blocked**, because no new retrieval happened.
- **AgentSpec change:** set **`Allow ungrounded responses = OFF`** (Copilot Studio only). Pair with an instruction in `# GROUNDING`: *"Only answer based on information found in your knowledge sources. If the information isn't available, say so."* (the *ungrounded-response* remediation). **Surface caveat:** Agent Builder (M365 declarative) has **no equivalent hard switch** — its "Only use specified sources" merely *prioritizes*; Microsoft says use Copilot Studio when strict grounding is mandatory (v1 research/01 A.4).

### 2.3 Scoped web search vs. open web
Source: [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio), v1 research/01 A.4.

- **"Use information from the web" / Web Search** uses **Grounding with Bing** and runs **in parallel** with your configured public-site sources, interleaving results. Turning it **off** removes open-web noise; leaving only **scoped public-site knowledge** (M365: ≤4 URLs; Copilot Studio generative: 25) keeps answers to sanctioned domains.
- **AgentSpec change:** toggle **Web Search off** when the maker wants closed-corpus behavior; or keep it on but **add specific site URLs** to `KNOWLEDGE` to bias interleaving toward trusted domains.

### 2.4 Precision boosters
- **Tenant graph grounding with semantic search** (Copilot Studio, generative only): "greater volume of context, with **greater precision**" for SharePoint retrieval; requires **Authenticate with Microsoft** + an M365 Copilot license in the tenant; **costs 10 Copilot Credits per grounded message** (see §4). Trade-off: "certain users and queries might experience a **small increase in latency**." **Turn it off** if response quality drops or no M365 Copilot license is in-tenant. **File-size flag:** the page states support "up to **200 MB**" (maker-licensed) while a note says **512 MB for PDF/PPTX/DOCX** — a nuance/possible change vs. v1's flat 512 MB; confirm per tenant. ([knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio))
- **Official / authoritative sources:** mark a highly-trusted source "Official" so the agent uses it **without verification** (response gets a distinctive indicator). **Classic orchestration only — incompatible with generative** (must turn generative off to use it).
- **Conflicting sources** remediation: add *"When sources conflict, prefer `<primary source>` and note the discrepancy."* → `# GROUNDING`.

---

## 3. Instruction / output tuning

**Goal the maker states:** "The answers are fine but too long / wrong tone / inconsistent format / it over-uses a tool — tighten it up without breaking what works."

Primary source: [declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions) (`ms.date 2026-05-11`) + [evaluation-triage-remediation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-remediation).

### 3.1 The named prompt failure-modes and their fixes (declarative)
| Symptom | Fix (goes in) |
|---|---|
| **Over-eager tool use** (calls tools without inputs) | *"Only call the tool if necessary inputs are available; otherwise, ask the user."* → `# RESPONSE RULES` |
| **Repetitive verbatim phrasing** | vary responses; add **>1 example (few-shot)**, or remove the single example to save tokens → `# EXAMPLES` |
| **Verbose / over-formatted output** | add concise constraints + a concise example → `# OUTPUT FORMAT` |

### 3.2 Tone / verbosity / output-contract (the highest-leverage tighten)
- **Always specify tone, verbosity, and output format** — if unspecified the model *infers* them and drifts across model versions. Example: *Tone: professional and concise. Output: three bullets per section. Return only the requested format; no explanations.*
- Use an **Output Contract** block (Pattern 4): Goal / Format / Detail level (`do not exceed X bullets per section`) / Tone / Include / Exclude (`no "helpful tips"`) / Example shape. → `# OUTPUT FORMAT`.
- Remediation-map specifics that map cleanly to change-set edits: **too verbose/terse** → *"For simple questions, respond in 1–3 sentences; for complex procedures, use structured steps"*; **poor structure** → *"Use numbered steps for procedures…"*; **inconsistent tone** → **consolidate tone into one section, remove contradictory guidance**; **lacks empathy** → context-specific tone rule.

### 3.3 Reasoning-depth control (verbosity's cousin — also a latency/cost lever, see §4)
- Wording steers GPT-5 auto-routing: **deep** (reasoning verbs + "think step by step") vs. **fast/minimal** ("Short answer only. No reasoning or explanation."). Use minimal-reasoning phrasing for extraction/lookup to cut latency and tokens. → `# RESPONSE RULES` / per-`# WORKFLOW` step.

### 3.4 Stay under 8,000 chars **while improving** — the "instruction budget" problem
This is the sharpest new 2026 insight and central to the *improve* framing: **remediation adds instructions, and prompts have finite capacity.** ([evaluation-triage-remediation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-remediation))

- Symptoms of **instruction overload** (not missing guidance): previously-passing cases start failing after unrelated edits; agent follows some rules but ignores others; a fix for one scenario regresses another; **a new, clear instruction has no effect.**
- Five budget strategies: **Consolidate** (merge overlapping rules — three tone rules → one paragraph); **Prioritize** (highest-priority instructions **first and last** — models attend most to prompt start/end); **Simplify** (verbose → concise); **Externalize** (move static reference lists/policies into **knowledge sources**, not the prompt); **Test holistically** (rerun the **full** suite after any prompt edit to catch regressions).
- **Hard limit reminder:** 8,000 characters for M365 declarative instructions, and **do NOT offload instructions into a knowledge doc to dodge it** — knowledge is untrusted, XPIA-sanitized, and not honored as system instructions. So the *only* legitimate way to "improve" a maxed-out prompt is Consolidate/Simplify/Prioritize/Externalize. ([declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions))
- **AgentSpec change:** a *net-token-neutral* tightening pass across `# RESPONSE RULES` / `# OUTPUT FORMAT` / `# WORKFLOW`; move enumerated reference data to `KNOWLEDGE`; add a `# SELF-CHECK` gate only if it earns its tokens.

### 3.5 Model-drift resilience (improve-in-place after an upgrade)
- M365 auto-upgrades the model (GPT 5.0 → 5.1 shifted from literal to intent-first reasoning), so a working agent can *regress on its own*. Interim fix = **literal-execution header** (Pattern 8: "Always interpret instructions literally… Do not call tools unless a step instructs it."). Longer fix = **Pattern 9 audit prompt** ("Evaluate and migrate existing declarative agent instructions") — a repeatable structured audit that outputs a header patch + top-5 "Issue → Fix" + a rewrite of the riskiest step. ([declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions), [declarative-model-migration-overview]) **This audit prompt is effectively an off-the-shelf "improve" engine the builder can adopt.**

### 3.6 Copilot Studio wrinkle
Most correctness/grounding/tone/safety remediations live in the **Instructions pane of the Overview page**; knowledge and tool changes live on their own pages. But instructions **can't override system behaviors** — **fallback message** is edited in the **Fallback system topic**, not instructions; and **don't write "citation/reference"-shaping instructions** (can make the orchestrator treat answers as ungrounded and discard them). ([evaluation-triage-remediation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-remediation), v1 research/02 §1).

---

## 4. Cost / latency / Copilot-Credit optimization

**Goal the maker states:** "It works but it's expensive / slow — cut the credit burn and latency without losing quality."

### 4.1 What drives credit consumption — **verified live against current docs**
Source: [requirements-messages-management](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management) (`ms.date 2026-06-11`, verified 2026-07-14). **These are unchanged from v1 research/01** — the Sept 1 2025 "messages → Copilot Credits" cutover rates still hold:

| Billable event | Rate | M365-Copilot-licensed user (B2E) |
|---|---|---|
| **Classic answer** | **1** credit | No charge |
| **Generative answer** | **2** credits | No charge* |
| **Agent action** (triggers, deep reasoning, topic transitions, CUA) | **5** credits | No charge |
| **Tenant graph grounding** (per message) | **10** credits | No charge |
| **Agent flow actions** | **13** per **100 actions** | No charge (only via "When an agent calls the flow" trigger) |
| AI tools — basic / standard / premium | **1 / 15 / 100** per **10 responses** | No charge |
| Content processing tools | **8** per **page** | No charge |
| Voice: Classic / GenAI / Premium GenAI | **10 / 35 / 75** per minute | core activity included |

\* Generative answers are free **only** when the agent is built in **Agent Builder in M365** *and* the response doesn't use tenant-graph grounding. **Reasoning models bill twice:** *feature rate* + **premium AI-tools meter (10 credits / 1K tokens)** on top. A single complex turn can stack meters — MS's own example: tenant-graph + generative = **10 + 2 = 12 credits** for one prompt.

### 4.2 The optimization levers (cheapest → most structural)
- **Prefer the free surface for B2E:** if every user is **M365-Copilot-licensed**, core agent usage is **no charge** — so **unlicensed external users are what generate the bill.** A cheaper design keeps internal agents on the M365-licensed path.
- **Avoid the 10-credit tenant-graph meter unless it's earning quality:** it's the single most expensive per-message line. Turn it **off** where standard grounding suffices (also removes its latency cost, §4.3).
- **Downgrade answer type where possible:** a **classic answer (1)** vs. **generative (2)** vs. **agent action (5)** is a 5× spread. Deterministic/canned responses via **classic answers or authored topics** are cheapest; reserve generative + actions for turns that need them.
- **Don't use a reasoning model by default** — it adds the premium token meter. Use `# RESPONSE RULES` minimal-reasoning phrasing (§3.3) to keep routine turns on cheap/fast inference.
- **Move repetitive deterministic work to agent flows** (13/100 actions) instead of many 5-credit agent actions, when the task is a fixed sequence needing no per-step reasoning.
- **BYO-model / Azure Foundry models are billed separately** (excluded from these rates) — a lever only if the tenant already pays that meter.
- **Cap and forecast:** set **per-agent monthly consumption limits** in Power Platform admin center (**Licensing > Copilot Studio > Manage Agents**) to hard-stop runaway spend before the **125 %-of-prepaid overage enforcement** disables the agent. Forecast with the **[Copilot Studio agent usage estimator](https://microsoft.github.io/copilot-studio-estimator/)** (vary agent type / traffic / orchestration / knowledge / tools). ([requirements-messages-management](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management))

### 4.3 Latency levers
- **Tenant-graph semantic search** adds a "small increase in latency" — off when quality doesn't need it. ([knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio))
- **Fewer knowledge sources / fewer tools** = less orchestration overhead (the >25-source filter and >5-plugin semantic matching both add work; v1 research/01 A.5).
- **Minimal-reasoning phrasing** (§3.3) cuts reasoning-token latency.
- **Fewer orchestration hops:** every connected/child-agent hop and every extra `# WORKFLOW` step adds latency; keep autonomous chains **<15 consecutive actions** (v1 research/01 B.6). Multi-agent split only above ~30–40 tool/topic choices.

### 4.4 When a cheaper surface / orchestration suffices
- **Classic orchestration** is "more predictable, controllable, **cost-effective**" — if the agent is really single-intent Q&A over a fixed corpus, classic (or authored topics) avoids the generative planning layer's per-turn cost and the 5-credit agent-action meter. ([advanced-generative-actions], v1 research/02 §3)
- **Agent Builder / M365 declarative** is the cheapest surface for in-M365, licensed-user, retrieval+summarize workloads (generative answers free there absent tenant-graph). **Escalate to full Copilot Studio only when a hard capability forces it** (autonomy, multi-step orchestration, external channels, strict grounding, Dataverse) — the v1 research/01 C.3 trigger set. A surface *downgrade* (Copilot Studio → declarative) is itself a cost/latency lever when none of those triggers apply.
- **AgentSpec change:** flip **orchestration mode** to classic; or recommend a **surface change** in the change-set (with the credit note — this is the "map fog" edge case ticket 06 calls out: a surface flip that changes metering).

---

## 5. The improve-lever catalog as change-set rows (goal → lever → AgentSpec change)

| # | Goal the maker states | Lever | AgentSpec change | Verify |
|---|---|---|---|---|
| L1 | "Is it good enough / push the number up" | Build small test set → baseline → expand → rerun-avg | *(meta)* attach test set + `change X→rerun Y→expect Z` to every edit | Pass rate 80–90 %; safety ≥95 % |
| L2 | "Answers from the wrong doc" | Curate/rescope corpus; align source vocab to user phrasing; tighten descriptions | prune `KNOWLEDGE[]`; `# GROUNDING`: use `<section>` of `<source>` | Rerun grounding set |
| L3 | "Makes things up / uses general knowledge" | Strict grounding | **Allow ungrounded = OFF** + `# GROUNDING` "only answer from sources" (Copilot Studio; declarative can't hard-block) | Rerun grounding set |
| L4 | "Pulls stale/open-web noise" | Scope web search | Web Search off, or add specific site URLs to `KNOWLEDGE` | Rerun freshness cases |
| L5 | "SharePoint retrieval imprecise" | Tenant-graph semantic search on (cost/latency trade) | enable tenant-graph grounding (+10 credits/msg) | Rerun; watch latency |
| L6 | "Too long / wrong tone / inconsistent format" | Output contract + tone/verbosity spec | `# OUTPUT FORMAT` contract; consolidate tone in one block | Rerun response-quality set |
| L7 | "Over-eager / wrong tool" | Gate tool use; sharpen tool descriptions + negative examples | `# RESPONSE RULES` gate; `ACTIONS` description edits | Rerun tool-invocation set |
| L8 | "Prompt maxed at 8k / edits regress others" | Instruction-budget hygiene | Consolidate / Prioritize (first+last) / Simplify / Externalize to `KNOWLEDGE` | **Full-suite** rerun |
| L9 | "Regressed after model upgrade" | Literal-execution header → Pattern 9 audit | prepend stabilizing header; then structural rewrite | Rerun full suite |
| L10 | "Too expensive / slow" | Downgrade answer type; avoid tenant-graph/reasoning-by-default; cap spend; cheaper surface/orchestration | classic answers/topics; minimal-reasoning `# RESPONSE RULES`; per-agent cap; orchestration/surface flip | Estimator + rerun |

---

## 6. Where docs changed recently or are ambiguous (flags)

- **NEW since v1:** the **evaluation-driven triage & remediation** guidance set (`evaluation-triage-*`, `ms.date 2026-03-30`, updated Apr 2026) — 4-layer framework, remediation map, quick reference, instruction-budget guidance. This is the canonical "improve" loop and did not exist in v1 research. ([evaluation-triage-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-overview))
- **Eval methodology relocated** to a **cross-product Agents hub** `learn.microsoft.com/en-us/agents/agent-evaluation/` (`ms.date 2026-02-10`) — the Copilot-Studio pages now link out to it. Watch for further consolidation.
- **Credit rates: verified unchanged** (`ms.date 2026-06-11`) — classic 1 / generative 2 / action 5 / tenant-graph 10 / agent-flow 13-per-100 / AI-tools 1·15·100-per-10 / content-processing 8-per-page / voice 10·35·75-per-min. Reasoning models bill feature-rate **+** premium token meter. Overage enforcement still **125 %** of prepaid. New: **per-agent monthly consumption caps** in PPAC.
- **Tenant-graph file-size nuance:** page now cites **200 MB** (maker-licensed) alongside a **512 MB (PDF/PPTX/DOCX)** note — reconcile per tenant; v1 stated a flat 512 MB. ([knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio))
- **Allow-ungrounded OFF** still (a) doesn't guarantee zero general knowledge and (b) blocks context-only follow-ups — both documented caveats to surface to makers.
- **Official/authoritative sources** remain **classic-orchestration only** (incompatible with generative) — a strict-grounding lever that costs you the generative planner.
- **Surface asymmetry persists:** M365 declarative (Agent Builder) has **no strict-grounding switch and no built-in Evaluate tab** — the eval loop there is the manual Create→Publish→Test→Iterate cycle. Improve-mode must branch on surface.

---

## Sources

- Review the agent evaluation checklist — https://learn.microsoft.com/en-us/agents/agent-evaluation/evaluation-checklist
- Improve agents using evaluation-driven triage and remediation (overview) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-overview
- Map failure patterns to remediation strategies — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-remediation
- Triage and remediation quick reference — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-quick-reference
- Triage agent failures (diagnose & prioritize) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-failure
- Interpret evaluation scores / readiness — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-triage-readiness
- Knowledge sources summary (Allow ungrounded, tenant-graph, official sources, moderation) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- Write effective instructions for declarative agents (8k limit, tone/verbosity, failure-modes, reasoning control, Patterns 1–9) — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions
- Billing rates and management (Copilot Credits — verified live) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management
- Copilot Studio agent usage estimator — https://microsoft.github.io/copilot-studio-estimator/
- Orchestrate agent behavior with generative AI — https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions
- (v1 cross-refs) ../builder-agent/research/01-platform-building-blocks.md · ../builder-agent/research/02-what-makes-agent-good.md
