# The AgentSpec Base Skeleton

The AgentSpec is the surface-agnostic build specification — the invariant structure that every agent archetype and every agent the builder emits is constructed from. It is a hybrid structured spec: a structured *config envelope* plus a free-text *instruction body*, following Microsoft's proven Markdown pattern. This single source of truth renders either to a `declarativeAgent.json` for Microsoft 365 (M365) or to click-by-click portal steps for Copilot Studio. Consult this document whenever you need the canonical shape of an agent definition, the field-by-field structure of the config and instruction zones, or the mapping between a maker's answers and the fields they populate.

## 1. The AgentSpec structure (config envelope + instruction body)

The AgentSpec (the surface-agnostic build spec) has two zones. The `config` envelope holds everything that maps to a manifest or portal configuration field. The `instructions` body holds the free-text Markdown prose. The annotated YAML below is the complete skeleton.

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

instructions: |    # [core] the free-text Markdown body — see section 2
  # ROLE ...
```

### The two-zone rule for placing content

The AgentSpec enforces one placement rule across its two zones. Anything that is a *manifest or portal field* — name, description, knowledge, capabilities, actions, conversation starters — lives in `config`. Anything that is *instruction prose* lives in `instructions`. Items defined in `config` are then **referenced by their exact name inside** `instructions` (for example, "Use `ServiceNow KB`…").

## 2. The instruction-body template (Markdown headers)

The `instructions` body of the AgentSpec is free-text Markdown organized under a fixed set of headers, following Microsoft's recommended shape. In the template below, **[core]** marks headers that are essentially always present; **[conditional]** marks headers to include only when the scenario warrants them (omit them to conserve the 8,000-character M365 instruction budget).

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

### Guardrails on writing the instruction body

When authoring the instruction body, three constraints protect the agent. Never try to alter the citation format in prose. Never offload instructions into a knowledge document, which invites a cross-prompt injection attack (XPIA). And keep the whole instruction body at or below 8,000 characters for the declarative surface.

## 3. Element to skeleton-zone to surface mapping

This reference table maps each of the 13 agent-design elements to the AgentSpec zone that carries it, and shows how that zone renders on each surface — Microsoft 365 declarative agents and Copilot Studio. Use it to locate where any given element lives and how it appears once deployed.

| # | Element | Zone | M365 declarative | Copilot Studio |
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

## 4. How a maker's interview answers map to AgentSpec fields

When the builder interviews a maker, each question it asks fills specific AgentSpec fields. This reference table is the contract that the interview fills, in order — it shows which question populates which `meta`, `config`, or `instructions` field.

| Builder asks the maker… | Fills |
|---|---|
| "What should this agent do, in one sentence?" | `meta.name`, `meta.description`, `# OBJECTIVE` |
| "Who will use it, and how technical are they?" | `meta.audience`, `# ROLE`, tone in `# OUTPUT FORMAT` |
| "What should it stick to — and refuse?" | `# SCOPE`, `# GUARDRAILS` |
| "What information should it draw from?" | `config.knowledge[]`, `# CAPABILITIES` |
| "Does it need to *do* anything (send, create, look up live data)?" | `config.actions[]` → forces surface; `# WORKFLOW` |
| "Any must-follow rules or house style?" | `# RESPONSE RULES`, `# OUTPUT FORMAT` |
| "Any jargon it must know?" | `# VOCABULARY` |
| "Give me 3 things a user might open with." | `config.conversationStarters[]` |
| (derived) surface decision | `meta.surface` |

### Why the surface is derived, not asked

The `meta.surface` value is **derived, not asked** early in the interview. If any of the maker's answers imply autonomy, multi-step or looped orchestration, deterministic flows, multi-agent coordination, external channels, group use, strict grounding, a custom model, or Dataverse, then the surface is `copilot-studio`. Otherwise it is `declarative`.

## 5. Worked micro-example: an HR Policy Assistant

This worked example instantiates the AgentSpec for a simple read-only Q&A agent, confirming that the skeleton scales down cleanly. It uses only 7 of the 13 design elements; the 6 conditional elements are correctly omitted. Because the agent runs in-M365 with single-step retrieval and individual use, and has no actions, its surface stays `declarative`.

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
