# Base Skeleton — the AgentSpec

**Layer 1 of the template library.** The invariant structure every archetype (layer 2) and every agent the builder emits is built from. Resolves wayfinder ticket 03.

Form: **hybrid structured spec** — a structured *config envelope* plus a free-text *instruction body* in Microsoft's proven Markdown pattern. One surface-agnostic source of truth that renders to a `declarativeAgent.json` (M365) or to click-by-click portal steps (Copilot Studio). See `research/02-what-makes-agent-good.md` §6 (elements) and §7 (form rationale).

---

## 1. The AgentSpec structure

```yaml
# ── AgentSpec v1 ─────────────────────────────────────────────
meta:
  name:            # display name.  M365: manifest name (≤100). CS: agent name
  description:     # one-liner. M365: ≤1,000 chars
  surface:         # declarative | copilot-studio   (choose via 01-delta rule)
  audience:        # (optional) who the agent serves — drives tone/scope

config:            # the "envelope" — maps to manifest/portal config, NOT prose
  knowledge:       # [conditional] grounding sources; "less is more"
    - type:        # sharepoint | onedrive | graph-connector | web | file | dataverse
      ref:         # site / url / connection id
      scope:       # folder / KQL filter / channel  (tight scope beats broad)
      official:    # (optional, classic orchestration only) trust without verify
  capabilities:    # [conditional] declarative only: web_search | code_interpreter |
                   #   image_generator | ...  (CS: enabled via features/tools instead)
  actions:         # [conditional] things the agent can DO
    - name:        # exact name (referenced verbatim in instructions)
      type:        # api-plugin | connector | flow | mcp
      ref:         # plugin/openapi/flow id
      consequential: # true for any create/update/delete (M365: isConsequential)
  conversationStarters:  # [core] min 3, reflect core capabilities
    - title:
      text:

instructions: |    # [core] the free-text Markdown body — see §2
  # ROLE ...
```

**Two zones, one rule:** anything that is a *manifest/portal field* (name, description, knowledge, capabilities, actions, starters) lives in `config`; anything that is *instruction prose* lives in `instructions`. `config` items are **referenced by exact name inside** `instructions` (e.g. "Use `ServiceNow KB`…").

---

## 2. The instruction-body template

Markdown headers, following Microsoft's recommended shape. **[core]** = essentially always; **[conditional]** = include when the scenario warrants (omit to save the 8,000-char M365 budget).

```markdown
# ROLE                     [core]   — identity + expertise ("You are …")
# OBJECTIVE                [core]   — the single primary job
# SCOPE & GROUNDING        [core]   — in-scope topics; ground ONLY in configured
                                      knowledge/actions; "only respond to X"
# RESPONSE RULES           [core]   — behavioral rules: one question at a time,
                                      confirm before consequential actions, atomic tasks
# OUTPUT FORMAT            [core]   — Output Contract: tone, verbosity, format
                                      (bullets/tables), include/exclude, example shape
# CAPABILITIES & KNOWLEDGE [core]   — when to use each `named` source/action/capability
# WORKFLOW                 [cond.]  — sequential procedures ONLY; each step =
                                      **Goal / Action / Transition**; atomic; Markdown
# GUARDRAILS & FALLBACK    [core]   — out-of-scope refusal + route-to-human;
                                      injection constraints; (CS: moderation posture +
                                      edit the Fallback *topic*, not this text)
# VOCABULARY               [cond.]  — acronyms, formulas, org-specific terms
# EXAMPLES                 [cond.]  — few-shot: valid + invalid, for edge cases
# SELF-CHECK               [cond.]  — "before finalizing, confirm …"
# FOLLOW-UP & CLOSING      [cond.]  — missing-data behavior, next-step suggestions
```

**Guardrail on the guardrails:** never try to alter citation format in prose, never offload instructions into a knowledge doc (XPIA), and keep the whole body ≤ 8,000 chars for the declarative surface.

---

## 3. Element → skeleton-zone → surface mapping

| # | Element (from research 02 §6) | Zone | M365 declarative | Copilot Studio |
|---|---|---|---|---|
| 1 | Role / Persona | instructions `# ROLE` | Purpose component | Instructions header |
| 2 | Purpose / Objective | instructions `# OBJECTIVE` | Purpose | Instructions |
| 3 | Scope & grounding | instructions `# SCOPE` | ground in Knowledge/Actions | "Constraints"; add tools first |
| 4 | Response rules | instructions `# RESPONSE RULES` | General guidelines | Instructions |
| 5 | Tone / output format | instructions `# OUTPUT FORMAT` | General guidelines | "Response format" |
| 6 | Capability/knowledge/tool refs | **config** + referenced in `# CAPABILITIES` | `` `backtick` `` names | `/` inline, exact names |
| 7 | Workflow steps | instructions `# WORKFLOW` | `# WORKFLOW` G/A/T | ordered instructions / Topic |
| 8 | Guardrails & fallback | instructions `# GUARDRAILS` (+ config posture) | Restrictions; RAI | Fallback **topic**; moderation |
| 9 | Vocabulary | instructions `# VOCABULARY` | Nonstandard terms | "Guidance" hints |
| 10 | Examples | instructions `# EXAMPLES` | Interaction examples | dedicated Topic |
| 11 | Self-check | instructions `# SELF-CHECK` | self-eval gate | instruction-level |
| 12 | Conversation starters | **config** `conversationStarters` | manifest starters (min 3) | suggested prompts |
| 13 | Error / follow-up | instructions `# FOLLOW-UP` | error handling | follow-up (needs ungrounded ON) |

---

## 4. How a maker's conversation answers map to fields

This table is the contract the builder's interview (ticket 05) fills, in order:

| Builder asks the maker… | Fills |
|---|---|
| "What should this agent do, in one sentence?" | `meta.name`, `meta.description`, `# OBJECTIVE` |
| "Who will use it, and how technical are they?" | `meta.audience`, `# ROLE`, tone in `# OUTPUT FORMAT` |
| "What should it stick to — and refuse?" | `# SCOPE`, `# GUARDRAILS` |
| "What information should it draw from?" | `config.knowledge[]`, `# CAPABILITIES` |
| "Does it need to *do* anything (send, create, look up live data)?" | `config.actions[]` → **forces surface** via 01-delta rule; `# WORKFLOW` |
| "Any must-follow rules or house style?" | `# RESPONSE RULES`, `# OUTPUT FORMAT` |
| "Any jargon it must know?" | `# VOCABULARY` |
| "Give me 3 things a user might open with." | `config.conversationStarters[]` |
| (derived) surface decision | `meta.surface` |

Surface is **derived, not asked** early: if any answer implies autonomy, multi-step/looped orchestration, deterministic flows, multi-agent, external channels, group use, strict grounding, custom model, or Dataverse → `copilot-studio`; else `declarative` (see research 01).

---

## 5. Worked micro-example (validates the skeleton instantiates)

```yaml
meta:
  name: HR Policy Assistant
  description: Answers employee questions about Contoso HR policies from official docs.
  surface: declarative        # in-M365, single-step retrieval, individual use → declarative
  audience: All Contoso employees (non-technical)
config:
  knowledge:
    - type: sharepoint
      ref: https://contoso.sharepoint.com/sites/HR
      scope: /Policies
  capabilities: []
  actions: []                 # read-only Q&A → no actions → stays declarative
  conversationStarters:
    - {title: Leave policy, text: How many vacation days do I get?}
    - {title: Parental leave, text: What is the parental leave policy?}
    - {title: Expenses, text: How do I submit an expense claim?}
instructions: |
  # ROLE
  You are the Contoso HR Policy Assistant, an expert on Contoso's HR policies.
  # OBJECTIVE
  Answer employee questions accurately using only official HR policy documents.
  # SCOPE & GROUNDING
  Only answer questions about Contoso HR policy, grounded in the `HR Policies` SharePoint
  site. If asked anything else, say you can only help with HR policy.
  # RESPONSE RULES
  Ask one clarifying question at a time when a request is ambiguous. Do not speculate.
  # OUTPUT FORMAT
  Concise, friendly, plain language. Use short bullet lists for multi-part answers.
  # CAPABILITIES & KNOWLEDGE
  Use the `HR Policies` SharePoint site for every factual answer.
  # GUARDRAILS & FALLBACK
  If a policy isn't in the documents, say so and suggest contacting HR — never invent one.
```

The example uses 7 of 13 elements; the 6 conditional ones are correctly omitted. This confirms the skeleton scales down cleanly — the property archetypes (ticket 04) will need.

---

## Open follow-ons handed to later tickets
- **Ticket 04** instantiates archetypes on this skeleton (pre-filling `config` + `instructions`).
- **Ticket 05** turns §4 into the actual interview flow.
- **Ticket 07** specifies the exact render from AgentSpec → `declarativeAgent.json` (v1.7) and → Copilot Studio portal steps, using research 06.
