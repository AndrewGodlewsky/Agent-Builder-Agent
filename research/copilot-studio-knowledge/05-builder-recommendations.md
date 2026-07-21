# Builder Recommendations — Applying This to Your Agent

> Decision-oriented guidance for someone actively building a Copilot Studio agent.
> Synthesized from the findings in docs 01–04.

---

## The one rule to internalize

> **Knowledge = facts the agent retrieves and cites.
> Instructions = behavior, routing, tone, and any examples/templates.**

If you catch yourself putting behavior, persona, style, or examples *into a
knowledge source*, stop — it belongs in instructions (or topics/prompt nodes).
If you catch yourself trying to steer *which documents get retrieved* from
instructions, stop — that's structural config (a generative answers node), not
instructions.

---

## What goes where — a placement table

| You want the agent to… | Put it in… | Why |
|---|---|---|
| Answer questions from your docs/policies/site | **Knowledge source** | That's exactly what RAG is for |
| Follow a persona, tone, or brand voice | **Instructions** | Behavior, not facts |
| Match a specific response *format/template* | **Instructions** (or a topic/prompt node) | Examples must be deterministically in-context |
| Handle edge cases via examples | **Instructions** (few-shot prompting) | Microsoft's recommended technique |
| Route to the right source when ambiguous | **Instructions** (a short hint) | Only when genuinely ambiguous |
| Restrict a turn to specific sources | **Generative answers node** (topic) | Instructions can't steer retrieval |
| Force "answer only from approved content" | **`Allow ungrounded responses` = off** | Governance gate |
| Decide *what* is retrieved / ranked | *(you can't — it's automatic)* | Retrieval logic is not author-controllable |

---

## Anti-patterns to avoid (all sourced from the research)

1. **❌ Writing retrieval-steering instructions.**
   e.g. *"Always prefer the 2025 policy doc"* or *"search only the HR folder."*
   Microsoft says instructions **can't** modify retrieval and to **remove** such
   instructions. → Scope with a generative answers node instead.
   *(See [01](01-knowledge-vs-instructions.md) §3, §5.)*

2. **❌ Storing examples/templates as knowledge documents.**
   RAG is scoped to factual Q&A; retrieval is conditional + fragmentary
   (top-3-chunks), so your exemplars may never surface. → Put examples in
   instructions. *(See [02](02-knowledge-as-examples.md).)*

3. **❌ Enumerating/describing every knowledge source in instructions.**
   The orchestrator already routes on source names + descriptions. Boilerplate
   listings waste instruction space. → Add a hint *only* for real ambiguity.
   *(See [01](01-knowledge-vs-instructions.md) §4.)*

4. **❌ Dumping hundreds of sources for "coverage."**
   Retrieval pulls only ~3 chunks per source; volume dilutes rather than deepens.
   → Curate; give each source a clear, distinct name + description.
   *(See [03](03-retrieval-mechanics.md) §2, [04](04-knowledge-types-and-limits.md) §6.)*

5. **❌ Assuming knowledge can enforce persona/behavior.**
   Knowledge is data; it cannot define behavior. Behavior lives in instructions.
   *(See [01](01-knowledge-vs-instructions.md) §1.)*

6. **❌ Planning around large SharePoint docs without checking licensing.**
   Without a same-tenant M365 Copilot license, generative answers cap SharePoint
   files at **7 MB** (vs. 200 MB with it). → Verify tenant licensing first.
   *(See [04](04-knowledge-types-and-limits.md) §4.)*

---

## Config decisions for your build

Make these explicit choices, not defaults-by-accident:

- **Orchestration mode → Generative** (recommended for knowledge-heavy agents):
  more inputs, proactive automatic retrieval, node-level scoping.
- **`Allow ungrounded responses`:**
  - **Off** if the agent must only answer from approved content (high assurance;
    it will refuse + hit the fallback topic when it can't ground).
  - **On** if you want it to fall back to general model knowledge.
- **Source curation:** name and describe each source clearly (this is what the
  orchestrator routes on). Prefer a few authoritative sources over many.
- **Scoping:** if certain topics must only draw from certain sources, build a
  **generative answers node** with those sources for the relevant topic.
- **SharePoint:** confirm permission-trimming expectations (test as a
  regular-permission user, not just an admin) and confirm the file-size ceiling
  your licensing allows.

---

## A quick build checklist

- [ ] Behavior, persona, tone, and examples are in **instructions** — not in
      knowledge.
- [ ] No instruction tries to steer *which* documents are retrieved.
- [ ] Retrieval scoping (if needed) is done via **generative answers nodes**.
- [ ] Each knowledge source has a clear, distinct **name + description**.
- [ ] Sources are **curated**, not dumped (remember top-3-chunks-per-source).
- [ ] `Allow ungrounded responses` is set deliberately for your assurance level.
- [ ] SharePoint sources: licensing + file-size ceiling + permission-trimming all
      confirmed.
- [ ] You're within the caps (500 sources / 500 files / etc.) — verified against
      **live** docs, since quotas shift.
- [ ] If you need large-scale/custom retrieval, you've evaluated the **M365
      Retrieval API / Azure AI Search** path vs. built-in knowledge.

---

## If you specifically need example-driven / templated responses

Since knowledge is the wrong vehicle, use one of these supported paths:

1. **Few-shot examples in instructions** — input→output pairs directly in the
   instructions field (Microsoft's recommended technique for edge cases).
2. **Topics + prompt nodes** — for deterministic, structured response shapes.
3. **Prompt library / prompt components** — where available in your environment.

*(Note: the research flagged an open question about the exact best supported
mechanism for template responses — see
[06-sources-and-open-questions.md](06-sources-and-open-questions.md). Prototype
the instructions-based approach first; it's the documented path.)*
