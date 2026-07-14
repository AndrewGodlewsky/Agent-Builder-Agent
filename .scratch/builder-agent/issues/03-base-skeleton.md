# 03 · The base skeleton (invariant agent structure)

Type: grilling
Status: resolved
Blocked by: 01, 02

## Question

Define the base skeleton — the invariant, fill-in-the-blank structure that every template and every agent the builder emits will follow. This is layer 1 of the two-layer template library.

Decide, using findings from 01 (platform building blocks) and 02 (agent-quality principles):

- The named sections of the skeleton (e.g. identity/role, goal, scope & boundaries, instruction body, knowledge sources, actions/tools, conversation starters, guardrails, fallback behavior, tone).
- Which sections are common to both surfaces vs. surface-specific.
- The canonical field-by-field format the skeleton is expressed in (so archetypes and emitted artifacts can be derived from it mechanically).
- How a maker's answers during the builder conversation map onto skeleton fields.

Output: a written base-skeleton specification saved under `.scratch/builder-agent/templates/`.

## Answer

**Decision: the base skeleton is a hybrid structured spec — the "AgentSpec"** — with the full spec at [`templates/base-skeleton.md`](../templates/base-skeleton.md).

- **Form: hybrid** (chosen over Markdown-template-only and pure-schema; rationale in `research/02` §7). A structured **config envelope** (`meta`, `knowledge`, `capabilities`, `actions`, `conversationStarters`) + a free-text **instruction body** in Microsoft's proven Markdown header pattern. One surface-agnostic source of truth that renders to `declarativeAgent.json` (M365) or click-by-click portal steps (Copilot Studio).
- **Named sections:** adopted the 13 researched elements, sorted into two zones — *config* (name/description, knowledge, capabilities, actions, conversation starters) vs. *instructions* (`# ROLE / # OBJECTIVE / # SCOPE / # RESPONSE RULES / # OUTPUT FORMAT / # CAPABILITIES / # WORKFLOW / # GUARDRAILS / # VOCABULARY / # EXAMPLES / # SELF-CHECK / # FOLLOW-UP`). 6 core sections + 6 conditional; config actions/capabilities are referenced by exact name inside the instruction body.
- **Common vs. surface-specific:** all 13 elements are common in *principle*; §3 of the spec maps each to its M365 vs. Copilot Studio mechanic (e.g. fallback = manifest restriction on M365 vs. a Fallback *topic* on CS; 8,000-char cap on M365 only).
- **Canonical format:** YAML AgentSpec (config) + Markdown body (instructions) — see §1–2.
- **Maker-answer mapping:** §4 gives the question→field contract that ticket 05's interview fills; **surface is derived, not asked**, via the 01-delta rule.
- Validated with a worked HR-Policy-Assistant example that uses 7/13 elements and correctly omits the 6 conditional ones (§5).
