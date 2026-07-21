# Microsoft Agent Platforms and Agent Quality Reference

This document is a combined reference for building Microsoft agents on two surfaces: **M365 declarative agents** (M365 = Microsoft 365; agents that ride on Microsoft 365 Copilot's own orchestrator and models) and **Copilot Studio agents** (a separate authoring product that can produce either a declarative agent or a full custom-engine / autonomous agent). Part A covers the platform building blocks, hard limits, and the surface-choice delta rule that decides which platform a scenario needs; Part B covers what makes an agent good — instruction writing, knowledge grounding, conversation design, guardrails, evaluation, and a reusable agent skeleton. Consult this document when choosing a build surface for a new agent, when checking a specific platform limit or license requirement, or when authoring or reviewing agent instructions and knowledge.

## Terminology and the two architectures

Microsoft's naming in this space drifts and is a frequent source of confusion. "Agents for Microsoft 365 Copilot" split into two architectures: **declarative agents**, which use Copilot's own orchestrator plus foundation models, and **custom engine agents**, which bring their own orchestrator and models. A **Copilot Studio agent** is a distinct authoring product that can produce *either* a declarative agent *or* a full custom/autonomous agent.

So the practical fork — "M365 declarative agent vs. full Copilot Studio agent" — maps onto the deeper architectural fork: **declarative (Copilot-hosted) vs. custom-engine (Copilot Studio-hosted)**. Keep that mapping in mind throughout; the delta and decision guide below makes it concrete.

---

# Part A — Platform Building Blocks and the Surface Delta

## M365 declarative agents: what they are and how they are built

A declarative agent (DA = declarative agent) customizes Microsoft 365 Copilot by declaring **instructions, knowledge, actions, and capabilities**. It runs on Copilot's shared orchestrator, foundation models, and trusted AI services, and it inherits all Microsoft 365 security, compliance, and Responsible AI (RAI = Responsible AI) controls. No extra hosting is required.

Authoring tools for declarative agents are: **Agent Builder** in Microsoft 365 Copilot (low-code), the **Microsoft 365 Agents Toolkit** (pro-code, for Visual Studio / VS Code), **Copilot Studio**, and **SharePoint agents**.

## The declarativeAgent manifest and its capability objects

The declarative agent manifest is the trusted, versioned, governed source of agent behavior. The current schema is **v1.7**. At a high level the manifest declares:

- **Identity/metadata**: `name`, `description`, icon, `instructions`, `conversation_starters`.
- **`capabilities[]`**: an array of capability/knowledge objects — `WebSearch` (with optional `sites` for scoped search), `CodeInterpreter`, `GraphicArt` (image generator), `OneDriveAndSharePoint`, `Email`, `People` (with `include_related_content` in v1.6+), `TeamsMessages`, `Meetings`, `Dataverse`, and Copilot connectors. Different capabilities were added at different schema versions: scoped web search, Email, Teams, Dataverse, and People at v1.3+; Meetings and People related-content at v1.6+.
- **`actions`**: API plugins (covered under capabilities and actions below).

Microsoft explicitly warns **not** to offload instructions into knowledge sources to dodge the instruction length limit. Knowledge content is untrusted and subject to XPIA (cross-prompt injection attack) sanitization, so it is not honored as trusted agent behavior.

## Declarative agent instructions and the 8,000-character limit

Declarative agent instructions have an **8,000-character hard limit**. Recommended structure is purpose + guidelines + skills: use Markdown headers and lists, make tasks atomic, specify tone / verbosity / output contract, and reference capabilities by name.

**Model auto-upgrade caveat.** Copilot periodically auto-upgrades the underlying GPT model. The **GPT 5.0 to 5.1** move shifted from literal instruction-following to intent-first adaptive reasoning, which can change agent behavior in step-by-step scenarios. Microsoft recommends adding a "literal-execution header" as mitigation. This is an ongoing moving target.

## Declarative agent knowledge sources and per-agent limits (Agent Builder)

In Agent Builder, each declarative agent knowledge source has its own per-agent cap, license requirement, and behavior. The table below lists them for lookup.

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

**Knowledge control gap.** In Agent Builder, the "Only use specified sources" setting only *prioritizes* your sources; it **cannot fully block** general AI knowledge. Microsoft explicitly says to use Copilot Studio if you need strict grounding.

## Declarative agent capabilities and actions (API plugins)

Declarative agents expose built-in capabilities and pluggable actions. **Code interpreter** and the **image generator** require no license, and **web search / scoped web search** requires no license.

**Actions are API plugins** backed by an OpenAPI spec or an **MCP server**. Multiple plugins can run at once. Practical limits:

- **Up to 5 plugins are always injected into the prompt**; beyond 5, semantic matching by description is used.
- A plugin may declare unlimited functions, but response quality degrades past roughly **10 functions**.
- An **undocumented/observed** orchestrator behavior silently stops after the **3rd distinct API action** in a turn (this comes from community Q&A, not official documentation).

## Declarative agent architecture: the hard constraints that define the ceiling

Declarative agents use a **sequential grounding-then-tool-call pipeline** that Microsoft controls; developers control only instructions, knowledge, and plugins. Because grounding and external tool calls happen sequentially, **you cannot do chained operations over grounding data or looped/iterative operation plans** — Microsoft states declarative agents are "not suitable for complex multistep operations."

## Declarative agent technical limits (optimize to about 66% of each)

The declarative agent runtime enforces the fixed limits below across grounding, plugin responses, tokens, and time. Microsoft's guidance is to design to roughly 66% of each value.

| Limit | Value |
|---|---|
| Grounding record limit | **50 items** |
| Plugin response limit | **25 items** |
| Token limit | **4,096** (all context + response) |
| Timeout | **45 seconds** |

## What declarative agents cannot do

Beyond the numeric limits, declarative agents have architectural limitations. There is no control of iterative reasoning loops or orchestration; no custom corpus (except Copilot Tuning); processing is sequential; and dynamic / non-OpenAPI web content grounds poorly. Declarative agents are **not** suitable for complex decision trees, large-data or full-document processing, custom models, or reliable recency from dynamic sites.

Declarative agents are also **individual-use** and **user-initiated only** — there is **no proactive/autonomous behavior** — and they run in **Microsoft 365 channels only** (Copilot, Teams, Word, Excel, Outlook).

**Needs official confirmation.** Third-party sources report **MCP Apps** (interactive UI rendered inside Copilot chat) shipping around April 2026, plus an Agents Toolkit CLI / natural-language scaffolding plugin. These are not yet corroborated in the core Microsoft Learn pages; treat as needing official confirmation.

---

## Copilot Studio agents: building blocks

A Copilot Studio agent is assembled from **topics**, **tools/actions**, **knowledge**, and **other agents**, under one of two orchestration modes (generative or classic).

## Copilot Studio generative vs. classic orchestration

In Copilot Studio, **generative orchestration is now the default** for new agents. Generative orchestration adds an LLM planning layer that interprets intent, decomposes multi-intent queries, and picks the best combination of topics, tools, knowledge, and other agents; it can also respond autonomously to event triggers. **Classic orchestration** matches user query to topic trigger phrases, selects a single topic, and uses knowledge only as a fallback; tools and knowledge are called explicitly from topics.

Selection is driven by the **name + description** of each topic/tool/agent/knowledge source, so description quality is the main authoring lever. Known generative-mode limitations: no Conversational-boosting customization, no custom-entity input parameters, no auto-disambiguation (the "Multiple Topics Matched" flow is not called), a limited conversation-history window, and "official source" marking is incompatible with generative mode.

## Copilot Studio knowledge sources and limits

In Copilot Studio, knowledge source caps differ between generative and classic orchestration, and each source has its own authentication requirement. The table below is for lookup.

| Source | Generative mode | Classic mode | Auth |
|---|---|---|---|
| Public website (Bing) | **25** websites | 4 URLs | None |
| Documents (uploaded to Dataverse) | All | Limited by Dataverse storage | None |
| SharePoint | **25** URLs | 4 per generative-answers node | Agent user Entra ID |
| Dataverse | **Unlimited** | 2 sources × up to 15 tables | Agent user Entra ID |
| Enterprise data via Copilot connectors | **Unlimited** | 2 per agent | Agent user Entra ID |

In Copilot Studio generative orchestration, an internal GPT model filters sources when there are more than 25 sources (uploaded files are exempt from that 25 cap). Generative mode does not support Custom Data / Bing Custom Search / Azure OpenAI as agent-level knowledge — those must be embedded in a generative-answers node. **Web Search** uses Grounding with Bing.

**Tenant graph grounding with semantic search** is optional, carries extra cost, and requires Authenticate-with-Microsoft plus a Copilot license in the tenant; it raises quality and supports SharePoint/connector files up to 512 MB. The **Allow ungrounded responses** setting can be turned off to force tool/knowledge-grounded answers — this is the strict grounding control that Agent Builder lacks.

## Copilot Studio Power Automate flows and agent flows

In Copilot Studio, **agent flows** are deterministic, rule-based automations built in Copilot Studio (or converted from a Power Automate cloud flow — a **one-way** conversion that switches billing to Copilot Credits). Flows using the **"When an agent calls the flow"** trigger can be added as **tools**. Action types include connectors (Microsoft 365, third-party, custom), AI capabilities (LLM prompts, call-an-agent), human-in-the-loop (approvals), and control structures (loops/branches/child flows). Every executed action consumes capacity. The documentation distinguishes a **classic vs. new** workflow experience; agent flows are the classic experience.

## Copilot Studio connectors, actions, and tools

In Copilot Studio, tools include prebuilt/custom **connectors**, agent flows, prompts, and MCP-style tools. In generative mode, the agent chooses among them by their description, so description quality directly controls tool selection.

## Copilot Studio autonomous and event triggers

Autonomous behavior in Copilot Studio **requires generative orchestration**. An event — a Dataverse row added/modified/deleted, a SharePoint item created, a OneDrive file created, a Planner task completed, a **Recurrence**, and similar — delivers a **trigger payload** (JSON/text plus author instructions) to the agent via a connector; the agent then selects actions/topics per its instructions. Key constraints:

- **Maker credentials only** — all authenticated triggers/actions run as the author's identity, which is a data-exposure risk; makers are warned before publishing.
- Requires **solution-aware cloud flow sharing** enabled in the environment; admins can block event triggers via DLP (data loss prevention) data policies.
- Each trigger payload is a **billed** message; frequent or recurrence triggers can hit quota throttling. Keep to **fewer than 15 consecutive actions/topics** for reliability.

## Copilot Studio agent-to-agent and multi-agent options

In Copilot Studio, multi-agent designs use **child agents** (lightweight, in-agent), **connected agents** (other Copilot Studio agents in the same environment), and external agents via the **A2A (agent-to-agent) protocol**, **Microsoft Foundry agents (preview)**, **Fabric Data agents (preview)**, and **Microsoft 365 Agents SDK agents (preview)**.

Rule of thumb: split into connected agents when a single agent exceeds roughly **30–40** tool/topic/agent choices, or when teams, lifecycle, or settings must be independent. Trade-offs: added latency per orchestration hop; a larger test and governance surface; an agent used as a main agent with connected agents cannot itself be a connected agent elsewhere; and Fabric Data agents cannot be redirected-to from topics and do not work when the main agent is deployed to Microsoft 365 Copilot.

## Copilot Studio channels

A Copilot Studio agent is published once, and publishing applies to all channels: **Microsoft Teams + Microsoft 365 Copilot**, **SharePoint**, **WhatsApp**, **custom website / demo website**, **mobile app**, **Facebook**, and **Azure Bot Service channels** (Slack, Telegram, Twilio/SMS, Line, Kik, GroupMe, Direct Line Speech, Email, Cortana). Voice/telephony tiers also exist (Classic Voice, GenAI Voice, Premium GenAI Voice).

## Copilot Studio authentication modes

Copilot Studio offers three authentication modes: **Authenticate with Microsoft** (Entra ID, the default; automatic for Teams / Power Apps / Microsoft 365 Copilot), **No authentication** (anyone with the link, but then tools cannot use user credentials), and **Authenticate manually**. Tenant-graph semantic search requires Authenticate-with-Microsoft.

## Copilot Studio environment, licensing, and consumption constraints

Copilot Studio billing and capacity work as follows:

- **Copilot Credits** are the billing unit (they replaced "messages" on **Sept 1, 2025**). Capacity is either **prepaid packs pooled across the tenant** and/or **pay-as-you-go** (PAYG, via an Azure meter). Unused credits do not roll over.
- **Microsoft 365 Copilot-licensed users incur no charge** for core B2E (business-to-employee) agent usage, and for agent flows only via the "When an agent calls the flow" trigger; unlicensed users consume tenant credits. Computer-Using Agents are **not** covered by the Microsoft 365 Copilot license.
- **Overage enforcement at 125% of prepaid capacity disables custom agents**; agent-flow enforcement blocks new flow runs when prepaid capacity is exhausted (in-progress runs finish). Publishing requires a Microsoft 365 Copilot license, or a Copilot Studio user license with allocated/pooled messages.

## Copilot Studio Copilot Credits billing rates

The Copilot Credit consumption rates below apply per the indicated unit.

| Action | Copilot Credit rate |
|---|---|
| Classic answer | 1 |
| Generative answer | 2 |
| Agent action | 5 |
| Tenant graph grounding | 10 |
| Agent flow | 13 per 100 actions |
| AI tools — basic | 1 (per 10 responses) |
| AI tools — standard | 15 (per 10 responses) |
| AI tools — premium | 100 (per 10 responses) |

Reasoning models add the premium token meter on top of the feature rate.

---

## The delta: declarative agent vs. Copilot Studio full agent

This section compares the two build surfaces so you can pick one. The comparison is between a **declarative agent (Copilot-hosted)** and a **Copilot Studio full agent (custom engine / autonomous)**. Because it is wide, it is split into two tables — orchestration and capability, then reach and operations.

### Comparison: orchestration and capability

| Dimension | Declarative agent (Copilot-hosted) | Copilot Studio full agent |
|---|---|---|
| Orchestration | Copilot's, fixed, sequential single grounding+tool step | Generative or classic; multi-step planning, chains topics/tools/agents |
| Iterative loops / multi-step workflows | **No** | Yes |
| Instruction length | 8,000 chars hard | Much larger; logic can live in topics/flows/triggers |
| Deterministic automation | Only via API plugins | **Power Automate / agent flows** (deterministic) |
| Strict grounding (block general knowledge) | Cannot fully block in Agent Builder | **Yes** ("Allow ungrounded responses" off) |
| Custom model choice | No (Copilot's model) | Yes (BYO model / Foundry) |

### Comparison: reach, hosting, and operations

| Dimension | Declarative agent (Copilot-hosted) | Copilot Studio full agent |
|---|---|---|
| Autonomous / proactive / event triggers | **No** (user-initiated only) | **Yes** (event triggers, recurrence) |
| Multi-agent (A2A, child/connected) | No (declarative is individual) | **Yes** |
| Group / shared collaboration | Individual use | **Yes** |
| Channels | M365 apps only (Copilot, Teams, Word, Excel, Outlook) | M365 **plus** web, WhatsApp, Slack, Telegram, SMS, voice, Direct Line, etc. |
| Hosting | None (Microsoft 365) | Copilot Studio (Power Platform env) or external |
| Compliance/security | Inherits M365 | Maker/env responsibility; Power Platform DLP |
| Licensing/cost | M365 Copilot license per user; no separate metering for most capabilities | **Copilot Credits** consumption (prepaid/PAYG); free for M365 Copilot users in B2E |

## When to choose a declarative agent

Choose a declarative agent when all of the following hold:

- The workflow lives **inside Microsoft 365** (Copilot chat, Teams @mentions, Word/Excel/Outlook, SharePoint).
- The job is **information retrieval + summarization** over Microsoft 365 / enterprise knowledge, or **single-step** actions via API plugins.
- You want to **inherit Microsoft 365 security/compliance/RAI** with no hosting and minimal cost overhead.
- Individual/personal productivity is acceptable (no shared/group agent, no autonomy).
- You can express behavior in 8,000 characters or fewer and stay within the 50-record / 25-response / 4,096-token / 45-second envelope.

## When to choose a Copilot Studio full agent

Choose a Copilot Studio full agent when **any one** of the following forces the choice:

- **Autonomous / event-triggered / proactive** behavior is required (declarative agents cannot do this).
- **Complex multi-step / iterative / looped orchestration**, precise business rules, or multiple system integrations are needed.
- **Deterministic automation** via Power Automate / agent flows is needed.
- A **multi-agent** (child/connected/A2A) design or reuse across agents is needed.
- **Group collaboration** or **external channels** (web, WhatsApp, Slack, SMS, voice, custom app) are needed.
- **Strict grounding** (must block general-model knowledge) or **Dataverse** as a primary knowledge source is needed.
- You need to **choose the model**, exceed the 8,000-character instruction ceiling, or run custom auth flows.

## The build-surface decision framed correctly

Copilot Studio is the superset authoring surface: it can emit a *declarative agent* (Copilot-hosted, same limits as the declarative sections above) **or** a full custom/autonomous agent. The decision is therefore less "which product" and more "**does the scenario need capabilities that only the custom-engine / Copilot Studio runtime provides**" — the "when to choose a Copilot Studio full agent" list is that trigger set. Microsoft's own guidance frames it as declarative-when-inside-Copilot's-orchestration vs. custom-engine-when-you-need-custom-orchestration, models, autonomy, or external reach.

---

## Where the platform docs changed recently or are ambiguous

The following areas were changing or ambiguous as of mid-2026 and should be re-verified:

- **Billing model change:** "messages" became **Copilot Credits** on Sept 1, 2025; the rate tables and enforcement (125% overage) are current as of June–July 2026.
- **Generative orchestration is now the default**; classic is the legacy path. Several generative-mode features are still gapped (disambiguation, custom entities, official-source marking).
- **Model auto-migration (GPT 5.0 to 5.1)** changes how declarative-agent instructions are interpreted; expect behavior drift over time.
- **Classic vs. new experience split** exists in Copilot Studio for both agents and workflows/agent flows — docs straddle both, so watch which experience a page describes.
- **Preview surfaces:** connecting to Foundry, Fabric Data, and Microsoft 365 Agents SDK agents are all **public preview** and subject to change.
- **Manifest version churn:** capabilities land at different schema versions (v1.3 through v1.7); current is v1.7. Confirm the target version per capability.
- **Unofficial/observed limits:** the declarative-agent orchestrator reportedly stops after the 3rd distinct API action in a turn (community Q&A, not documented), and **MCP Apps** interactive UI in Copilot chat (third-party blog, around April 2026) — both need official confirmation.

---

# Part B — What Makes an Agent Good

The principles that separate a good Microsoft agent (M365 declarative and Copilot Studio) from a mediocre one are largely shared across both surfaces: clear role/goal, tight scope grounded in configured resources, explicit rules/tone/format, guardrails, examples, and iterative evaluation. The surfaces differ mainly in *mechanics* (character limit, orchestration model, where fallback and citations are controlled), not in *principles*.

## The two surfaces at a glance

The table below contrasts the runtime, instruction limit, and building blocks of the two surfaces so best practices below can be mapped onto each.

| Aspect | M365 declarative agent (Agent Builder / Agents Toolkit) | Copilot Studio agent |
|---|---|---|
| Runtime | Rides on Microsoft 365 Copilot's GPT model (auto-upgraded, e.g. GPT 5.0 to 5.1) | Own agent with selectable **orchestration**: classic (NLU, topic-based) or **generative** (LLM reasons over instructions/tools/knowledge) |
| Instruction limit | **8,000 characters** | Free-text instructions on the Overview page; grounded in configured resources |
| Building blocks | Name, Description (≤1,000 chars), Instructions (≤8,000), Knowledge sources, Capabilities, Actions/plugins, Conversation starters (min 3) | Instructions, Knowledge sources, Tools, Topics, Triggers, other Agents, Variables, Power Fx |

NLU here means natural language understanding. The **core discipline is the same on both surfaces**; only the mechanics differ.

---

## Instruction writing: Microsoft's named components (M365 declarative)

For M365 declarative agents, Microsoft names the **primary instruction components** as:

- **Purpose**
- **General guidelines** — general directions, **tone**, and **restrictions**
- **Skills**

Include **when relevant**: step-by-step instructions, error handling and limitations, feedback and iteration, interaction examples, nonstandard terms, and follow-up and closing.

Microsoft's own **example instruction set** uses these Markdown headers, which acts as a reference skeleton:
`# OBJECTIVE` then `# RESPONSE RULES` then `# WORKFLOW` (each step = **Goal / Action / Transition**) then `# OUTPUT FORMATTING RULES` then `# EXAMPLES` (Valid + Invalid).

## Instruction writing: Copilot Studio's three elements

For Copilot Studio generative orchestration, conversational instructions are framed as three combined elements:

- **Constraints** — what the agent may respond to, and its scope.
- **Response format** — structure, tables, formatting.
- **Guidance** — hints, for example which folder or source to search.

## Instruction writing: rules that separate good from mediocre

These best-practice rules apply to instruction writing on both surfaces:

- **Say what to DO, not what to avoid.** Use precise verbs — *ask, search, send, check, use* (M365). The Copilot Studio verb table covers conditions (*when, if, ensure, compare*), filters (*from, include, exclude*), data (*retrieve, get, analyze, extract*), and tools (*notify, direct, ask, assign*).
- **Strict structure signals intent:** use *sections* for logical grouping (no implied order), *bullets* for parallel independent tasks (avoid numbering that implies sequence), and *steps* only for true sequential workflows.
- **Make tasks atomic** — split "extract metrics and summarize" into separate steps to stop the model merging or reinterpreting them.
- **Every step = Goal + Action + Transition** (its purpose, what to do / which tool, and the criteria to move on or end).
- **Always specify tone, verbosity, and output format.** If unspecified, the model infers them, causing inconsistency across model versions. Use an **Output Contract** (goal, format, detail level, tone, include/exclude, example shape).
- **Write in Markdown:** `#`/`##`/`###` headers, `-` lists, `` `backticks` `` for tool/system names (e.g. `Jira`, `ServiceNow`), and `**bold**` for critical rules.
- **Explicitly reference capabilities/knowledge/actions** at each step (e.g. "Use `ServiceNow KB` for help articles"; "Use code interpreter to generate charts").
- **Provide domain vocabulary** — define acronyms, formulas, and org-specific terms to prevent wrong inference.
- **Use few-shot examples** for complex scenarios (more than one example to cover edge cases); skip examples for simple ones to save tokens.
- **Add a final self-evaluation / self-check gate** (e.g. "Before finalizing, confirm all Section A items appear in the summary").
- **Control reasoning depth via phrasing** — reasoning verbs plus "think step by step" for deep reasoning; "short answer only, no explanation" for fast responses (this works with GPT-5 auto-routing).

## Instruction writing: the length vs. specificity trade-off (M365)

For M365 declarative agents, the instruction budget is **8,000 characters**. Do **not** offload instructions into a SharePoint doc to dodge the limit — knowledge content is untrusted, subject to XPIA (cross-prompt injection attack) sanitization, and not honored as system instructions (an explicit Microsoft warning).

- **Specific beats long.** Watch for failure modes: over-eager tool use (add "only call the tool if inputs are available, else ask"); repetitive verbatim phrasing (vary wording or add few-shot examples); verbose output (add concise constraints).
- **Model-drift resilience.** M365 auto-upgrades models; GPT 5.0 to 5.1 shifted from literal to intent-first reasoning. If you see step reordering or added steps, apply a **literal-execution header** ("Always interpret instructions literally. Never infer intent or fill missing steps... Do not call tools unless a step instructs it.") as an interim stabilizer.

## Instruction writing: Copilot Studio specifics

For Copilot Studio agents:

- Reference resources inline with `/` (tool, topic, agent, variable, Power Fx); use the **exact** tool name.
- Be explicit about tool **sequence** when there are more than 5 tools; be explicit about which knowledge doc to use when there are many.
- **Do not** write instructions that alter citation format or behavior (words like "citation" or "reference") — this can make the orchestrator treat responses as ungrounded and discard them.
- Instructions **cannot** override system behaviors: the fallback message (edit the Fallback **topic**), Adaptive Card triggers, or search-retrieval logic. Use instructions for *summarization and conversational flow*, not system-level behavior.

---

## Knowledge grounding: relevance, scope, and freshness

Good knowledge grounding is about relevance, not volume, on both surfaces:

- **Relevance over quantity — "less is more."** Add only the sources needed for expected questions; Copilot performs best with reasonably sized, focused documents. Over-broad sources add noise.
- **Scope tightly:** specific Teams channels/threads over "all my chats"; specific SharePoint sites/folders. In generative orchestration, an internal GPT model filters sources when there are more than **25**; uploaded files do not count toward that limit.
- **Right source for the data:** SharePoint/connectors for static or structured knowledge; a Copilot connector or API plugin for CRM/database records.
- **Freshness and maintenance:** the agent answers *from* source content, so keep it up to date and periodically refresh and review it.
- **Permissions and licensing:** the agent only retrieves content the *user* can access (per-user Entra ID auth); some knowledge features need a Copilot license, so shared agents degrade for unlicensed users.

## Knowledge grounding: reducing hallucination

To reduce hallucination in grounded answers:

- **Test with and without knowledge.** If the agent invents answers absent the doc but finds them once added, grounding works; if it over-uses a source, remove it or scope instructions.
- **Copilot Studio "Allow ungrounded responses" setting:** OFF = the agent blocks any turn that did not call a knowledge source or tool (fallback fires instead); ON = model general knowledge is allowed. Caveat: OFF does not *guarantee* zero general knowledge — the model may still blend it with retrieved content. Also, turning it OFF disables follow-up/clarifying questions, which are treated as ungrounded.
- **Official/authoritative sources:** mark a trusted source "Official" so the agent uses it without verification (classic orchestration only; not compatible with generative).
- **Tenant graph grounding with semantic search** improves SharePoint retrieval precision and volume (needs Authenticate with Microsoft).
- **Citations are system-controlled** — do not try to reshape them.
- **Freshness / real-time:** "Use information from the web" / Web Search (Grounding with Bing) interleaves live web results with your public-site sources.

## Knowledge vs. actions, and the Retrieval API

Knowledge and actions play different roles. Knowledge is for *grounding factual answers* (read / RAG = retrieval-augmented generation); actions and tools are for *doing things, querying external systems, and transactions*. Mark any create/update/delete action `isConsequential: true`; read-only queries can be nonconsequential.

For custom-engine agents, the **Microsoft 365 Copilot Retrieval API** does RAG over SharePoint/OneDrive/connectors in place (no re-indexing), scoped via a KQL `filterExpression` — validate that expression, because bad syntax silently runs *unscoped* — and it honors least-privilege permissions.

---

## Conversation and orchestration: classic vs. generative (Copilot Studio)

When designing conversation flow in Copilot Studio, the orchestration choice sets the trade-off between control and flexibility:

- **Classic** = an NLU model selects one manually-authored topic per turn via trigger phrases; more **predictable, controllable, cost-effective**; supports custom data sources / Bing Custom Search directly.
- **Generative** (default for new agents) = an LLM reasons over instructions + tools + knowledge, can **chain** multiple topics/tools/knowledge, act autonomously, and ask context-aware follow-ups; more natural but less deterministic. It does not support custom data / Bing Custom Search unless embedded in a generative-answers node.
- **Guidance:** use **generative** for open, multi-step, natural conversation; use **classic** (or author explicit topics) where you need a guaranteed, controlled response.

## Conversation design: disambiguation, follow-ups, and failure handling

Good conversation design handles missing info and failure gracefully:

- **Disambiguation and missing info:** ask **one focused clarifying question at a time, only when needed**; do not overwhelm with options; use conversation history to fill tool inputs and only ask the user for what is still missing.
- **Follow-up questions (generative):** reference tools/knowledge/variables in instructions so the agent asks the *right* next question and suggests the next logical step. This shifts effort from authoring every branch to guiding reasoning (fewer brittle hard-coded flows). Note: this requires Allow ungrounded responses ON.
- **Graceful failure / handoff:** provide explicit fallback behavior. In Copilot Studio the **default fallback** ("I'm sorry, I'm not sure how to help with that. Can you try rephrasing?") is edited via the **Fallback system topic**, not instructions. Route forbidden or out-of-scope requests to human support (e.g. "Consult HR"). For highly specific canned responses, author a dedicated **topic** rather than relying on instructions.
- **Autonomous/triggered flows:** define trigger payloads (e.g. "Onboard the following employee: ..."); keep payloads small via variables; protect triggers against jailbreak injection by limiting which tools/parameters the agent may use from trigger content.
- **Confirmation loops:** always confirm before consequential steps (submitting tickets, sending email); test both the Allow and Cancel/Deny paths.

---

## Guardrails and safety: staying in scope

The primary in-scope / out-of-scope guardrail on both surfaces is an explicit scope instruction, for example: "Only respond to messages relevant to Contoso and ordering coffee. Otherwise, tell the user you can't help."

## Guardrails and safety: moderation, permissions, and injection defense

Additional safety controls span moderation, least-privilege data access, and injection defense:

- **Content moderation (Copilot Studio):** enforced on all generative requests. Configurable **Lowest to Highest** at agent / topic / prompt level (topic overrides agent); the **default is High**. Higher = fewer answers and stricter harmful-content filtering; lower = more answers and more risk. Blocked-query counts are visible in the Power Platform admin center. If moderation over-blocks legitimate behavior, update instructions to state that the behavior is expected.
- **Auth-gated data:** knowledge honors per-user Entra ID permissions (the agent only surfaces what the user can access); grant apps least privilege (e.g. Retrieval API: `Files.Read.All`, `Sites.Read.All`, `ExternalItem.Read.All`).
- **Injection / jailbreak defense:** do not offload instructions into knowledge sources (XPIA risk); constrain tool use and parameters when acting on trigger or knowledge content (e.g. "only email a specified list of individuals," "only email after checking a knowledge source").
- **Responsible AI validation:** M365 agents pass RAI validation at publish; expect behavioral change across automatic model upgrades and re-test.

---

## Evaluation: iterate from day one

Treat evaluation as continuous, from envisioning through deployment and regression detection: create, then publish and pass RAI, then test, then iterate.

- **Built-in test chat:** use it frequently; run every conversation starter / sample prompt **plus** edge, long, and irrelevant questions; test across apps (Word/Teams/Outlook behave differently); test confirmation Allow/Deny flows; peer/user testing surfaces unexpected phrasings and missing conversation starters.
- **Spot-check groundedness:** verify summaries and citations against source material; ensure factual queries prefer knowledge sources.

## Evaluation: structured test sets and the four-stage lifecycle

The Copilot Studio Evaluate tab supports structured evaluation. A **test set** is up to 100 test cases; a **test case** is a prompt + optional expected response (assertion) + acceptance criteria + test method. **General quality** uses an LLM judge to score how well the agent answers.

The evaluation checklist defines a **four-stage lifecycle**:

1. Build a foundational test set for core scenarios.
2. Establish a baseline pass rate plus root-cause analysis (distinguish a test-case issue from an agent-design issue).
3. Systematically expand across quality categories — **Foundational core, Robustness, Architecture (tool/knowledge/routing/handoff), Edge cases (out-of-scope, guardrails)**.
4. Run continuous evaluation ops, triggered by a model change, knowledge update, new tool, or production incident.

## Evaluation: metrics and adversarial testing

For scoring and safety verification:

- **Metrics:** run each set multiple times (outputs are probabilistic) and average; **aim for an 80–90% pass rate**. Category signal: a core failure means broken; a robustness failure means too strict; an architecture failure means a component/workflow bug; an edge-case failure means weak guardrails.
- **Adversarial "Always Fail" test set** verifies that safety guardrails hold. Production analytics (generated-answer rate and quality, knowledge-source use, blocked queries) close the loop.

---

## The invariant agent skeleton

Every good Microsoft agent shares an invariant structure, synthesized from the M365 declarative instruction components, the Copilot Studio Constraints/Response format/Guidance model, and the best practices above. Elements marked **[core]** appear in essentially every good agent; **[conditional]** elements appear when the scenario warrants.

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
12. **Conversation starters / sample prompts** *[core, agent-level]* — minimum 3, reflecting core capabilities (metadata, not instruction body).
13. **Error handling & follow-up/closing** *[conditional]* — missing-data behavior, follow-up questions, closing.

## Mapping the skeleton onto each surface

Each skeleton element realizes differently on M365 declarative agents vs. Copilot Studio. The table below is the mapping.

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

## Representing an agent specification: three forms and when to use each

An agent specification that must serve both surfaces has to bridge two very different outputs: a clean `declarativeAgent.json` file (M365, fully file-based) and **click-by-click portal steps** (Copilot Studio, which has no clean import for runtime wiring). Three candidate representation forms trade off differently:

- **Markdown instruction template only** — a prose template with headers (`# OBJECTIVE` / `# RESPONSE RULES` / `# WORKFLOW` / `# GUARDRAILS` / `# EXAMPLES`, Microsoft's proven header pattern). It is lightest to author, most readable for non-technical makers, and looks like the finished instruction box. **Weakness:** name, description, knowledge, capabilities, actions, and conversation-starters live **outside** the instruction text — they are manifest/config fields (JSON fields for M365, portal steps for Copilot Studio) and have **no clean home** in a prose template, so a second structure must be bolted on. **Best when** the agent is essentially just an instruction prompt with no meaningful config.
- **Pure structured schema** — everything, including the instruction body, decomposed into discrete typed fields (`role`, `purpose`, `rules[]`, `workflowSteps[{goal, action, transition}]`, `guardrails[]`, ...), with the final instruction text assembled from the fields. **Best for** machine manipulation, validation, recombination at scale, and tooling-driven generation. **Weakness:** (a) Microsoft guidance recommends instructions be **well-crafted free-text Markdown with deliberate structure** — decomposing and reassembling risks losing that shape and human nuance; (b) it is the **heaviest** form for a mixed / non-technical audience.
- **Hybrid structured spec** — a **structured envelope for the config** (name, description, knowledge, capabilities, actions, conversation starters — mapping 1:1 to manifest fields) **plus one `instructions` field** holding the free-text Markdown body in Microsoft's proven header pattern. The config half renders into `declarativeAgent.json` fields or Copilot Studio portal steps; the instruction half drops into the instruction box unchanged. It is a **single source of truth for both surfaces**, with slightly more structure than a plain template and far less than full decomposition.

**Decision rule:**

- Simplest prose-only agents → **Markdown template**.
- Machine-generating / validating at scale → **pure schema**.
- Helping a **human build a complete agent for two surfaces from one conversation** → **hybrid** (the recommended default for that case).

---

## Sources

- Declarative Agents overview — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-declarative-agent
- Agents overview — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-overview
- Declarative agent architecture — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-architecture
- Write effective instructions for declarative agents — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions
- Best practices for building declarative agents — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-best-practices
- Knowledge sources — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/knowledge-sources
- Add knowledge in Agent Builder — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge
- Overview of plugins — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-plugins
- Microsoft 365 Copilot Retrieval API overview — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview
- Orchestrate agent behavior with generative AI — https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions
- Knowledge sources summary (Copilot Studio) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- About triggers (autonomous agents) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-triggers-about
- Flows overview — https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview
- Advanced flow guidance — https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-flow
- Add other agents — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents
- Publish and channels fundamentals — https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
- Requirements and messages management (billing/licensing) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management
- Write agent instructions (Copilot Studio) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions
- Configure high-quality instructions for generative orchestration — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance
- Review the agent evaluation checklist — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-checklist
- Create a single response test set — https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-create
- Choose evaluation methods — https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview
- Resolve responsible AI content filter errors — https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai
- Practitioner: Forward Forever — Orchestration: Classic or Generative — https://forwardforever.com/orchestration-in-copilot-studio-classic-or-generative-ai/
- Practitioner: reshmeeauckloo — GenAI vs Classic orchestration — https://reshmeeauckloo.com/posts/copilotstudio-genai-versus-classic/
- Practitioner: Voitanos — Declarative agents what's new (April 2026) — https://www.voitanos.io/blog/microsoft-365-copilot-declarative-agents-whats-new-202604-april-2026/
