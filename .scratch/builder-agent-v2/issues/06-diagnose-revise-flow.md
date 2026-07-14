# 06 · Diagnose→revise conversation flow design

Type: prototype
Status: resolved (2026-07-14)
Blocked by: 01, 02, 03, 04, 05

## Question

Design the **new mode's conversation flow** — the diagnose→revise journey — as a prototype validated with a worked dialogue, mirroring how v1's ticket 05 designed the build interview.

Decisions to reach (HITL — `/prototype` + `/grilling`):

- **Entry fork** at greet: "build new" vs. "improve/fix an existing agent", and within improve/fix the **symptom-first vs. goal-first** split.
- The **phased flow**: gather artifact → gather evidence (transcripts/test output, with the "how to capture" playbook from ticket 02) → reconstruct into AgentSpec (ticket 05) → isolate the layer (ticket 03 algorithm) → assess against taxonomy (ticket 01) / levers (ticket 04) → present **diagnosis + change-set** → revise-loop with the maker → **emit full revised artifact**.
- **Quick vs. guided dial** carried over from v1 (one field/turn vs. batched).
- **Edge cases**: partial/garbled paste, no evidence available, multiple independent problems, a fix that flips the surface (declarative→Copilot Studio), a fix that adds metered capability (credit note — see map fog), maker disagrees with the diagnosis.
- Reuse the existing instruction-body shape (ROLE/OBJECTIVE/SCOPE/RESPONSE RULES/OUTPUT FORMAT/WORKFLOW/GUARDRAILS/SELF-CHECK) so the new branch slots into `Agent/01-instructions.md`.
- Validate with a **worked dialogue** (e.g., "my HR agent refuses valid questions" → paste → diagnosis → revised `declarativeAgent.json`).

**Uses the ticket 05 domain model** — the flow encodes the diagnose→revise loop over `Finding` / `Change` / `Probe` / `verify-signal` / `Backlog` (single-Finding loop, confidence-gated, artifact-required). Plus two decisions **handed from ticket 05** to make here:
- **Licensing/permission as a root cause**: model it as a sub-type under the Grounding/Action layers, or as a **pre-flight "Entitlement" check** run before the five-layer binary search? (Research 01: silent SharePoint/OneDrive grounding failures from license/auth/permission gaps are a top declarative cause.)
- **Surface-flip escalation**: how the flow presents a Finding whose fix is *migrate declarative → Copilot Studio* (a declarative ceiling hit) — an escalation outcome distinct from an in-place Change (research 03 says escalate rather than keep tweaking).
- **Backlog ordering**: how multiple surfaced Findings are prioritized (ticket 04: fix by shared root cause; safety/compliance gates first).

Feeds ticket 07 (synthesis). Link the prototype artifact from this ticket on resolution.

## Answer

Resolved via `/prototype` (flow + worked dialogue) — the reacting artifact is [`builder-spec/diagnose-revise-design.md`](../builder-spec/diagnose-revise-design.md); flow + all three handed-down decisions confirmed with the user 2026-07-14.

- **Entry fork** at the shared greet: *build new* vs *improve/fix*; then *troubleshoot* (symptom-first) vs *improve* (goal-first) — same engine, different opening question.
- **10-step flow (D0–D9):** entry & framing → artifact-anchored **intake** (artifact required) → **reconstruct → AgentSpec + reflect back** → **Entitlement pre-check** → per-surface **evidence** capture → **reproduce** → **binary-search the layer** (change nothing; Instructions last) → **confidence → propose** (Change / Probe / escalation) → **apply & re-test the verify-signal** → **emit** diagnosis + change-set + revised artifact **+ ordered Backlog**.
- **Decision 1 — Entitlement pre-check (D3)** runs *before* the binary search: silent license/permission/auth gaps mimic Grounding/Instructions symptoms, so catch them first.
- **Decision 2 — Surface-flip escalation (D7):** a declarative-ceiling fix is a distinct escalation that bridges into the existing *build* flow on Copilot Studio, reusing the reconstructed AgentSpec (not modeled as an in-place Change).
- **Decision 3 — Backlog order (D9):** safety/compliance → the maker's reported symptom → confidence×impact; group shared-root-cause Findings; maker can reorder.
- **Reuse:** the improve/fix branch is a new `# WORKFLOW` branch inside the existing instruction-body shape, so it slots into `Agent/01-instructions.md` at ticket 07.
- Edge cases handled: partial paste, no evidence (cap confidence, offer Probes), multiple problems, credit-cost fixes, maker disagrees (settle with a Probe), "improve" with no test set.
- **Validated** by a guided-path worked dialogue (§8): HR agent over-refusal → paste → reconstruct → entitlement ruled out → `-developer on` card → isolates to Instructions (over-tight `# SCOPE`) → one Change + verify-signal → re-test → emit all three outputs.
