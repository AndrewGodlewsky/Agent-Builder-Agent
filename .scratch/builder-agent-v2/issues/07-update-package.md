# 07 · Update the build-ready package (CAPSTONE)

Type: task
Status: resolved (2026-07-14) — CAPSTONE, closes the map
Blocked by: 06

## Question

**Closes the map.** Carry the design through to the actual build-ready deliverables — edit the real `Agent/` package (and its provenance docs) so the Agent Builder now does **build + improve + troubleshoot**.

Work to do (AFK where possible; confirm surface with the maker):

- **New knowledge file** `Agent/knowledge/05-diagnostics.md` — failure taxonomy + fix patterns (ticket 01), how to read each surface's own test/analytics signals + capture playbook (ticket 02), the root-cause isolation algorithm (ticket 03), improvement levers (ticket 04), the reconstruction rules + change-set representation (ticket 05). Grounded, paste-ready.
- **Revised `Agent/01-instructions.md`** — add the greet **entry fork** and the **diagnose→revise WORKFLOW branch** (ticket 06), plus GUARDRAILS/SELF-CHECK additions (never invent a diagnosis without evidence; always output diagnosis + change-set + full revised artifact).
- **`Agent/00-agent-settings.md`** — add improve/troubleshoot conversation starter(s) and list the new knowledge file.
- **`Agent/README.md`** — reflect the new capability, the 5th knowledge file, and updated test cases.
- **`builder-spec/`** — update the builder's own spec (the capstone doc) to describe the two-mode agent.
- **Repo `README.md`** — refresh per the project's README-currency rule (delegate to a sub agent per CLAUDE.md).
- Update the **v1 memory** ([[project-agent-builder-overview]]) to note the v2 mode, and this map's **Decisions so far**.

Resolved when the `Agent/` package is a coherent build-ready two-mode agent and the map is closed.

## Answer

**Delivered — the shipped `Agent/` package is now a two-mode (build + improve/fix) agent.** All edits complete and verified 2026-07-14:

- **New knowledge file `Agent/knowledge/05-diagnostics.md`** (~281 lines) — the improve/fix reference: the ticket-05 domain model (ubiquitous language + 5 isolation-ordered layers), per-surface evidence & capture playbooks (research 02), the Entitlement pre-check (research 01), the five-layer isolation algorithm + probes (research 03), the symptom→layer→zone→fix taxonomy + Copilot Studio error-code decoder (research 01), improvement levers + eval loop (research 04), and surface-flip escalation. Grounded in Microsoft Learn with inline citations; house-style-consistent.
- **`Agent/01-instructions.md`** — now routes at greet (step 0) between **Workflow A (build)** and **Workflow B (improve/fix, D0–D9)**; added guardrails ("never invent a diagnosis"; change one thing, verify by signal; three-layer output) and a per-mode SELF-CHECK.
- **`Agent/00-agent-settings.md`** — "Fix my agent" conversation starter; 5th knowledge file listed; description + Fallback updated to build/improve/troubleshoot.
- **`Agent/README.md`** — two-mode intro, five knowledge files, an improve/fix test case, and a revised "what done looks like."
- **`../builder-agent/builder-spec/builder-agent-spec.md`** — a v2-extension pointer to this effort + the diagnose-revise design; notes `Agent/` is canonical.
- **Repo `README.md`** — broadened to the two-mode agent, four→five knowledge files, an "Improve or fix" usage paragraph, and the v2 section moved from "in progress" to **"Delivered."**
- **Memory** ([[project-agent-builder-overview]]) refreshed to the delivered state.

Destination reached: the Agent Builder now builds **and** improves/troubleshoots, within the same planning-only boundary (maker pastes artifacts + evidence; no live-tenant access).
