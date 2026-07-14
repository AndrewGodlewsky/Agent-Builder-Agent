# 05 · The builder agent's conversation design

Type: prototype
Status: resolved
Blocked by: 03

## Question

Design how the builder agent interviews a maker and drives the conversation to a finished, ready-to-paste artifact set.

Decide (and prototype the flow with `/prototype`):

- **Skill-level detection**: how the builder reads whether it's talking to a non-technical maker or a technical builder, and how it branches into quick vs. guided paths.
- **The interview flow**: the sequence of questions that fills the base skeleton (03) — starting from "what do you want the agent to do," selecting/tailoring an archetype (04), gathering knowledge sources, defining scope/guardrails, and confirming.
- **Surface selection**: how/when the builder decides or recommends declarative vs. Copilot Studio (using the 01 delta guide).
- **Confirmation & handoff**: how it summarizes, lets the maker revise, and then emits artifacts.
- Failure/edge handling: vague requests, out-of-scope asks, maker who doesn't know what they want.

Output: a conversation-design spec + a worked example dialogue saved under `.scratch/builder-agent/builder-spec/`.

## Answer

**Decision: a 7-phase, goal-first interview** — spec + worked dialogue at [`builder-spec/conversation-design.md`](../builder-spec/conversation-design.md).

- **Flow:** Phase 0 greet & calibrate → 1 goal capture → 2 archetype match → 3 fill the spec (one field/turn on guided, per base-skeleton §4) → 4 derive & explain surface → 5 review & revise → 6 emit artifacts.
- **Skill-level detection** via an explicit quick-vs-guided offer + inferred signals; the pace is a **dial, not a switch** (deepen/speed mid-conversation).
- **Surface is never asked** — derived by the 01-delta rule and explained in one sentence.
- **Confirmed decisions:** (a) opening = goal-first → suggest nearest archetype (not menu-first); (b) Phase 5 = plain-language summary + revise loop; (c) quick path keeps a compressed one-line archetype match.
- **Edge handling:** vague goal → archetype menu as examples; "don't know what I want" → walk archetypes; surface-flipping capability → confirm; over-broad knowledge → nudge tighter; >8,000-char declarative body → trim or move to CS; consequential action → enforce confirm-before-acting.
- **Validated** with a 9-turn worked dialogue (non-technical maker → HR assistant → `declarativeAgent.json` + publish checklist).

Phase 6 render *format* is deferred to ticket 07 (this spec defines *when* emission happens and *what* is produced, not the exact field mapping).
