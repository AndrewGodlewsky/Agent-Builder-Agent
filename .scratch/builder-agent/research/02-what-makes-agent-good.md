# Research 02 · What makes a Microsoft agent "good"

**Question:** What principles and best practices separate a good Microsoft agent (M365 declarative + Copilot Studio) from a mediocre one, and how do they map onto the two surfaces?

**Status:** Resolved · **Date:** 2026-07-14 · Grounded in current Microsoft Learn guidance (pages dated Mar–Jul 2026) plus practitioner sources.

---

## 0. The two surfaces at a glance

| | **M365 declarative agent** (Agent Builder / Agents Toolkit) | **Copilot Studio agent** |
|---|---|---|
| Runtime | Rides on Microsoft 365 Copilot's GPT model (auto-upgraded, e.g. GPT 5.0 → 5.1) | Own agent with selectable **orchestration**: classic (NLU, topic-based) or **generative** (LLM reasons over instructions/tools/knowledge) |
| Instruction limit | **8,000 characters** | Free-text instructions on the Overview page; grounded in configured resources |
| Building blocks | Name, Description (≤1,000 chars), Instructions (≤8,000), Knowledge sources, Capabilities, Actions/plugins, Conversation starters (min 3) | Instructions, Knowledge sources, Tools, Topics, Triggers, other Agents, Variables, Power Fx |
| Key doc | [Write effective instructions for declarative agents](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions) · [Best practices](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-best-practices) | [Write agent instructions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions) · [High-quality instructions for generative orchestration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance) |

The **core discipline is the same on both surfaces** — clear role/goal, tight scope grounded in configured resources, explicit rules/tone/format, guardrails, examples, and iterative evaluation. The surfaces differ mainly in *mechanics* (character limit, orchestration model, where fallback/citations are controlled), not in *principles*.

---

## 1. Instruction writing

### Microsoft's named instruction components (M365 declarative)
From [declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions), the **primary components** are:
- **Purpose**
- **General guidelines** — general directions, **tone**, and **restrictions**
- **Skills**

Include **when relevant**: Step-by-step instructions · Error handling and limitations · Feedback and iteration · Interaction examples · Nonstandard terms · Follow-up and closing.

Microsoft's own **example instruction set** uses these Markdown headers, which is effectively a reference skeleton:
`# OBJECTIVE` → `# RESPONSE RULES` → `# WORKFLOW` (each step = **Goal / Action / Transition**) → `# OUTPUT FORMATTING RULES` → `# EXAMPLES` (Valid + Invalid).

### Copilot Studio's construction
[generative-mode-guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance) frames conversational instructions as three combined elements:
- **Constraints** (what the agent may respond to / scope)
- **Response format** (structure, tables, formatting)
- **Guidance** (hints, e.g. which folder/source to search)

### Best-practice rules that separate good from mediocre (both surfaces)
- **Say what to DO, not what to avoid.** Use precise verbs — *ask, search, send, check, use* (M365). Copilot Studio verb table: conditions (*when, if, ensure, compare*), filter (*from, include, exclude*), data (*retrieve, get, analyze, extract*), tools (*notify, direct, ask, assign*).
- **Strict structure is a top signal of intent:** *sections* for logical grouping (no implied order), *bullets* for parallel independent tasks (avoid numbering that implies sequence), *steps* only for true sequential workflows.
- **Make tasks atomic** — split "extract metrics and summarize" into separate steps to stop the model merging/reinterpreting.
- **Every step = Goal + Action + Transition** (purpose, what to do/which tool, criteria to move on or end).
- **Always specify tone, verbosity, and output format.** If unspecified the model infers them, causing inconsistency across model versions. Use an **Output Contract** (goal, format, detail level, tone, include/exclude, example shape).
- **Write in Markdown:** `#/##/###` headers, `-` lists, `` `backticks` `` for tool/system names (e.g. `Jira`, `ServiceNow`), `**bold**` for critical rules.
- **Explicitly reference capabilities/knowledge/actions** at each step (e.g. "Use `ServiceNow KB` for help articles"; "Use code interpreter to generate charts").
- **Provide domain vocabulary** — define acronyms, formulas, org-specific terms to prevent wrong inference.
- **Few-shot examples** for complex scenarios (>1 example to cover edge cases); skip examples for simple ones to save tokens.
- **Add a final self-evaluation / self-check gate** ("Before finalizing, confirm all Section A items appear in the summary").
- **Control reasoning depth via phrasing** — reasoning verbs + "think step by step" for deep; "short answer only, no explanation" for fast (works with GPT-5 auto-routing).

### Length vs. specificity trade-off
- Budget is **8,000 chars** (M365) — do **not** offload instructions into a SharePoint doc to dodge the limit; knowledge content is untrusted, subject to XPIA sanitization, and not honored as system instructions (explicit MS warning).
- **Specific beats long.** Watch for failure modes: over-eager tool use → add "only call the tool if inputs are available, else ask"; repetitive verbatim phrasing → vary/few-shot; verbose output → add concise constraints.
- **Model-drift resilience:** M365 auto-upgrades models. GPT 5.0→5.1 shifted from literal to intent-first reasoning. If you see step reordering/added steps, apply a **literal-execution header** ("Always interpret instructions literally. Never infer intent or fill missing steps… Do not call tools unless a step instructs it.") as an interim stabilizer.

### Copilot Studio specifics
- Reference resources inline with `/` (tool, topic, agent, variable, Power Fx); use the **exact** tool name.
- Be explicit about tool **sequence** when there are >5 tools; be explicit about knowledge doc when there are many.
- **Do not** write instructions that alter citation format/behavior (words like "citation"/"reference") — it can make the orchestrator treat responses as ungrounded and discard them.
- Instructions **can't** override system behaviors: fallback message (edit the Fallback **topic**), Adaptive Card triggers, or search-retrieval logic. Use instructions for *summarization and conversational flow*, not system-level behavior.

---

## 2. Knowledge grounding

Sources: [declarative-agent-best-practices](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-best-practices), [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio).

- **Relevance over quantity — "less is more."** Add only sources needed for expected questions; Copilot performs best with reasonably sized, focused documents. Over-broad sources add noise.
- **Scope tightly:** specific Teams channels/threads over "all my chats"; specific SharePoint sites/folders. In generative orchestration, an internal GPT model filters sources when there are **>25**; uploaded files don't count toward that limit.
- **Right source for the data:** SharePoint/connectors for static/structured knowledge; Copilot connector or API plugin for CRM/database records.
- **Freshness & maintenance:** the agent answers *from* source content, so keep it up to date and periodically refresh/review.
- **Permissions & licensing:** the agent only retrieves content the *user* can access (Entra ID auth per user); some knowledge features need a Copilot license, so shared agents degrade for unlicensed users.
- **Reduce hallucination:**
  - Test queries **with and without** knowledge — if the agent invents answers absent the doc but finds them once added, grounding works; if it over-uses a source, remove it or scope instructions.
  - Copilot Studio **Allow ungrounded responses** setting: OFF = agent blocks any turn that didn't call a knowledge source/tool (fallback fires instead); ON = model general knowledge allowed. (Caveat: OFF doesn't *guarantee* zero general knowledge — model may still blend it with retrieved content. Also: turning it OFF disables follow-up/clarifying questions, which are treated as ungrounded.)
  - **Official/authoritative sources:** mark a trusted source "Official" so the agent uses it without verification (classic orchestration only; not compatible with generative).
  - **Tenant graph grounding with semantic search** improves SharePoint retrieval precision/volume (needs Authenticate with Microsoft).
- **Citations are system-controlled** — don't try to reshape them (see §1).
- **Freshness/real-time:** "Use information from the web"/Web Search (Grounding with Bing) interleaves live web results with your public-site sources.
- **Knowledge vs. actions:** knowledge = *ground factual answers* (read/RAG); actions/tools = *do things / query external systems / transactions*. Mark any create/update/delete action `isConsequential: true`; read-only queries can be nonconsequential. For custom-engine agents, the **M365 Copilot Retrieval API** does RAG over SharePoint/OneDrive/connectors in place (no re-indexing), scoped via KQL `filterExpression` (validate it — bad syntax silently runs *unscoped*), honoring least-privilege permissions.

---

## 3. Conversation / topic design & orchestration

Sources: [generative-mode-guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance), [advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions), practitioner: [Forward Forever](https://forwardforever.com/orchestration-in-copilot-studio-classic-or-generative-ai/), [reshmeeauckloo](https://reshmeeauckloo.com/posts/copilotstudio-genai-versus-classic/).

- **Classic vs. generative orchestration (Copilot Studio):**
  - *Classic* = NLU model, one manually-authored topic per turn via trigger phrases; more **predictable, controllable, cost-effective**; supports custom data sources / Bing Custom Search directly.
  - *Generative* (default for new agents) = LLM reasons over instructions + tools + knowledge, can **chain** multiple topics/tools/knowledge, act autonomously, ask context-aware follow-ups; more natural but less deterministic. Doesn't support custom data / Bing Custom Search unless embedded in a generative-answers node.
  - Guidance: use **generative** for open, multi-step, natural conversation; use **classic** (or author explicit topics) where you need a guaranteed, controlled response.
- **Disambiguation & missing info:** ask **one focused clarifying question at a time, only when needed**; don't overwhelm with options; use conversation history to fill tool inputs, and only ask the user for what's still missing.
- **Follow-up questions** (generative): reference tools/knowledge/variables in instructions so the agent asks the *right* next question and suggests the next logical step — shifts effort from authoring every branch to guiding reasoning (fewer brittle hard-coded flows). Note: requires Allow ungrounded responses ON.
- **Graceful failure / handoff:** provide explicit fallback behavior. In Copilot Studio the **default fallback** ("I'm sorry, I'm not sure how to help with that. Can you try rephrasing?") is edited via the **Fallback system topic**, not instructions. Route forbidden/out-of-scope requests to human support (e.g. "Consult HR"). For highly specific canned responses, author a dedicated **topic** rather than relying on instructions.
- **Autonomous/triggered flows:** define trigger payloads ("Onboard the following employee: …"); keep payloads small via variables; protect triggers against jailbreak injection (limit which tools/parameters the agent may use from trigger content).
- **Confirmation loops:** always confirm before consequential steps (submitting tickets, sending email); test both Allow and Cancel/Deny paths.

---

## 4. Guardrails & safety

Sources: [generative-mode-guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance), [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio) (Moderation), [RAI content-filter troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai).

- **Stay in scope by instruction:** e.g. "Only respond to messages relevant to Contoso and ordering coffee. Otherwise, tell the user you can't help." This is the primary in-scope/out-of-scope guardrail on both surfaces.
- **Content moderation (Copilot Studio):** enforced on all generative requests. Configurable **Lowest → Highest** at agent / topic / prompt level (topic overrides agent); **default is High**. Higher = fewer answers, stricter harmful-content filtering; lower = more answers, more risk. Blocked-query counts are visible in the Power Platform admin center. If moderation over-blocks legitimate behavior, update instructions to state the behavior is expected.
- **Auth-gated data:** knowledge honors per-user Entra ID permissions (agent only surfaces what the user can access); grant apps least privilege (e.g. Retrieval API: `Files.Read.All`, `Sites.Read.All`, `ExternalItem.Read.All`).
- **Injection / jailbreak defense:** don't offload instructions into knowledge sources (XPIA risk); constrain tool use and parameters when acting on trigger/knowledge content (e.g. "only email a specified list of individuals," "only email after checking a knowledge source").
- **Responsible AI validation:** M365 agents pass RAI validation at publish; expect behavioral change across automatic model upgrades and re-test.

---

## 5. Evaluation

Sources: [evaluation-checklist](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-checklist), [agent evaluation (create test set)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-create), [analytics-agent-evaluation-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview), M365 best-practices "Test and iterate."

- **Iterate from day one:** create → publish/RAI → test → iterate. Evaluation spans envisioning through deployment and regression detection.
- **Built-in test chat:** use it frequently; run every conversation starter/sample prompt **plus** edge, long, and irrelevant questions; test across apps (Word/Teams/Outlook behave differently); test confirmation Allow/Deny flows; peer/user testing surfaces unexpected phrasings and missing conversation starters.
- **Spot-check groundedness:** verify summaries/citations against source material; ensure factual queries prefer knowledge sources.
- **Structured evaluation (Copilot Studio Evaluate tab):** a **test set** = up to 100 test cases; a **test case** = prompt + optional expected response (assertion) + acceptance criteria + test method. **General quality** uses an LLM judge to score how well the agent answers.
- **Four-stage evaluation lifecycle** (checklist): (1) foundational test set for core scenarios; (2) baseline pass rate + root-cause analysis (distinguish test-case issue vs. agent-design issue); (3) systematic expansion across quality categories — **Foundational core, Robustness, Architecture (tool/knowledge/routing/handoff), Edge cases (out-of-scope, guardrails)**; (4) continuous evaluation ops triggered by model change, knowledge update, new tool, or production incident.
- **Metrics:** run each set multiple times (probabilistic outputs) and average; **aim for 80–90% pass rate**. Category signal: core fail = broken; robustness fail = too strict; architecture fail = component/workflow bug; edge-case fail = weak guardrails.
- **Adversarial "Always Fail" test set** verifies safety guardrails hold. Production analytics (generated-answer rate & quality, knowledge-source use, blocked queries) close the loop.

---

## 6. Candidate base skeleton

**The invariant structure every good Microsoft agent shares** (synthesized from M365 declarative instruction components + Copilot Studio Constraints/Response format/Guidance + best-practices). This is the candidate template skeleton for ticket 03. Elements marked **[core]** appear in essentially every good agent; **[conditional]** appear when the scenario warrants.

1. **Role / Persona** *[core]* — who the agent is (identity, expertise).
2. **Purpose / Objective / Goal** *[core]* — the single primary job (`# OBJECTIVE`).
3. **Scope & grounding boundary** *[core]* — what topics are in scope; explicitly grounded only in the tools/knowledge actually configured.
4. **Response rules / constraints** *[core]* — behavioral rules (one question at a time, confirm before acting, don't overwhelm).
5. **Tone, verbosity & output format / Output Contract** *[core]* — professional/concise, bullets/tables, detail ceiling, include/exclude.
6. **Capability, knowledge & tool references** *[core]* — explicit named calls to each action/knowledge source, with when-to-use hints.
7. **Workflow / steps (Goal → Action → Transition)** *[conditional]* — for true sequential procedures; atomic steps in Markdown.
8. **Guardrails, safety & out-of-scope / refusal-fallback** *[core]* — in-scope-only rule + graceful "I can't help with that" / route-to-human; moderation posture; injection constraints.
9. **Domain vocabulary / nonstandard terms** *[conditional]* — definitions of acronyms, formulas, org terms.
10. **Examples (few-shot: valid + invalid)** *[conditional]* — illustrate edge cases and anti-patterns.
11. **Self-evaluation / final check gate** *[conditional]* — verify completeness/alignment before responding.
12. **Conversation starters / sample prompts** *[core, agent-level]* — min 3, reflecting core capabilities (metadata, not instruction body).
13. **Error handling & follow-up/closing** *[conditional]* — missing-data behavior, follow-up questions, closing.

### Surface mapping of the skeleton

| Skeleton element | M365 declarative | Copilot Studio |
|---|---|---|
| 1 Role, 2 Purpose | Purpose component; `# OBJECTIVE` | Instructions header; NL description generates it |
| 3 Scope/grounding | Instructions; ground in configured Knowledge/Actions | "Constraints"; must add tools/knowledge first; `/` references |
| 4 Rules, 5 Tone/format | General guidelines; `# RESPONSE RULES` / Output Contract | "Response format"; tone only when non-default |
| 6 Capability refs | `` `backtick` `` named actions/knowledge/capabilities | `/` inline refs; exact tool names; rely on tool descriptions |
| 7 Workflow steps | `# WORKFLOW`, Goal/Action/Transition | Numbered/ordered instructions; or author a Topic |
| 8 Guardrails/fallback | Restrictions; RAI validation; 8k limit (no offloading) | In-scope rule + **Fallback system topic**; moderation Lowest→Highest (default High); Allow-ungrounded toggle |
| 9 Vocabulary | Nonstandard terms component | "Guidance" hints |
| 10 Examples | Interaction examples (few-shot) | Optional; or dedicated topic for canned responses |
| 11 Self-check | Self-evaluation gate | Instruction-level only |
| 12 Conversation starters | Manifest conversation starters (min 3) | Suggested prompts / starter topics |
| 13 Error/follow-up | Error handling; follow-up & closing | Follow-up questions (needs ungrounded ON); trigger payloads |

---

## 7. Skeleton representation — form trade-offs (design rationale)

> **Note:** This section is **design rationale for this effort, not web research.** §6 above settles *which elements* the skeleton contains; this section settles *what form/representation* those elements are expressed in. It supports **wayfinder ticket 03 (the base skeleton)**.

The base skeleton must serve as an **intermediate form** between the builder conversation and two very different outputs: a clean `declarativeAgent.json` file (M365, fully file-based — see research/06 §1) and **click-by-click portal steps** (Copilot Studio, which has no clean import for runtime wiring — see research/06 §4–5). Three candidate forms were considered:

- **Markdown instruction template only** — a prose template with headers (`# OBJECTIVE` / `# RESPONSE RULES` / `# WORKFLOW` / `# GUARDRAILS` / `# EXAMPLES`, i.e. Microsoft's proven header pattern from §1). Lightest to author, most readable for non-technical makers, and looks like the finished instruction box. **Weakness:** name / description / knowledge / capabilities / actions / conversation-starters live **outside** the instruction text — they are manifest/config fields (JSON fields for M365, portal steps for Copilot Studio) and have **no clean home** in a prose template; a second structure must be bolted on. **Best when** the agent is essentially just an instruction prompt with no meaningful config.

- **Pure structured schema** — everything, including the instruction body, decomposed into discrete typed fields (`role`, `purpose`, `rules[]`, `workflowSteps[{goal, action, transition}]`, `guardrails[]`, …); the final instruction text is assembled from the fields. **Best for** machine manipulation / validation / recombination at scale and tooling-driven generation. **Weakness:** (a) Microsoft guidance (§1) recommends instructions be **well-crafted free-text Markdown with deliberate structure** — decomposing and reassembling risks losing that shape and human nuance; (b) it is the **heaviest** form for a mixed / non-technical audience.

- **Hybrid structured spec (CHOSEN)** — a **structured envelope for the config** (name, description, knowledge, capabilities, actions, conversation starters — maps 1:1 to manifest fields) **PLUS one `instructions` field** holding the free-text Markdown body in Microsoft's proven header pattern. The config half renders into `declarativeAgent.json` fields or Copilot Studio portal steps; the instruction half drops into the instruction box unchanged. **Single source of truth for both surfaces.** Trade-off: slightly more structure than a plain template, far less than full decomposition.

**Decision rule:**
- simplest prose-only agents → **Markdown template**;
- machine-generating / validating at scale → **pure schema**;
- helping a **human build a complete agent for two surfaces from one conversation** → **hybrid**.

This effort is the third case (a builder conversation producing both an M365 file and Copilot Studio portal steps), so the **hybrid form was chosen** for ticket 03.

---

## Sources

- Write effective instructions for declarative agents — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions
- Best practices for building declarative agents — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-best-practices
- Declarative Agents overview — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-declarative-agent
- Write agent instructions (Copilot Studio) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions
- Configure high-quality instructions for generative orchestration — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance
- Orchestrate agent behavior with generative AI — https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions
- Knowledge sources summary — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- Review the agent evaluation checklist — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-checklist
- Create a single response test set — https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-create
- Choose evaluation methods — https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview
- Resolve responsible AI content filter errors — https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai
- M365 Copilot Retrieval API overview — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview
- Practitioner: Forward Forever — Orchestration: Classic or Generative — https://forwardforever.com/orchestration-in-copilot-studio-classic-or-generative-ai/
- Practitioner: reshmeeauckloo — GenAI vs Classic orchestration — https://reshmeeauckloo.com/posts/copilotstudio-genai-versus-classic/
