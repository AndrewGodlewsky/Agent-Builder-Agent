---
name: project-diagnostic-domain-model
description: The diagnose→revise domain model (ubiquitous language) for the builder's improve/fix mode
metadata:
  type: project
---

The Agent Builder's **improve/fix mode** reasons over this fixed vocabulary (set in wayfinder ticket 05; shipped as `Agent/knowledge/05-diagnostics.md`). Use these terms exactly.

- **Finding** — the core unit: `{symptom, isolated layer, root cause, confidence, proposed Change OR Probe}`. Worked in a **single-Finding loop** (fix one, re-test, repeat) with a **Backlog** of other suspected Findings surfaced but not yet worked.
- **Diagnostic layer** — the five, isolation-ordered: **Moderation → Action → Orchestration → Grounding → Instructions**. Instructions is the **residual**, diagnosed **last** (it has no machine signal; the other four do).
- **Evidence** — tiered: *Machine signal* (dev-mode card / activity-map node / error code) > *Transcript* > *Self-report*. The tier sets the **confidence ceiling**.
- **Confidence** — High/Med/Low. **High** ⇒ propose a Change. **Med/Low** ⇒ a **Probe** or an exact evidence-capture ask — **never a guess-fix**.
- **Change** — atomic per Finding: `{layer, zone(s), before→after, rationale, verify-signal}`; one per re-test cycle. **Verify-signal** = the objective signal that must flip (function now *Selected*, node cites right source, no `ContentFiltered`) — never "the answer looks better."
- **Artifact / Reconstruction** — the maker's pasted config+instructions is the **required anchor**; reconstruct it fully into the [[project-agentspec-hybrid-decision]] AgentSpec (gaps → `unknown`), zoom diagnosis on the suspected zone.

**Three flow decisions (ticket 06):** (1) a pre-flight **Entitlement check** (silent license/permission gaps) runs *before* the binary search; (2) **surface-flip** (declarative ceiling → Copilot Studio) is a distinct **escalation** that bridges into the build flow, not an in-place Change; (3) **Backlog order** = safety/compliance → the maker's reported symptom → confidence×impact.

Output contract, every fix: **diagnosis + change-set + full revised artifact**. Effort: [[project-agent-builder-overview]] (v2, CLOSED). Design: `.scratch/builder-agent-v2/`.
