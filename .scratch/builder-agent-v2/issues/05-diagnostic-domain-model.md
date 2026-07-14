# 05 · Diagnostic domain model + AgentSpec reconstruction

Type: grilling
Status: resolved (2026-07-14)
Blocked by: 01, 02, 03

## Question

Pin down the **domain model** for the diagnose→revise engine and decide **how a pasted artifact is reconstructed** into the AgentSpec.

Decisions to reach (HITL — `/grilling` + `/domain-modeling`):

- **Vocabulary**: precise definitions for `symptom`, `root cause`, `diagnostic layer` (instructions / grounding / orchestration / moderation / action), `evidence` (artifact vs. transcript vs. test-output), `reconstruction`, `change-set`. Record as the effort's ubiquitous language.
- **Reconstruction**: how the engine turns a pasted `declarativeAgent.json` / instruction body / Copilot Studio config into the AgentSpec model — what maps cleanly, what must be inferred, what to do when the paste is partial or malformed.
- **Symptom→layer mapping**: adopt/refine the mapping from ticket 01 into the layer taxonomy from ticket 03 so diagnosis is deterministic, not vibes.
- **Change-set representation**: how a proposed change is expressed against the reconstructed spec (field-level diff referencing AgentSpec zones) so it renders to both the change-set output and the full revised artifact.
- **Confidence & missing evidence**: how the engine behaves when evidence is thin — when to diagnose anyway vs. ask the maker to capture more (ties to ticket 02's "how to get me evidence" playbook).

Feeds ticket 06 (flow design). Record decisions here on resolution; land the diagnostic KB material in `research/` / the eventual `Agent/knowledge/05-diagnostics.md`.

## Answer

Resolved via `/grilling` + `/domain-modeling` (5 decisions confirmed 2026-07-14). This is the effort's **ubiquitous language** and the diagnose→revise model; it graduates into `Agent/knowledge/05-diagnostics.md` at ticket 07 and drives the flow in ticket 06.

### Glossary (ubiquitous language)

| Term | Definition |
|------|-----------|
| **Agent-under-repair** | The maker's existing deployed agent being diagnosed. |
| **Artifact** | The agent's own config + instructions (`declarativeAgent.json` / instruction body / CS exported-or-described config). **Required anchor** — reconstruction starts here; no artifact ⇒ can't emit a full revised artifact. |
| **Evidence** | Observed-behavior signal the maker pastes, **tiered**: *Machine signal* (dev-mode card / activity-map node / error code) > *Transcript* (real conversation / test-run output) > *Self-report* (artifact-only / described symptom). |
| **Symptom** | The observed wrong behavior (troubleshoot, symptom-first) or the gap to close (improve, goal-first). |
| **Diagnostic layer** | The pipeline stage a fault lives in — exactly **five, isolation-ordered**: **Moderation → Action → Orchestration → Grounding → Instructions**. Instructions is the **residual**, diagnosed last (research 03). |
| **Root cause** | The specific reason expressed in **AgentSpec terms** (a zone/field) within one layer. |
| **Finding** | Core unit: `{symptom, isolated layer, root cause, confidence, proposed Change OR Probe}`. |
| **Backlog** | Suspected Findings surfaced (named) but not yet worked — fixed one at a time. |
| **Confidence** | High / Med / Low = *f(evidence tier, isolation cleanliness)*. |
| **Probe** | A confirm-before-change action (research 03) that raises confidence **without editing config** (ungrounded-OFF, drop moderation a notch, re-check action params). The Med/Low move. |
| **Change** | Atomic fix for one Finding: `{layer, zone(s), before → after, rationale, verify-signal}`. **One per re-test cycle**; may span >1 AgentSpec zone only when it is one logical fix (e.g. add `KNOWLEDGE` source + reference it in `# CAPABILITIES`). |
| **Verify-signal** | The **objective signal that must flip** to confirm a Change worked (function now *Selected*, node cites right source, no `ContentFiltered`) — never "the answer looks better." |
| **Reconstruction** | Parsing the Artifact into the AgentSpec model; unparseable/absent fields → marked **`unknown`** (lowers confidence). |
| **Revised artifact** | Reconstructed spec + accumulated Changes, rendered back to the surface. |

### Decisions

1. **Reasoning unit = single-Finding loop + surfaced Backlog.** Fix ONE Finding at a time and re-test (research 03 discipline); other suspected problems are surfaced as a named, unfixed Backlog so nothing is lost (research 01 multi-cause reality). Not batch (bundled changes destroy re-test attribution).
2. **Reconstruction = artifact is a required anchor; full parse, zoomed diagnosis.** Reconstruct the whole Artifact into the same AgentSpec model the builder already uses (so it can render a full revised artifact), but focus diagnosis on the suspected layer's zone. Partial/malformed paste → parse what's there, mark gaps `unknown` (feeds confidence). Not artifact-optional; not lightweight-patch.
3. **Confidence-gated behavior — probe or ask, never guess-fix.** High ⇒ propose the Change + its verify-signal. Med/Low ⇒ the move is a **Probe** or an **exact evidence-capture ask** (name top-2 candidate layers + the per-surface capture click-path from research 02), never a blind config change. Enforces "never invent a diagnosis without evidence."
4. **Change representation = atomic per Finding, structured diff.** `{layer, zone(s), before→after, rationale, verify-signal}`, exactly one Change proposed per loop cycle (may touch 2 zones if one logical fix); Changes accumulate across cycles into the evolving Revised artifact. Not one-field-strict; not free-bundle.
5. **Symptom→layer mapping = adopted** from research 01 (taxonomy) keyed into research 03 (five layers), carrying the **surface-asymmetry** insight: same symptom, different likely layer per surface — declarative skews Instructions / Knowledge / **Licensing**; Copilot Studio exposes error-codes + activity map.

### The diagnose→revise loop (model in motion)

```
Intake (symptom + REQUIRE artifact + gather Evidence per surface playbook)
  → Reconstruct artifact → AgentSpec (gaps = unknown)
  → Reproduce
  → Binary-search the layer  [Moderation→Action→Orchestration→Grounding→Instructions,
                              machine-signal-gated, Instructions last]
  → set Confidence
       HIGH   → propose ONE atomic Change (+ verify-signal)
       MED/LO → propose a Probe OR an exact evidence-capture ask (name top-2 layers)
  → maker applies → re-test the VERIFY-SIGNAL → confirm or revert
  → surface remaining Backlog → next Finding
Every cycle emits: Diagnosis + accumulated Change-set + full Revised artifact
```

### Handed to ticket 06 (design, not decided here)

- **Licensing/permission** (research 01's *silent* grounding failures) is a frequent declarative root cause but isn't a pipeline layer. Ticket 06 decides: model it as a sub-type under Grounding/Action, or a **pre-flight "Entitlement" check** before the binary search.
- **Surface-flip** (a Finding whose fix is *migrate declarative → Copilot Studio* because a declarative ceiling is hit) is an **escalation outcome**, distinct from an in-place Change. Ticket 06 designs how it's presented.
