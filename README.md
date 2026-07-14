# Agent-Builder-Agent

A build-ready package for creating an **"Agent Builder"** — a Copilot Studio agent that talks to a person and helps them design and produce **their own** Microsoft agent, then hands them ready-to-paste artifacts to create it.

The Agent Builder helps makers build **both** kinds of Microsoft agent:

- **Microsoft 365 declarative agents** ("agents in Microsoft 365 Copilot")
- **Copilot Studio agents** (topics, Power Automate flows, connectors, autonomous triggers, generative orchestration)

It's designed for a **mixed audience** — it detects whether it's talking to a non-technical maker or a technical builder and adapts, offering a quick path or a guided, explained walkthrough.

> **What this repo is:** the research, templates, and specification you assemble into the Agent Builder inside Copilot Studio. It is a **blueprint + assets**, not a running agent — there is no live-tenant provisioning here.

---

## What's inside

Everything lives under `.scratch/builder-agent/` (it was produced as a [wayfinder](#how-this-was-built) planning effort; the layout is stable and safe to depend on):

```
.scratch/builder-agent/
├─ map.md                         Index of every decision (the effort is CLOSED)
├─ issues/01–07.md                The decision tickets, each with its answer
├─ research/
│  ├─ 01-platform-building-blocks.md   M365 vs Copilot Studio: capabilities, limits, when to use which
│  ├─ 02-what-makes-agent-good.md      Instruction/knowledge/guardrail/eval best practices (+ §7 design rationale)
│  └─ 06-artifact-formats.md           Exact output formats: declarativeAgent.json v1.7, apiPlugin.json v2.4, CS portal steps
├─ templates/
│  ├─ base-skeleton.md            ★ The "AgentSpec" — the structure every agent is built from
│  └─ archetypes/library.md       6 starter archetypes built on the skeleton
└─ builder-spec/
   ├─ conversation-design.md      The 7-phase interview the builder runs
   └─ builder-agent-spec.md       ★★ THE DELIVERABLE — the complete, build-ready Agent Builder spec
```

The two files marked with stars are the ones you'll use most:

- **`builder-spec/builder-agent-spec.md`** — the complete spec of the Agent Builder itself, including an assembly checklist. **Start here to build the agent.**
- **`templates/base-skeleton.md`** — the **AgentSpec**, the reusable structure at the heart of everything.

---

## How to use it

### Build the Agent Builder in Copilot Studio

Follow the **assembly checklist** in `builder-spec/builder-agent-spec.md` (§5). In short:

1. **Create** a new agent in Copilot Studio; name it *Agent Builder*.
2. **Orchestration:** set **generative**; **Allow ungrounded responses = ON**.
3. **Instructions:** paste the instruction body from the spec (§3).
4. **Knowledge:** upload the four knowledge files (§4) — the base skeleton, the archetype library, the artifact-formats research, and the platform + quality research — or place them in a SharePoint library and point the agent there.
5. **Moderation:** leave at **High**. **Conversation starters:** add the three provided.
6. **Fallback:** edit the Fallback system topic so off-topic asks restate what the builder does.
7. **Test** with the built-in test chat: try each starter, a vague goal, an out-of-scope ask, one declarative case and one Copilot-Studio case. Iterate to ~80–90% pass.
8. **Publish** and share.

### What the Agent Builder does once running

It runs a **goal-first, one-question-at-a-time interview**:

1. Greets and calibrates (quick vs. guided).
2. Asks what the maker wants the agent to do.
3. Proposes the nearest **archetype** as a starting point.
4. Fills the **AgentSpec** — audience & tone, scope & refusals, knowledge sources, actions, house rules, conversation starters.
5. **Derives the surface** (declarative vs. Copilot Studio) from the answers and explains the choice — the maker never has to know the difference.
6. Shows a plain-language summary and revises until the maker is happy.
7. **Emits ready-to-paste artifacts:**
   - **Declarative** → a valid `declarativeAgent.json` (plus `apiPlugin.json` if there are actions) and a publish checklist.
   - **Copilot Studio** → numbered click-by-click portal steps (because Copilot Studio has no clean full import).

---

## Key concepts

### The AgentSpec (the base skeleton)

A single, surface-agnostic **hybrid structured spec** that every template and every produced agent is built from:

- a structured **`config` envelope** — name, description, surface, knowledge, capabilities, actions, conversation starters (the parts that become manifest/portal fields); plus
- one free-text **`instructions`** body in Microsoft's proven Markdown pattern (`# ROLE / # OBJECTIVE / # SCOPE / …`).

One source of truth renders to either surface. See `templates/base-skeleton.md`.

### The archetype library

Six ready-to-tailor starting points (`templates/archetypes/library.md`), spanning both surfaces and every capability tier:

| Archetype | Surface |
|---|---|
| Knowledge Q&A Assistant | declarative |
| IT Helpdesk Agent | declarative + action |
| Employee Onboarding Agent | Copilot Studio + flow |
| Research / Analyst Assistant | declarative + capabilities |
| Autonomous Monitoring Agent | Copilot Studio + trigger |
| Compose-from-scratch | fallback (bare skeleton) |

### Surface is derived, not asked

Makers don't choose declarative vs. Copilot Studio. The builder infers it: any need for autonomy, multi-step/looped orchestration, deterministic flows, multi-agent, external channels, group use, strict grounding, a custom model, or Dataverse forces **Copilot Studio**; otherwise **declarative**. (Full rule and rationale in `research/01`.)

---

## How this was built

This package was produced with the **wayfinder** planning method (part of the `mattpocock/skills` toolkit): the work was charted as a **map** of decision tickets (`.scratch/builder-agent/map.md`), researched against current Microsoft documentation, and resolved one decision at a time. The map is now **closed** — its `## Decisions so far` section is a readable audit trail of every choice and why.

Project context and key decisions are also recorded in **`.claude/memory/`** (committed repo memory, loaded at the start of each session).

---

## Extending it (future / v2)

Consciously deferred — a future wayfinder effort, not part of this one (see the map's "Deferred" section):

- An "help me test my agent" evaluation phase.
- Governance, security, and publishing guidance baked into the builder.
- Multi-language / localization.
- Richer knowledge-source / connector discovery during the interview.
- An optional Power Automate flow to package the emitted `declarativeAgent.json` as a downloadable file.
