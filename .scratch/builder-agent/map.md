# Wayfinder Map: Builder Agent

`wayfinder:map` · effort slug: `builder-agent` · **STATUS: CLOSED (2026-07-14)** — destination reached, all 7 tickets resolved.

> Build-ready package delivered. Assemble the Agent Builder per [`builder-spec/builder-agent-spec.md`](builder-spec/builder-agent-spec.md) §5.

## Destination

A **build-ready package** that can be assembled into a working "builder agent" inside Copilot Studio — an agent that converses with a maker and hands them ready-to-paste artifacts to create their own M365 declarative agent **or** Copilot Studio agent. The package consists of:

1. A **deep-research knowledge base** on what makes M365 declarative agents and Copilot Studio agents good, grounded in current (2026) Microsoft documentation.
2. A **two-layer template library**: a base skeleton (the invariant structure of a good agent) + use-case archetypes built on it.
3. A **full specification of the builder agent itself** — system instructions, knowledge sources, conversation design (skill-level detection, quick vs. guided paths), and tool/flow list — such that it emits ready-to-paste artifacts (final instructions, knowledge list, topic/flow design, action config, and a `declarativeAgent.json` for the M365 case).

Scope covers **both** target agent types at full depth. All deliverables live as markdown/JSON files in this repo. This is a planning + assets effort: no live-tenant provisioning.

## Notes

- **Domain**: Microsoft agent-building — M365 declarative agents ("agents in Microsoft 365 Copilot") and Copilot Studio agents (topics, Power Automate flows, connectors, autonomous triggers, generative orchestration).
- **End user of the builder agent**: mixed audience (non-technical makers + technical builders); the builder detects skill level and offers quick vs. guided paths.
- **Output fidelity**: ready-to-paste artifacts, minimal end-user thinking.
- **Skills every session should consult**: `/grilling` + `/domain-modeling` for decisions; `/research` (mattpocock) for research tickets; `/prototype` for conversation-design and archetype tickets.
- **Standing preference**: research must be grounded in current official Microsoft Learn documentation (web-sourced), not model memory, because these platforms change fast.
- Research findings are captured under `.scratch/builder-agent/research/`; each research ticket points at its findings file.

## Decisions so far

<!-- one line per closed ticket: gist of the answer + link -->

- [01 · Platform building blocks & delta](issues/01-platform-building-blocks.md) — **declarative agents** = Copilot's fixed orchestrator (instructions ≤8,000 chars, single grounding + tool-call, no looped/multi-step orchestration; limits 50 grounding / 25 plugins / 45s; individual-use, M365 channels only). **Copilot Studio agents** add generative-vs-classic orchestration, Power Automate/agent flows, autonomous event triggers, multi-agent/A2A, external channels, strict grounding — at Copilot Credits cost. Delta: stay declarative for in-M365 single-step individual retrieval; any of {autonomy, multi-step/looped orchestration, deterministic flows, multi-agent, external channels, group use, strict grounding, custom model, Dataverse} → full Copilot Studio. Findings: `research/01-platform-building-blocks.md`.
- [02 · What makes an agent "good"](issues/02-what-makes-agent-good.md) — same discipline both surfaces (clear role/goal, tight grounded scope, explicit rules+tone+output contract, guardrails, examples, iterative eval to 80–90% pass); mechanics differ (M365 8,000-char limit & auto model; Copilot Studio classic-vs-generative orchestration + system-topic moderation/fallback). Yields a **13-element candidate base skeleton** for ticket 03. Findings: `research/02-what-makes-agent-good.md`.
- [03 · Base skeleton — the AgentSpec](issues/03-base-skeleton.md) — **hybrid structured spec**: a config envelope (`meta`/`knowledge`/`capabilities`/`actions`/`conversationStarters`) + a free-text Markdown instruction body (MS's `# ROLE/# OBJECTIVE/# SCOPE/…` pattern), one surface-agnostic source of truth rendering to `declarativeAgent.json` or CS portal steps. 13 elements (6 core + 6 conditional) sorted into config vs. instructions zones; surface is *derived* via the 01-delta rule. Spec: [`templates/base-skeleton.md`](templates/base-skeleton.md).
- [04 · v1 archetypes](issues/04-v1-archetypes.md) — **6 archetypes** shipped, all AgentSpec instances ([`templates/archetypes/library.md`](templates/archetypes/library.md)): A Knowledge Q&A (decl), B IT Helpdesk (decl+action), C Employee Onboarding (CS+flow), D Research/Analyst (decl+caps), E Autonomous Monitoring (CS+trigger), F Compose-from-scratch (fallback). Prototyped A/B/C first — skeleton held, **no revision needed**; `capabilities` confirmed declarative-only, `surface` reliably derived.
- [05 · Builder conversation design](issues/05-builder-conversation-design.md) — **7-phase, goal-first interview** ([`builder-spec/conversation-design.md`](builder-spec/conversation-design.md)): greet & calibrate (quick/guided *dial*) → goal capture → archetype match → fill spec one field/turn (base-skeleton §4) → derive & explain surface → review & revise → emit artifacts. Surface never asked; edges (vague goal, surface-flip, over-broad knowledge, 8k limit, consequential action) handled. Validated with a 9-turn worked dialogue.
- [07 · Synthesis — the builder's own spec](issues/07-builder-agent-spec-synthesis.md) — **CAPSTONE / destination delivered** ([`builder-spec/builder-agent-spec.md`](builder-spec/builder-agent-spec.md)): the Agent Builder built on **Copilot Studio (generative orchestration)** — derived, since a branching interview + KB reasoning + artifact generation needs multi-step orchestration. Full instruction body (the 7-phase interview encoded), 4 knowledge files, **no custom actions** (artifacts emitted as chat), and an 8-step Copilot Studio assembly checklist. §6 confirms all destination components delivered.
- [06 · Artifact & manifest formats](issues/06-artifact-formats.md) — **M365 declarative = clean file-based import**: `.zip` app package chaining `manifest.json` (`copilotAgents.declarativeAgents[]`) → `declarativeAgent.json` (schema **v1.7**, 12 capability types, inline knowledge) → `apiPlugin.json` (**v2.4**, MCP + vault auth) → OpenAPI + icons. **Copilot Studio = no clean full-fidelity import**: agent moves via unmanaged Dataverse solution `.zip` or `pac copilot` YAML, but connections, knowledge auth, generative settings, channels, icon don't transfer → builder must emit **click-by-click portal steps** there. Findings: `research/06-artifact-formats.md`.

## Deferred to a future effort (fog that never blocked the destination)

<!-- The destination was reached without these; they'd be a v2 map, not a resumption. -->

- Evaluation / testing approach for agents the builder produces (a "help me test my agent" phase; research 02 §5 has the raw material).
- Governance, security, and publishing/sharing guidance the builder should bake in.
- Multi-language / localization handling.
- Deeper knowledge-source harvesting during the interview (partially covered: Phase 3c gathers sources; a richer connector-discovery flow is future).
- Optional Power Automate flow to package the emitted `declarativeAgent.json` as a downloadable file (builder-spec §2 notes this as a v1-optional enhancement).

## Out of scope

<!-- ruled beyond the destination; never graduates -->

- Live provisioning of agents via APIs/Graph/connectors (destination is spec + assets, not a running integration).
