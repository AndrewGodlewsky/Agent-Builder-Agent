# Builder Agent — Conversation Design (prototype)

**PROTOTYPE — reacting artifact for wayfinder ticket 05.** How the builder agent interviews a maker and drives to ready-to-paste artifacts. The concrete thing to react to is the **flow** (§3) and the **worked dialogue** (§6). Question being answered: *does this interview flow feel right for a mixed audience?*

Fills the AgentSpec via the question→field contract in `../templates/base-skeleton.md` §4, choosing/tailoring an archetype from `../templates/archetypes/library.md`.

## 1. Design principles
- **One question at a time.** Never bombard; each turn advances one field (MS best practice).
- **Minimize maker thinking.** Offer concrete options and a recommended default on every choice; accept "you decide."
- **Derive, don't ask, the surface.** The maker never picks declarative vs. Copilot Studio — it's inferred (01-delta rule) and *explained* once.
- **Show, don't quiz.** Reflect progress back as a growing plain-language summary, not jargon.
- **Escape hatches everywhere.** "Not sure" / "skip" / "you decide" always work.

## 2. Skill-level detection & the two paths
Detect early, adapt depth — never label the maker out loud.

**Signals:** an explicit opening offer ("I can keep this quick, or walk you through it — which do you prefer?") *plus* inferred signals (does the maker use terms like "manifest", "connector", "Power Automate"? did they name a surface? are answers terse and precise?).

| | **Guided path** (default; non-technical signals) | **Quick path** (technical signals / maker asks) |
|---|---|---|
| Pace | one field per turn, each explained in plain language | batches related fields; skips explanations |
| Concepts | defines knowledge/action/guardrail as it goes | assumes fluency |
| Defaults | recommends + explains why | recommends tersely |
| Surface | explains the choice in a sentence | states it |

The path is a **dial, not a switch** — the builder can deepen explanation the moment a "quick" maker hesitates, and speed up if a "guided" maker races ahead.

## 3. The interview flow

```
Phase 0 · Greet & calibrate
  - Greet; state what the builder produces (a ready-to-paste agent design).
  - Offer quick vs guided; read skill signals. Set path (dial).

Phase 1 · Goal capture            → meta.name, meta.description, # OBJECTIVE
  - "In a sentence, what should your agent do?"
  - Reflect back a draft name + one-line purpose for confirmation.

Phase 2 · Archetype match          → picks A–F as starting point
  - Match the goal to the nearest archetype; propose it:
    "This sounds like a Knowledge Q&A assistant — want to start there?"
  - If none fit → F (compose-from-scratch). Maker can always override.

Phase 3 · Fill the spec (per §4 mapping, one field/turn on guided)
  a. Audience & tone             → meta.audience, # ROLE, # OUTPUT FORMAT
  b. Scope & refusals            → # SCOPE, # GUARDRAILS
  c. Knowledge sources           → config.knowledge[], # CAPABILITIES
  d. Actions / "does it DO things?" → config.actions[]  (⇒ surface signal)
  e. House rules / jargon        → # RESPONSE RULES, # VOCABULARY (if any)
  f. Conversation starters       → config.conversationStarters[] (offer 3 drafts)
  (archetype pre-fills these; the builder confirms/edits rather than asking cold)

Phase 4 · Surface derivation & explain   → meta.surface
  - Apply 01-delta rule to the answers.
  - Tell the maker which surface and why, in one sentence.

Phase 5 · Review & revise
  - Show the full AgentSpec as a plain-language summary.
  - "Change anything?" loop until the maker is happy.

Phase 6 · Emit artifacts            → hands to render (ticket 07)
  - Declarative → declarativeAgent.json (+ apiPlugin.json) to copy.
  - Copilot Studio → click-by-click portal steps.
  - Include an assembly checklist.
```

## 4. Edge & failure handling
- **Vague goal** ("make me an AI helper") → offer the archetype menu as concrete examples to react to.
- **"I don't know what I want"** → walk the archetypes with one-line use-cases; let them pick a nearest.
- **Out-of-scope ask** (build something non-agent) → politely decline, restate what the builder does.
- **Capability that flips the surface** (e.g. adds an autonomous trigger mid-way) → note the surface change and why, confirm the maker still wants it.
- **Over-broad knowledge** ("all our SharePoint") → nudge to scope tighter ("less is more").
- **Declarative body > 8,000 chars** → warn, offer to trim conditional sections or move to Copilot Studio.
- **Consequential action** → ensure the emitted instructions include a confirm-before-acting rule.

## 5. Where this hands off
- Archetype pre-fills come from `../templates/archetypes/library.md`.
- Field semantics + surface rule from `../templates/base-skeleton.md` §4 and research 01.
- Phase 6 render format is **ticket 07's** job (uses research 06); this spec only defines *when* emission happens and what's produced.

## 6. Worked dialogue (guided path — non-technical maker)

> **Builder:** Hi! I help you design an agent you can drop straight into Microsoft 365 or Copilot Studio. I can keep this quick, or walk you through step by step — which sounds better?
> **Maker:** Walk me through it, I've never done this.
> **Builder:** Happy to. In one sentence, what would you like your agent to do?
> **Maker:** Answer HR questions for our staff from our policy documents.
> **Builder:** Great — so something like an **"HR Policy Assistant"** whose job is *answering staff HR questions from official policy docs.* Sound right?
> **Maker:** Yes.
> **Builder:** That's a classic **Knowledge Q&A** agent — I'll start from that template so we skip the boilerplate. First, who'll use it, and should it sound formal or friendly?
> **Maker:** All employees. Friendly but professional.
> **Builder:** Got it. Where should it get its answers? For example a SharePoint site or folder where your HR policies live.
> **Maker:** Our HR SharePoint, the Policies folder.
> **Builder:** Perfect — I'll point it only there, so it won't guess from outside that folder. Should it refuse anything outside HR policy?
> **Maker:** Yes, HR only.
> **Builder:** Does it need to *do* anything — submit a request, look up someone's record — or just answer questions?
> **Maker:** Just answer.
> **Builder:** Then this fits a **Microsoft 365 declarative agent** — the lighter option, because it only reads documents and answers, no live actions. Here are three example questions I'll add as starters: *"How many vacation days do I get?"*, *"What's the parental leave policy?"*, *"How do I submit expenses?"* — keep these?
> **Maker:** Yes.
> **Builder:** Here's your agent 👇 [plain-language summary of the AgentSpec]. Change anything?
> **Maker:** Looks good.
> **Builder:** Done. I'll give you a `declarativeAgent.json` file to paste in, plus a 4-step checklist to publish it in Microsoft 365. Ready?

## Verdict (confirmed)
The flow fills every AgentSpec field via the §4 contract, keeps surface derivation invisible-until-explained, and degrades gracefully on the listed edges. Decisions locked with the user:
- **(a) Opening = goal-first → suggest.** The builder asks what the maker wants, then proposes the nearest archetype (not a menu-first pick). Confirmed.
- **(b) Phase 5 review** = a plain-language summary of the whole AgentSpec + a "change anything?" revise loop until the maker is happy. Kept lightweight, no field-by-field re-read.
- **(c) Quick path keeps Phase 2** but as a single one-line archetype suggestion the maker can accept in one word — it doesn't skip the match, just compresses it.
