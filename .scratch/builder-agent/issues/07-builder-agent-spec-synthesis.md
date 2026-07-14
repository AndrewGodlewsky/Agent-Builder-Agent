# 07 · Synthesis — the builder agent's own spec

Type: grilling
Status: resolved
Blocked by: 03, 05, 06

## Question

Assemble the capstone: the complete specification of the builder agent itself, ready to build in Copilot Studio.

Synthesize from the base skeleton (03), conversation design (05), and artifact formats (06) into a single build-ready spec:

- **The builder's own system instructions** (verbatim, using the skeleton on itself).
- **The builder's knowledge sources**: the research knowledge base (01, 02), the base skeleton, the archetype library (04), and the artifact-format reference (06) — packaged as knowledge the builder agent reads at runtime.
- **The builder's tools/flows**: what actions or topics it needs (e.g. artifact-emission logic, surface-selection guidance).
- **Which surface the builder itself should be built on** and why.
- An assembly checklist: the exact steps to stand it up in Copilot Studio from these files.

Output: the final build-ready builder-agent spec under `.scratch/builder-agent/builder-spec/`. This closes the map.

## Answer

**The capstone is delivered** — the full build-ready spec is at [`builder-spec/builder-agent-spec.md`](../builder-spec/builder-agent-spec.md).

- **Surface: the builder is built on Copilot Studio (generative orchestration, ungrounded ON, moderation High)** — derived by the project's own delta rule: a branching multi-phase interview + reasoning over a large KB + artifact generation needs multi-step orchestration, which a declarative agent (single-step, 8,000-char cap) can't host.
- **The builder as an AgentSpec** (§2): name/description/starters, four knowledge files, **no custom actions** (artifacts are emitted as chat code blocks/portal steps — no connectors needed).
- **Instruction body** (§3): the full 7-phase interview from ticket 05 encoded as agent instructions, with the derive-the-surface rule, guardrails (valid-fields-only, 8k warning, confirm-before-consequential), self-check, and the two-surface emit step grounded in research 06.
- **Knowledge sources** (§4): `base-skeleton.md`, `archetypes/library.md`, `research/06`, and `research/01`+`02` concatenated.
- **Assembly checklist** (§5): 8 steps to stand it up + test in Copilot Studio.
- **Destination coverage table** (§6): confirms all three destination components (research KB, template library, builder spec with ready-to-paste output) are delivered.

**Map closed** — no open tickets, no live fog.
