# 01 · Platform building blocks & the M365-vs-Copilot-Studio delta

Type: research
Status: resolved
Blocked by: none

## Question

What are the current (2026) building blocks, capabilities, and hard limits of the two target surfaces, and what is the delta between them?

Resolve, grounded in current Microsoft Learn documentation:

- **M365 declarative agents** ("agents in Microsoft 365 Copilot" / Copilot Studio agent builder / Teams Toolkit declarative agents): what an author can configure — instructions, knowledge sources (SharePoint, Graph connectors, web, files), capabilities (web search, code interpreter, image gen), actions (API plugins / Graph), and the constraints (instruction length limits, knowledge source types/counts, no custom orchestration/flows).
- **Copilot Studio agents**: topics, generative vs. classic orchestration, knowledge sources, Power Automate flows, connectors/actions, autonomous triggers, agent-to-agent, channels, authentication, environment/licensing constraints.
- **The delta**: a clear decision guide — when a maker should choose a declarative agent vs. a full Copilot Studio agent, and what capabilities force the choice.

Capture findings to `.scratch/builder-agent/research/01-platform-building-blocks.md` with source links, and note where the platforms have changed recently or where docs are ambiguous.

## Answer

- **Two architectures, not two products.** "Agents for M365 Copilot" fork into **declarative agents** (run on Copilot's own orchestrator/models) and **custom engine agents** (bring-your-own orchestration). Copilot Studio is the superset authoring surface that can emit *either*. The real decision is declarative (Copilot-hosted) vs. custom/autonomous (Copilot Studio runtime).
- **Declarative agents = configuration inside a fixed pipeline.** Author instructions (**8,000-char hard limit**), knowledge (Agent Builder: ≤4 web URLs, ≤100 SharePoint items +1 list, ≤50 OneDrive files, ≤5 Teams URLs, ≤20 uploaded files, Copilot connectors), capabilities (code interpreter, image gen, web search — all no-license), and actions (API plugins / MCP; ~5 injected then semantic-matched). Everything inherits M365 security/compliance.
- **Declarative hard ceiling:** sequential single grounding+tool step — **no chained/looped/iterative operations, no custom orchestration**; limits of **50 grounding records, 25 plugin-response items, 4,096 tokens, 45s**; **no autonomy/proactivity**, individual-use, **M365 channels only**; and Agent Builder can't fully block general-model knowledge.
- **Copilot Studio agents = full orchestration.** Generative (now default) vs. classic orchestration; topics/tools/knowledge/other-agents; larger knowledge limits (25 web/SharePoint, unlimited Dataverse/connectors in generative); **Power Automate / agent flows** for deterministic automation; **strict grounding** via "Allow ungrounded responses" off.
- **Copilot Studio unlocks the capabilities declarative agents lack:** **autonomous/event triggers** (Dataverse/SharePoint/recurrence, maker-credential only), **multi-agent** (child/connected/A2A + preview Foundry/Fabric/M365 SDK), **group collaboration**, and **many external channels** (web, WhatsApp, Slack, SMS, voice).
- **Licensing delta:** declarative = M365 Copilot license per user, little extra metering. Copilot Studio = **Copilot Credits** (replaced "messages" Sept 2025; prepaid pooled + PAYG; classic answer 1 / generative 2 / agent action 5 / tenant-graph 10 credits; **125% overage disables agents**); M365 Copilot-licensed B2E users are no-charge.
- **Decision rule:** choose declarative when the scenario is in-M365, retrieval/single-step, individual, and fits the 8k/limits envelope. **Any** of {autonomy, multi-step/looped orchestration, deterministic flows, multi-agent, external channels, group use, strict grounding, custom model, Dataverse-primary} forces a full Copilot Studio agent.
- **Recent/ambiguous:** messages→Credits (2025); generative orchestration default; GPT 5.0→5.1 changes instruction interpretation; classic-vs-new experience split; Foundry/Fabric/M365-SDK connections are preview; manifest v1.7 with capabilities added across v1.3–1.7; unofficial reports (3-API-action stop, April 2026 MCP Apps) need confirmation.

Full findings with citations: [`.scratch/builder-agent/research/01-platform-building-blocks.md`](../research/01-platform-building-blocks.md)
