# Diagnose→Revise — Conversation Design (prototype)

**PROTOTYPE — reacting artifact for wayfinder ticket 06.** How the Agent Builder's new **improve/fix mode** interviews a maker and drives to a diagnosis + change-set + full revised artifact. The concrete things to react to are the **flow** (§4) and the **worked dialogue** (§7). Question being answered: *does this diagnose→revise flow feel right, and are the three handed-down decisions right?*

> **Prototype-branch note:** this is a *logic/flow* question, but — like v1's ticket-05 `conversation-design.md` — the right concrete artifact is a **flow spec + worked dialogue**, not a runnable terminal app: what's being validated is conversational UX, not a hard-to-reason state machine.

Encodes the ticket-05 domain model (`Finding` / `Change` / `Probe` / `verify-signal` / `Backlog`). Reconstructs into the AgentSpec (`../../builder-agent/templates/base-skeleton.md`); uses research 01 (taxonomy), 02 (evidence playbooks), 03 (isolation algorithm), 04 (improve levers).

## 1. Design principles (carried from v1 + new)
- **One question at a time**; minimize maker thinking; escape hatches everywhere. *(v1)*
- **Never guess-fix.** Med/Low confidence ⇒ a Probe or an exact evidence-capture ask, never a blind config change. *(ticket 05)*
- **Change nothing until the layer is isolated.** Read objective signals first; Instructions is the residual. *(research 03)*
- **Verify by signal, not vibe.** Every Change carries the objective signal that must flip. *(ticket 05)*
- **Reflect the current agent back** before diagnosing — proves the reconstruction and builds trust.

## 2. Entry fork & the two framings
Shared greet with build mode: **"Build something new, or improve/fix an agent you already have?"**

If improve/fix, detect framing from wording (or ask):
- **Troubleshoot (symptom-first)** — "What's it doing wrong?" Something is broken.
- **Improve (goal-first)** — "What do you wish it did better?" It works; make it better.

Same engine; the framing only changes the opening question and whether the assessment step isolates a *failure* (research 03) or measures against *levers* (research 04).

## 3. Quick vs guided dial
Carried from v1 — a dial, not a switch. Guided: one step per turn, each explained, defines terms (evidence, layer). Quick: batches, assumes fluency, terser probes. Deepen the moment a "quick" maker hesitates.

## 4. The diagnose→revise flow

```
D0 · Entry & framing
   - Greet fork → improve/fix. Detect troubleshoot (symptom-first) vs improve (goal-first).

D1 · Intake  (artifact REQUIRED + symptom/goal)
   - "Paste your agent's setup — the declarativeAgent.json, or the Instructions text,
      or (Copilot Studio) an export / description of its config." → the anchor.
   - Capture the symptom (troubleshoot) or the goal (improve), in the maker's words.

D2 · Reconstruct → AgentSpec
   - Parse artifact into meta/config/instructions zones; unparseable/absent → `unknown`.
   - Reflect back: "Here's what your agent does today …" (plain-language). Confirm.

D3 · Entitlement pre-check   [DECISION 1 — runs BEFORE the binary search]
   - Quick gate for SILENT access gaps (research 01): license present? knowledge source
     actually shared with the agent + permissions? action auth/consent granted?
     source in-tenant / supported? 
   - If a gap is the likely cause → that IS the Finding (fix access); skip the search for it.

D4 · Gather evidence  (per-surface playbook, research 02)
   - Surface known from D2. Ask for the right evidence + exact capture click-path:
       Copilot Studio → activity map node / "Show rationale" / Save snapshot / transcript CSV
       Declarative    → `-developer on` card  /  Agents Toolkit F5 `.txt`
   - Evidence tier (machine signal > transcript > self-report) sets the confidence ceiling.

D5 · Reproduce
   - Pin the failing case to one concrete repro prompt (from the transcript, or ask them
     to run it once). "Improve": establish/expand a tiny test set (research 04).

D6 · Binary-search the layer   (change NOTHING — research 03's 5-step)
   - Moderation → Action → Orchestration → Grounding → Instructions (residual, last).
   - Machine-signal-gated: each layer has a "tell" in the evidence. Land on ONE layer + root cause.

D7 · Confidence → propose
   - HIGH  → ONE atomic Change {layer, zone(s), before→after, rationale, verify-signal}.
   - MED/LOW → a Probe (ungrounded-OFF, moderation −1 notch, re-check params) OR an exact
               evidence-capture ask, naming the top-2 candidate layers. → loop to D4/D6.
   - Declarative ceiling hit (loop/autonomy/strict-grounding/>8k)?  [DECISION 2]
       → SURFACE-FLIP ESCALATION: "declarative can't do this, here's why" → offer to carry
         the reconstructed AgentSpec into the BUILD flow on Copilot Studio (no re-interview).

D8 · Apply & re-test
   - Maker applies the Change (or runs the Probe). Re-test the VERIFY-SIGNAL, 2–3× (probabilistic).
   - Confirm (signal flipped, starters still pass) or REVERT (flat).

D9 · Emit + Backlog + next   [DECISION 3 — ordering]
   - Emit all three: Diagnosis (symptom→root cause) + accumulated Change-set + full Revised artifact.
   - Surface remaining Backlog, ordered: (1) safety/compliance/guardrail, (2) the maker's
     REPORTED symptom, (3) rest by confidence×impact; group shared-root-cause Findings.
     Maker can reorder. → next Finding (loop to D5/D6) or close.
```

## 5. The three handed-down decisions (resolved this ticket)
1. **Licensing/permission = pre-flight Entitlement check (D3)** — runs before the binary search, because these failures are *silent* and masquerade as Grounding/Instructions problems; catching them first stops the maker rewriting instructions for a permissions gap.
2. **Surface-flip = distinct escalation that bridges into the build flow (D7)** — a re-platform isn't a one-diff edit and has no single verify-signal; reuse the reconstructed AgentSpec and hand to "build new" on Copilot Studio.
3. **Backlog order = safety-gated → reported symptom → confidence×impact (D9)** — safety first (research 04 block gate), then the maker's felt pain so they see movement, then impact; grouped by shared root cause; maker can override.

## 6. Edge & failure handling
- **Partial/garbled paste** → reconstruct what parses, mark the rest `unknown`, ask for the missing piece or proceed at capped confidence.
- **No capturable evidence** → confidence capped at self-report; offer Probes the maker can run, or the D4 capture playbook — don't guess-fix.
- **Multiple independent problems** → Backlog (D9 order), one at a time.
- **Fix adds metered capability / flips orchestration cost** → note the Copilot-Credit implication (research 04) before the maker commits.
- **Maker disagrees with the diagnosis** → treat the disagreement as a hypothesis; offer the objective Probe that settles it rather than arguing.
- **"Improve" with no test set** → offer to build a tiny one first (research 04) — you can't measure an improvement you can't re-run.
- **Reconstruction can't identify the surface** → ask one disambiguating question (autonomy? flows? external channel?) per the 01-delta rule.

## 7. Where this hands off
- Reconstruction target + zones: `../../builder-agent/templates/base-skeleton.md`. Evidence playbooks: `../research/02`. Isolation 5-step: `../research/03`. Taxonomy + entitlement causes: `../research/01`. Improve levers/eval: `../research/04`.
- **Instruction-body reuse:** the improve/fix branch is a new `# WORKFLOW` branch inside the existing shape (ROLE/OBJECTIVE/SCOPE/RESPONSE RULES/OUTPUT FORMAT/GUARDRAILS/SELF-CHECK) so it slots into `Agent/01-instructions.md` at **ticket 07**.
- Exact render of the Revised artifact (→ `declarativeAgent.json` v1.7 / CS portal steps) is **ticket 07**'s job (research 06).

## 8. Worked dialogue (guided path — troubleshoot, declarative)

> **Builder:** Welcome back! Do you want to **build a new agent**, or **improve or fix one you already have**?
> **Maker:** Fix one — my HR assistant keeps refusing questions it should answer.
> **Builder:** Let's get it sorted. Can you paste its setup? Either the `declarativeAgent.json`, or just the **Instructions** text from its config — whatever you have.
> **Maker:** *[pastes declarativeAgent.json]*
> **Builder:** Thanks. Here's what I see today: an **HR Policy Assistant**, a Microsoft 365 declarative agent, grounded in your **HR SharePoint / Policies** folder, that answers HR questions. Its scope rule says *"only answer questions about the employee handbook."* Does that match?
> **Maker:** Yes.
> **Builder:** Quick check before we dig in — is that SharePoint site shared with the agent, and can employees who hit the refusal actually open it themselves?
> **Maker:** Yes, everyone can open it, and it answers *some* questions fine.
> **Builder:** Good — so it's not a permissions gap. To see *why* it refuses, run one failing question in Microsoft 365 Copilot with **`-developer on`** at the end — it'll show a debug card. What did it refuse, and does the card show a content-filter block?
> **Maker:** I asked "how much parental leave do I get?" It said it can't help. The card shows no filter block, and it found the policy doc.
> **Builder:** That's the tell. Nothing was blocked and the right document was retrieved — so this isn't moderation or grounding. It's the **instructions**: your scope says *"only the employee handbook,"* and parental leave lives in a policy doc the agent doesn't count as "the handbook," so it refuses. **One change:** in `# SCOPE & GROUNDING`, replace *"only answer questions about the employee handbook"* with *"answer employee questions about any HR policy in the HR Policies site."* You'll know it worked when that exact question gets answered **and** an off-topic question (e.g. "write me a poem") still gets declined.
> **Maker:** Makes sense — done, and yes, it answers now and still refuses the poem.
> **Builder:** 🎯 Here's your **diagnosis** (over-tight scope → over-refusal), the **change** I made, and your full updated `declarativeAgent.json` to paste back in. *[emits all three.]* I didn't spot any other issues. Anything else to improve?

## Verdict (confirmed 2026-07-14)
The 10-step diagnose→revise flow and all three handed-down decisions are locked with the user:
- **Flow** (D0–D9): entry fork → artifact-anchored intake → reconstruct-and-reflect → entitlement pre-check → per-surface evidence → reproduce → machine-signal-gated binary search → confidence-gated propose (Change / Probe / escalation) → re-test the verify-signal → emit three-layer output + ordered Backlog. Encodes the ticket-05 model faithfully; validated by the §8 worked dialogue.
- **(1) Entitlement pre-check** runs before the binary search (silent access gaps mimic Grounding/Instructions).
- **(2) Surface-flip** is a distinct escalation that bridges into the build flow, reusing the reconstructed AgentSpec.
- **(3) Backlog order** = safety-gated → maker's reported symptom → confidence×impact, grouped by root cause, maker can reorder.
Hands to ticket 07 for the render into `Agent/` deliverables.
