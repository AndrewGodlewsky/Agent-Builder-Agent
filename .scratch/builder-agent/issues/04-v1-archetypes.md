# 04 · Which archetypes ship in v1

Type: prototype
Status: resolved
Blocked by: 03

## Question

Decide the starter set of use-case archetypes (layer 2), each built on the base skeleton (03).

Decide:

- The list of v1 archetypes (candidates: knowledge/FAQ assistant, IT/helpdesk agent, HR policy agent, sales/research agent, workflow-automation agent, autonomous monitoring agent). How many, and which.
- For each archetype: target surface (declarative vs. Copilot Studio vs. either), pre-filled skeleton values, recommended knowledge pattern, suggested topics/actions.
- Which archetypes are "compose from scratch" fallbacks vs. fully pre-filled.

Prototype one or two archetypes end-to-end first (via `/prototype`) to validate the skeleton actually instantiates cleanly, then commit the full list.

Output: archetype specs saved under `.scratch/builder-agent/templates/archetypes/`.

## Answer

**Decision: ship 6 v1 archetypes** (user-approved), all instances of the AgentSpec — library at [`templates/archetypes/library.md`](../templates/archetypes/library.md):

- **A · Knowledge Q&A** (declarative, knowledge-only) — the floor case.
- **B · IT Helpdesk** (declarative + read action + capability + workflow).
- **C · Employee Onboarding** (copilot-studio, write flows + autonomous trigger).
- **D · Research/Analyst** (declarative + `web_search` + `code_interpreter`).
- **E · Autonomous Monitoring** (copilot-studio, event trigger, proactive).
- **F · Compose-from-scratch** — the fallback on the bare skeleton for when no archetype fits.

**Prototype validation (per `/prototype`):** built A, B, C end-to-end first as throwaway AgentSpec instances to stress empty→full config zones and both surfaces; the skeleton (ticket 03) held with **no revision required**. Confirmed `capabilities` is declarative-only (a render concern on CS, not a skeleton field) and that `surface` is reliably **derived** from the answers, not asked. D and E extend the proven B/C patterns. The prototype instances were folded into the deliverable library; verdict recorded there.

Per-archetype: each specifies surface, pre-filled `config` (knowledge/capabilities/actions/starters), and a full instruction body; the coverage grid in the library maps which conditional sections each uses. Hands to ticket 05 (interview that fills these) and ticket 07 (render to artifacts).
