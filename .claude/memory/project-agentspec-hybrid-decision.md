---
name: project-agentspec-hybrid-decision
description: The base agent template is a hybrid structured "AgentSpec" — config envelope + Markdown instruction body
metadata:
  type: project
---

The base skeleton every template and every emitted agent is built from — the **AgentSpec** — is a **hybrid structured spec**: a structured `config` envelope (`name`, `description`, `surface`, `knowledge`, `capabilities`, `actions`, `conversationStarters`) **+** one free-text `instructions` field in Microsoft's Markdown header pattern (`# ROLE / # OBJECTIVE / # SCOPE / # RESPONSE RULES / # OUTPUT FORMAT / # CAPABILITIES / # WORKFLOW / # GUARDRAILS / # VOCABULARY / # EXAMPLES / # SELF-CHECK / # FOLLOW-UP` — 6 core + 6 conditional). One surface-agnostic source of truth that renders to `declarativeAgent.json` (M365) or click-by-click Copilot Studio portal steps. Spec: `.scratch/builder-agent/templates/base-skeleton.md`.

**Why:** the skeleton must hold both manifest/config fields (needed to emit the JSON manifest) AND high-quality free-text instructions (Microsoft recommends well-structured prose, not decomposed fields), across two different surfaces, filled from one maker conversation.

**How to apply:** keep `config` vs `instructions` as the two zones; config items are referenced by **exact name** inside the instruction body. `capabilities` is **declarative-only** (Copilot Studio models them as tools — a render concern, not a skeleton field). `surface` is **derived**, never asked upfront: any of {autonomy/event triggers, multi-step or looped orchestration, deterministic flows, multi-agent, external channels, group use, strict grounding, custom model, Dataverse} → `copilot-studio`; else `declarative`. Declarative instruction body must stay ≤ 8,000 chars.

Alternatives rejected: Markdown-template-only (no clean home for config/manifest fields); pure structured schema (loses MS's recommended free-text instruction shape, too heavy for non-technical makers). Rationale: `.scratch/builder-agent/research/02-what-makes-agent-good.md` §7.
