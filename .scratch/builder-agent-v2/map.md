# Wayfinder Map: Builder Agent v2 — Improve & Troubleshoot

`wayfinder:map` · effort slug: `builder-agent-v2` · **STATUS: CLOSED (2026-07-14)** — destination reached, all 7 tickets resolved.

> Successor to the closed [`builder-agent`](../builder-agent/map.md) effort, which deferred "a 'help me test my agent' phase" to a future map. This is that map.
>
> **Delivered:** the shipped [`../../Agent/`](../../Agent/) package is now a two-mode **build + improve/fix** agent. Assemble it per [`Agent/README.md`](../../Agent/README.md); the improve/fix reference is [`Agent/knowledge/05-diagnostics.md`](../../Agent/knowledge/05-diagnostics.md).

## Destination

Extend the existing **Agent Builder** from **build-only** to **build + improve + troubleshoot**, delivered as an **updated build-ready package** (like v1 — execution carried into the map; see Notes).

The capability is a **new "improve/fix" fork** inside the *same* agent (chosen at greet, alongside "build new"). The maker supplies **their agent's own artifacts + real conversation transcripts / test-run outputs** (maker-pasted — **no direct tenant access**, staying inside the planning-only boundary). A shared **diagnose→revise engine** then:

1. **reconstructs** the pasted artifact into the AgentSpec model,
2. **isolates** the failure to a layer (instructions / grounding / orchestration / moderation / action),
3. returns **three layers of output**: a plain-language **diagnosis** (symptom→root cause), a targeted **change-set** ("in # SCOPE, change X→Y, because…"), and the **full paste-ready revised artifact**.

"Troubleshoot" enters **symptom-first**; "improve" enters **goal-first** — same core engine, different opening question.

**Deliverables that close the map** (updates to the real `Agent/` package):
- new `Agent/knowledge/05-diagnostics.md` (failure taxonomy + fix patterns + how to read the surfaces' own test/analytics signals + diagnostic method),
- revised `Agent/01-instructions.md` (greet fork + the diagnose→revise workflow branch),
- updated `Agent/00-agent-settings.md` (starters + knowledge list), `Agent/README.md`, `builder-spec/`, and repo `README.md`.

Scope covers **both** target surfaces. Planning + assets only: no live-tenant provisioning, no direct telemetry access.

## Notes

- **Domain**: diagnosing & improving already-built M365 declarative agents and Copilot Studio agents. New vocabulary (symptom / root cause / diagnostic layer / evidence / reconstruction / change-set) is pinned in ticket 05.
- **Execution override**: like v1, this map **carries execution into itself** — the capstone ticket edits the real `Agent/` deliverables, it does not merely design them.
- **Input contract**: maker pastes artifacts + real transcripts / test-run outputs. The tool never touches the tenant; where it needs more evidence it tells the maker how to capture it.
- **Output contract**: diagnosis + change-set + full revised artifact (all three, every time).
- **Skills every session should consult**: `/grilling` + `/domain-modeling` for decisions; mattpocock `/research` for research tickets (grounded in **current official Microsoft Learn docs**, not model memory — these platforms change fast); `/prototype` for the flow-design ticket.
- **Reuse, don't duplicate**: build on the existing AgentSpec ([[project-agentspec-hybrid-decision]]), archetype library, and the 4 existing knowledge files; the diagnose→revise engine reconstructs *into* the same AgentSpec model.
- Research findings are captured under `.scratch/builder-agent-v2/research/`; each research ticket points at its findings file.

## Decisions so far

<!-- one line per closed ticket: gist of the answer + link -->

- [01 · Failure-mode taxonomy + fix patterns](issues/01-failure-taxonomy.md) — a **symptom → root-cause → fix** catalog keyed to AgentSpec zones (`# SCOPE`/`# GROUNDING`/`KNOWLEDGE`/`ACTIONS`/`# GUARDRAILS`/orchestration/moderation), with surface-specific causes split out. Findings: `research/01-failure-taxonomy.md`.
- [02 · Native testing / analytics / observability](issues/02-testing-observability.md) — the two surfaces are **wildly asymmetric**: Copilot Studio gives a deep exportable stack (**activity map** shows sources *used vs. searched-but-unused*, tool I/O, AI "Rationale"; `dialog.json` snapshots, outcome/transcript CSVs, preview **evaluation** harness), while declarative agents give only the **ephemeral `-developer on` Developer Mode card** (+ one Agents-Toolkit `.txt`). ⇒ the "how to get me evidence" ask must be **calibrated per surface**. Findings: `research/02-testing-observability.md`.
- [03 · Diagnostic methodology — root-cause isolation](issues/03-diagnostic-methodology.md) — a **five-layer binary search** (Moderation → Action → Orchestration → Grounding → **Instructions last, as the residual**), gated on objective machine signals; each layer has a confirm-before-change **probe** (e.g. "Allow ungrounded responses OFF" for grounding) and a minimal-change→re-test loop. Ends in a **7-step algorithm** (Intake → Reproduce → Binary-search → Probe → One-fix → Re-test → Iterate/escalate) ready for ticket 06. Findings: `research/03-diagnostic-methodology.md`.
- [04 · Improvement / optimization levers](issues/04-improvement-levers.md) — Microsoft now ships an official **evaluation-driven triage & remediation** framework (`change X → rerun Y → expect Z`); levers across eval-loop (target 80–90%, safety <95% = block), grounding precision, instruction/output tuning (incl. the **8,000-char "instruction budget"** trap), and cost/credits (rates verified unchanged; surface-downgrade is itself a lever). Distilled to a **10-row change-set catalog** (goal → lever → AgentSpec zone → verify). Findings: `research/04-improvement-levers.md`.
- [05 · Diagnostic domain model + reconstruction](issues/05-diagnostic-domain-model.md) — the effort's **ubiquitous language** + the **diagnose→revise model**: a **Finding** (`symptom → isolated layer → root cause → confidence → Change|Probe`) worked in a **single-Finding loop with a surfaced Backlog**; **Artifact required** as anchor (full reconstruct into AgentSpec, gaps = `unknown`); **confidence-gated** (Med/Low ⇒ Probe or exact evidence-ask, never a guess-fix); a **Change** is atomic per Finding as a structured diff (`layer, zone(s), before→after, rationale, verify-signal`), one per re-test cycle, accumulating into the Revised artifact; five isolation-ordered layers with Instructions as the residual. Handed licensing-as-cause + surface-flip escalation to ticket 06.
- [06 · Diagnose→revise conversation flow design](issues/06-diagnose-revise-flow.md) — a **10-step flow (D0–D9)** ([`builder-spec/diagnose-revise-design.md`](builder-spec/diagnose-revise-design.md)): entry fork (build vs improve/fix; troubleshoot vs improve) → artifact-anchored intake → reconstruct-and-reflect → **Entitlement pre-check** → per-surface evidence → reproduce → binary-search → confidence-gated propose (Change/Probe/escalation) → re-test the verify-signal → emit three-layer output + ordered Backlog. Three handed decisions locked: **(1)** licensing = a **pre-flight Entitlement check** before the search; **(2)** surface-flip = a **distinct escalation bridging into the build flow**; **(3)** Backlog order = **safety → reported symptom → confidence×impact**. New branch reuses the existing instruction-body shape. Validated by a worked dialogue.
- [07 · Update the build-ready package](issues/07-update-package.md) — **CAPSTONE / destination delivered.** The shipped [`../../Agent/`](../../Agent/) package is now a two-mode agent: new [`Agent/knowledge/05-diagnostics.md`](../../Agent/knowledge/05-diagnostics.md) (taxonomy + evidence playbooks + isolation algorithm + entitlement check + improve levers + surface-flip, grounded & cited); `Agent/01-instructions.md` routes at greet into **Workflow A (build)** / **Workflow B (improve-fix, D0–D9)** with new guardrails/self-check; `00-agent-settings.md`, `Agent/README.md`, the v1 builder-spec pointer, the repo `README.md`, and the project memory all updated. Same planning-only boundary — maker pastes artifacts + evidence, no live-tenant access.

## Not yet specified

<!-- in-scope fog; graduates to tickets as the frontier advances -->

_(empty — all fog to date has graduated into tickets or been resolved. Remaining work is ticket 07, the capstone.)_

<!-- Resolved fog (kept for trace):
     • "improve" prioritization → ticket 06 Backlog order (safety → reported symptom → confidence×impact).
     • licensing/permission as a root cause → ticket 06 D3 pre-flight Entitlement check.
     • surface-flip escalation → ticket 06 D7 distinct escalation bridging into the build flow.
     • credit/cost estimate on surface flip → ticket 06 edge-cases (note the credit implication before commit).
     • reproduce-it-first → ticket 03 algorithm step / ticket 06 D5. -->


<!-- Graduated / answered by research (cleared from fog):
     • "credit/cost estimate on surface flip" → confirmed a real edge by ticket 04; folded into ticket 06 edge-cases.
     • "reproduce-it-first sub-step" → ANSWERED yes by ticket 03 (Reproduce = step 2 of the 7-step algorithm); baked into ticket 06 flow. -->


## Out of scope

<!-- ruled beyond the destination; never graduates -->

- **Direct tenant / telemetry access** (Graph/Dataverse/analytics connection to inspect a live agent) — considered and ruled out at charting; would break the planning-only boundary and is a different effort.
- Live provisioning / auto-applying fixes to a deployed agent (inherited from v1 — destination is revised assets, not a running integration).
