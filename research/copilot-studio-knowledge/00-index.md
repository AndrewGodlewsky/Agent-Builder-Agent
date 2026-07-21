# Copilot Studio: How Knowledge Is Used — Research Index

**Research question:** How is knowledge used in Microsoft Copilot Studio agents,
and *can/should* knowledge be used as instructions or examples?

**Context:** Compiled to inform an actively-in-development Copilot Studio agent
(and the Agent-Builder-Agent's guidance to makers). All primary claims are drawn
from first-party Microsoft Learn documentation and passed 3-0 unanimous
adversarial verification. Most cited pages were updated between 2026-02 and
2026-07. **Copilot Studio evolves fast — re-verify exact limits against live docs
before you build.**

Research date: 2026-07-21.

---

## The short answer

**No — knowledge should not be used as instructions, and should not be used as
examples/templates.** They are architecturally distinct surfaces:

| | **Instructions** | **Knowledge** |
|---|---|---|
| Purpose | Drive *behavior* | Supply *facts* |
| What it controls | Which resources to call, how to fill tool inputs, how to generate/shape the response | Content retrieved via RAG to ground answers |
| Analogy | The agent's operating manual | The agent's reference library |
| Can it define behavior? | Yes — this is its whole job | No |
| Can it be a few-shot example set? | Yes (examples go *in instructions*) | No — RAG is scoped to factual Q&A |

Knowledge **cannot** substitute for instructions (it can't define behavior), and
instructions **cannot** invoke knowledge that isn't attached to the agent. The
one nuance: instructions govern *summarization, tone, and flow after retrieval*
but **cannot modify retrieval logic itself** — Microsoft advises removing any
instruction that tries to influence document retrieval.

---

## Documents in this set

1. **[00-index.md](00-index.md)** — this file (overview + short answer).
2. **[01-knowledge-vs-instructions.md](01-knowledge-vs-instructions.md)** —
   Sub-question 1. The architectural line: what instructions do, what knowledge
   does, where they meet, and where instructions must *not* reach.
3. **[02-knowledge-as-examples.md](02-knowledge-as-examples.md)** —
   Sub-question 2. Why knowledge is the wrong vehicle for few-shot
   examples/templates, and the supported alternative (examples belong in
   instructions).
4. **[03-retrieval-mechanics.md](03-retrieval-mechanics.md)** —
   Sub-question 3. How retrieval actually works: orchestration-driven RAG, the
   four-step pipeline, per-source retrieval, gating, and the fallback vs.
   proactive-search nuance.
5. **[04-knowledge-types-and-limits.md](04-knowledge-types-and-limits.md)** —
   Sub-question 4. Supported source types, per-source input counts, hard quotas,
   SharePoint license gating, and permission trimming.
6. **[05-builder-recommendations.md](05-builder-recommendations.md)** —
   Practical, decision-oriented guidance for building an agent now: what goes
   where, common anti-patterns, and a config checklist.
7. **[06-sources-and-open-questions.md](06-sources-and-open-questions.md)** —
   Full citation list, verification notes, caveats, and unresolved questions
   worth checking before you commit to a design.
8. **[07-source-and-file-types-pros-cons.md](07-source-and-file-types-pros-cons.md)** —
   Follow-up. Every knowledge **source type** (website, uploaded files,
   OneDrive/SharePoint sync, SharePoint connector, Dataverse, connectors, 3rd-party
   KBs) and every supported **file/document format**, each with concrete pros/cons
   and a decision cheat-sheet.

---

## How to read this if you're short on time

- **Just want the ruling?** This page's short-answer table.
- **Building right now?** Jump to [05-builder-recommendations.md](05-builder-recommendations.md).
- **Need to defend the decision to a stakeholder?** [01](01-knowledge-vs-instructions.md)
  + [06](06-sources-and-open-questions.md) have the primary-source quotes.
