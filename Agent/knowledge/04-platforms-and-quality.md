# Knowledge: Platforms & Agent Quality

Combined reference for the Agent Builder — Part A is the platform building blocks & the M365-vs-Copilot-Studio delta; Part B is what makes an agent good. Both grounded in current Microsoft Learn documentation.

---

# PART A — Platform building blocks & the surface delta


_Research findings — grounded in current Microsoft Learn documentation (fetched 2026-07-14). Doc `ms.date` values cited are mostly June–July 2026._

> **Scope note / terminology.** Microsoft's naming is drifting and is a frequent source of confusion. "Agents for Microsoft 365 Copilot" split into two architectures: **declarative agents** (use Copilot's own orchestrator + foundation models) and **custom engine agents** (bring your own orchestrator/models). A **Copilot Studio agent** is a distinct authoring product that can produce *either* a declarative agent *or* a full custom/autonomous agent. So the practical fork this ticket asks about — "M365 declarative agent vs. full Copilot Studio agent" — maps onto the deeper architectural fork **declarative (Copilot-hosted) vs. custom-engine (Copilot Studio-hosted)**. Keep that in mind throughout; the "delta" section makes it concrete.

---

## Part A — M365 declarative agents

### A.1 What it is / building blocks
A declarative agent customizes Microsoft 365 Copilot by declaring **instructions, knowledge, actions, and capabilities**; it runs on Copilot's shared orchestrator, foundation models, and trusted AI services, and inherits all Microsoft 365 security/compliance/RAI controls. No extra hosting is required. ([overview-declarative-agent](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-declarative-agent), [agents-overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-overview))

Authoring tools: **Agent Builder** in M365 Copilot (low-code), **Microsoft 365 Agents Toolkit** (pro-code, VS/VS Code), **Copilot Studio**, and **SharePoint agents**. ([overview-declarative-agent](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-declarative-agent))

### A.2 The declarativeAgent manifest (high level — exact schema is a separate ticket)
The current schema is **v1.7**. At a high level the manifest declares:
- **Identity/metadata**: `name`, `description`, icon, `instructions`, `conversation_starters`.
- **`capabilities[]`**: an array of capability/knowledge objects — `WebSearch` (with optional `sites` for scoped search), `CodeInterpreter`, `GraphicArt` (image generator), `OneDriveAndSharePoint`, `Email`, `People` (with `include_related_content` in v1.6+), `TeamsMessages`, `Meetings`, `Dataverse`, and Copilot connectors. Different capabilities were added at different schema versions (scoped web search, Email, Teams, Dataverse, People at v1.3+; Meetings and People related-content at v1.6+). ([knowledge-sources](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/knowledge-sources))
- **`actions`**: API plugins (see A.5).

The manifest is the trusted, versioned, governed source of agent behavior — Microsoft explicitly warns **not** to offload instructions into knowledge sources to dodge the length limit (knowledge content is untrusted and subject to XPIA sanitization). ([declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions))

### A.3 Instructions — configuration and the hard limit
- **8,000-character limit** on instructions (hard). ([declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions))
- Structured guidance: purpose + guidelines + skills; use Markdown headers/lists; make tasks atomic; specify tone/verbosity/output contract; reference capabilities by name.
- **Recent change / ambiguity:** Copilot periodically auto-upgrades the underlying GPT model; the **GPT 5.0 → 5.1** move shifted from literal instruction-following to intent-first adaptive reasoning, which can change agent behavior in step-by-step scenarios. Microsoft recommends a "literal-execution header" as mitigation. This is an ongoing moving target. ([declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions))

### A.4 Knowledge sources and per-agent limits (Agent Builder)
| Source | Limit / notes | License needed? |
|---|---|---|
| Public website (web search) | Up to **4** URLs; scoped web search grounds on **Bing-indexed** content only (can be stale for dynamic/JS content); URLs max 2 levels, no query params | No |
| Search all websites (open web) | Toggle; admin can globally disable | No |
| SharePoint | Up to **100** files/folders/sites; **+1 SharePoint list** (max 20,000 rows / 50 MB, then truncated); respects permissions + sensitivity labels; blocked if Restricted SharePoint Search on | Yes (Copilot) |
| OneDrive | Up to **50** files | Yes |
| Embedded (uploaded) files | Up to **20** files; stored in SharePoint Embedded; size caps: .doc/.docx/.pdf/.ppt/.pptx/.txt **512 MB**, .xls/.xlsx **30 MB**; **not** in GCC; no Information Barriers support | Yes / metered |
| Teams messages | Up to **5** chat/channel/meeting URLs (or all) | Yes (add-on) |
| Teams meetings | Optional scope to 5 meetings; series limited to last 4 instances | Yes (add-on) |
| Outlook email | All mailbox; **can't scope** to folder/shared mailbox in Agent Builder (Agents Toolkit can, incl. up to 25 group mailboxes) | Yes (license only) |
| People | On by default with Copilot license; profile/org data | Yes (license only) |
| Copilot (Graph) connectors | Admin must enable; can scope by connector attribute (Jira project, ServiceNow KB, GitHub repo, etc.) | Yes |
| Dataverse | **Agents Toolkit only — not in Agent Builder** | Yes |

Sources: [agent-builder-add-knowledge](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge), [knowledge-sources](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/knowledge-sources)

**Knowledge control gap:** Agent Builder's "Only use specified sources" only *prioritizes* your sources; it **cannot fully block** general AI knowledge. Microsoft explicitly says use Copilot Studio if you need strict grounding. ([agent-builder-add-knowledge](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge))

### A.5 Capabilities and actions
- **Code interpreter** and **image generator** — both no license required. **Web search / scoped web search** — no license. ([knowledge-sources](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/knowledge-sources))
- **Actions = API plugins** backed by an OpenAPI spec or an **MCP server**. Multiple plugins can run at once. Practical limits: **up to 5 plugins are always injected into the prompt; beyond 5, semantic matching by description is used**; a plugin may declare unlimited functions but response quality degrades past ~10 functions. There is also an **undocumented/observed** orchestrator behavior of silently stopping after the 3rd distinct API action in a turn (community Q&A, not official). ([overview-plugins](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-plugins), community Q&A referenced via search)

### A.6 Architecture — the hard constraints that define the ceiling
Declarative agents use a **sequential grounding-then-tool-call pipeline** that Microsoft controls; developers control only instructions, knowledge, and plugins. Because grounding and external tool calls happen sequentially, **you cannot do chained operations over grounding data or looped/iterative operation plans** — it is "not suitable for complex multistep operations." ([declarative-agent-architecture](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-architecture))

Stated technical limits (optimize to ~66% of each):
| Limit | Value |
|---|---|
| Grounding record limit | **50 items** |
| Plugin response limit | **25 items** |
| Token limit | **4,096** (all context + response) |
| Timeout | **45 seconds** |

Primary limitations called out: no control of iterative reasoning loops / orchestration; no custom corpus (except Copilot Tuning); sequential processing; dynamic/non-OpenAPI web content grounds poorly. **Not** suitable for complex decision trees, large-data/full-document processing, custom models, or reliable recency from dynamic sites. Declarative agents are also **individual-use** and **user-initiated only — no proactive/autonomous behavior** and **M365 channels only** (Copilot, Teams, Word, Excel, Outlook). ([declarative-agent-architecture](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-architecture), [agents-overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-overview))

**Recent change (flag for verification):** third-party sources report **MCP Apps** (interactive UI rendered inside Copilot chat) shipping ~April 2026 and an Agents Toolkit CLI/natural-language scaffolding plugin. Not yet corroborated in the core Learn pages fetched here — treat as needs-official-confirmation. ([Voitanos, Apr 2026](https://www.voitanos.io/blog/microsoft-365-copilot-declarative-agents-whats-new-202604-april-2026/))

---

## Part B — Copilot Studio agents

### B.1 Building blocks
Topics, **tools/actions**, **knowledge**, and **other agents** — assembled under one of two orchestration modes. ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions))

### B.2 Generative vs. classic orchestration
**Generative orchestration is now the default** for new agents. It adds an LLM planning layer that interprets intent, decomposes multi-intent queries, and picks the best combination of topics, tools, knowledge, and other agents — and can respond autonomously to event triggers. **Classic orchestration** matches user query → topic trigger phrases, selects a single topic, and uses knowledge only as a fallback; tools/knowledge are called explicitly from topics. ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions))

Selection is driven by the **name + description** of each topic/tool/agent/knowledge source, so description quality is the main authoring lever. Known generative-mode limitations: no Conversational-boosting customization, no custom-entity input params, no auto-disambiguation (Multiple Topics Matched not called), limited conversation-history window, "official source" marking incompatible with generative mode. ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions))

### B.3 Knowledge sources and limits
| Source | Generative mode | Classic mode | Auth |
|---|---|---|---|
| Public website (Bing) | **25** websites | 4 URLs | None |
| Documents (uploaded to Dataverse) | All | Limited by Dataverse storage | None |
| SharePoint | **25** URLs | 4 per generative-answers node | Agent user Entra ID |
| Dataverse | **Unlimited** | 2 sources × up to 15 tables | Agent user Entra ID |
| Enterprise data via Copilot connectors | **Unlimited** | 2 per agent | Agent user Entra ID |

Generative orchestration filters sources with an internal GPT model when there are >25 sources (uploaded files are exempt from that 25 cap). Generative mode doesn't support Custom Data / Bing Custom Search / Azure OpenAI as agent-level knowledge (must embed in a generative-answers node). **Web Search** uses Grounding with Bing. **Tenant graph grounding with semantic search** (optional, extra cost, requires Authenticate-with-Microsoft + a Copilot license in tenant) raises quality and supports SharePoint/connector files up to 512 MB. **Allow ungrounded responses** can be turned off to force tool/knowledge-grounded answers — the strict grounding control that Agent Builder lacks. ([knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio))

### B.4 Power Automate flows / agent flows
**Agent flows** are deterministic, rule-based automations built in Copilot Studio (or converted from a Power Automate cloud flow, a **one-way** conversion that switches billing to Copilot Credits). Flows with the **"When an agent calls the flow"** trigger can be added as **tools**. Action types: connectors (M365, third-party, custom), AI capabilities (LLM prompts, call-an-agent), human-in-the-loop (approvals), and control structures (loops/branches/child flows). Every executed action consumes capacity. Note the docs distinguish a **classic vs. new** workflow experience; agent flows are the classic experience. ([flows-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview))

### B.5 Connectors / actions / tools
Tools include prebuilt/custom **connectors**, agent flows, prompts, and MCP-style tools; in generative mode the agent chooses them by description. Deep guidance in [add-tools-custom-agent] and [advanced-flow]. ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions), [advanced-flow](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-flow))

### B.6 Autonomous / event triggers
**Requires generative orchestration.** An event (Dataverse row added/modified/deleted, SharePoint item created, OneDrive file created, Planner task complete, **Recurrence**, etc.) delivers a **trigger payload** (JSON/text + author instructions) to the agent via a connector; the agent then selects actions/topics per its instructions. Key constraints:
- **Maker credentials only** — all authenticated triggers/actions run as the author's identity (data-exposure risk; makers are warned pre-publish).
- Requires **solution-aware cloud flow sharing** enabled in the environment; admins can block event triggers via DLP data policies.
- Each trigger payload is a **billed** message; frequent/recurrence triggers can hit quota throttling. Keep to **<15 consecutive actions/topics** for reliability. ([authoring-triggers-about](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-triggers-about))

### B.7 Agent-to-agent / multi-agent
Options: **child agents** (lightweight, in-agent), **connected agents** (other Copilot Studio agents in the same environment), and external agents via the **A2A protocol**, **Microsoft Foundry agents (preview)**, **Fabric Data agents (preview)**, and **Microsoft 365 Agents SDK agents (preview)**. Rule of thumb: split into connected agents when a single agent exceeds ~**30–40** tool/topic/agent choices, or when teams/lifecycle/settings must be independent. Trade-offs: added latency per orchestration hop; larger test/governance surface; an agent used as a main agent with connected agents can't itself be a connected agent elsewhere; Fabric Data agents can't be redirected-to from topics and don't work when the main agent is deployed to M365 Copilot. ([authoring-add-other-agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents))

### B.8 Channels
Publish (once, applies to all channels) to: **Microsoft Teams + M365 Copilot**, **SharePoint**, **WhatsApp**, **custom website / demo website**, **mobile app**, **Facebook**, and **Azure Bot Service channels** (Slack, Telegram, Twilio/SMS, Line, Kik, GroupMe, Direct Line Speech, Email, Cortana). Voice/telephony tiers also exist (Classic Voice, GenAI Voice, Premium GenAI Voice). ([publication-fundamentals-publish-channels](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels), [requirements-messages-management](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management))

### B.9 Authentication
Three modes: **Authenticate with Microsoft** (Entra ID, default; auto for Teams/Power Apps/M365 Copilot), **No authentication** (anyone with link — but then tools can't use user credentials), and **Authenticate manually**. Tenant-graph semantic search requires Authenticate-with-Microsoft. ([publication-fundamentals-publish-channels](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels))

### B.10 Environment / licensing / consumption constraints
- **Copilot Credits** are the billing unit (replaced "messages" on **Sept 1, 2025**). Capacity is **prepaid packs pooled across the tenant** and/or **pay-as-you-go** (Azure meter). Unused credits don't roll over. ([requirements-messages-management](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management), search: billing-licensing)
- Billing rates: **Classic answer 1**, **Generative answer 2**, **Agent action 5**, **Tenant graph grounding 10**, **Agent flow 13 per 100 actions**, AI tools **basic 1 / standard 15 / premium 100** (per 10 responses); reasoning models add the premium token meter on top of the feature rate.
- **Microsoft 365 Copilot-licensed users incur no charge** for core B2E agent usage (and for agent flows only via the "When an agent calls the flow" trigger); unlicensed users consume tenant credits. Computer-Using Agents are **not** covered by the M365 Copilot license.
- **Overage enforcement at 125% of prepaid capacity disables custom agents**; agent-flow enforcement blocks new flow runs when prepaid capacity is exhausted (in-progress runs finish). Publishing requires an M365 Copilot license, or a Copilot Studio user license with allocated/pooled messages. ([requirements-messages-management](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management))

---

## Part C — The delta and decision guide

### C.1 Capability comparison
| Dimension | Declarative agent (Copilot-hosted) | Copilot Studio full agent (custom engine / autonomous) |
|---|---|---|
| Orchestration | Copilot's, fixed, sequential single grounding+tool step | Generative or classic; multi-step planning, chains topics/tools/agents |
| Iterative loops / multi-step workflows | **No** | Yes |
| Instruction length | 8,000 chars hard | Much larger; logic can live in topics/flows/triggers |
| Deterministic automation | Only via API plugins | **Power Automate / agent flows** (deterministic) |
| Autonomous / proactive / event triggers | **No** (user-initiated only) | **Yes** (event triggers, recurrence) |
| Multi-agent (A2A, child/connected) | No (declarative is individual) | **Yes** |
| Group / shared collaboration | Individual use | **Yes** |
| Channels | M365 apps only (Copilot, Teams, Word, Excel, Outlook) | M365 **plus** web, WhatsApp, Slack, Telegram, SMS, voice, Direct Line, etc. |
| Strict grounding (block general knowledge) | Cannot fully block in Agent Builder | **Yes** ("Allow ungrounded responses" off) |
| Custom model choice | No (Copilot's model) | Yes (BYO model / Foundry) |
| Hosting | None (Microsoft 365) | Copilot Studio (Power Platform env) or external |
| Compliance/security | Inherits M365 | Maker/env responsibility; Power Platform DLP |
| Licensing/cost | M365 Copilot license per user; no separate metering for most capabilities | **Copilot Credits** consumption (prepaid/PAYG); free for M365 Copilot users in B2E |

Sources: [agents-overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-overview), [declarative-agent-architecture](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-architecture), plus the Copilot Studio pages above.

### C.2 Choose a **declarative agent** when
- The workflow lives **inside Microsoft 365** (Copilot chat, Teams @mentions, Word/Excel/Outlook, SharePoint).
- The job is **information retrieval + summarization** over M365/enterprise knowledge, or **single-step** actions via API plugins.
- You want to **inherit M365 security/compliance/RAI** with no hosting and minimal cost overhead.
- Individual/personal productivity is fine (no shared/group agent, no autonomy).
- You can express behavior in ≤8,000 chars and stay within the 50-record / 25-response / 4,096-token / 45-second envelope.

### C.3 Choose a **Copilot Studio full agent** when (any one forces the choice)
- **Autonomous / event-triggered / proactive** behavior is required (declarative agents cannot do this).
- **Complex multi-step / iterative / looped orchestration**, precise business rules, or multiple system integrations.
- **Deterministic automation** via Power Automate / agent flows.
- **Multi-agent** (child/connected/A2A) design or reuse across agents.
- **Group collaboration** or **external channels** (web, WhatsApp, Slack, SMS, voice, custom app).
- **Strict grounding** (must block general-model knowledge) or **Dataverse** as a primary knowledge source.
- Need to **choose the model**, exceed the 8k instruction ceiling, or run custom auth flows.

### C.4 Nuance to keep in the builder's model
Copilot Studio is the superset authoring surface: it can emit a *declarative agent* (Copilot-hosted, same limits as Part A) **or** a full custom/autonomous agent. The decision is therefore less "which product" and more "**does the scenario need capabilities that only the custom-engine/Copilot Studio runtime provides**" — the C.3 list is that trigger set. Microsoft's own decision guidance frames it as declarative-when-inside-Copilot's-orchestration vs. custom-engine-when-you-need-custom-orchestration/models/autonomy/external-reach. ([agents-overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-overview))

---

## Part D — Where docs changed recently or are ambiguous
- **Billing model change:** "messages" → **Copilot Credits** on Sept 1, 2025; rate tables and enforcement (125% overage) are current as of June–July 2026. ([requirements-messages-management](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management))
- **Generative orchestration is now the default**; classic is the legacy path. Several generative-mode features are still gapped (disambiguation, custom entities, official-source marking). ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions))
- **Model auto-migration (GPT 5.0 → 5.1)** changes how declarative-agent instructions are interpreted; expect behavior drift over time. ([declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions))
- **Classic vs. new experience split** in Copilot Studio for both agents and workflows/agent flows — docs straddle both; watch which experience a page describes. ([flows-overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview))
- **Preview surfaces:** connecting to Foundry, Fabric Data, and M365 Agents SDK agents are all **public preview** and subject to change. ([authoring-add-other-agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents))
- **Manifest version churn:** capabilities land at different schema versions (v1.3 → v1.7); current is v1.7. Confirm target version per capability (exact schema is a separate ticket). ([knowledge-sources](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/knowledge-sources))
- **Unofficial/observed limits:** declarative-agent orchestrator reportedly stopping after the 3rd distinct API action in a turn (community Q&A, not documented); and **MCP Apps** interactive-UI in Copilot chat (third-party blog, ~April 2026) — both need official confirmation.

## Key source URLs
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-declarative-agent
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-overview
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-architecture
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/knowledge-sources
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-plugins
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-triggers-about
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management

---

# PART B — What makes an agent good


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
