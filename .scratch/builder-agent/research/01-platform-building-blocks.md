# 01 · Platform building blocks & the M365-vs-Copilot-Studio delta

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
