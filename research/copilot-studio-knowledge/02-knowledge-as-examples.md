# Knowledge as Examples / Templates — Should You?

> **Sub-question 2:** Can knowledge serve as few-shot examples or templates for
> how the agent should respond?

**Verdict:** No — this is not what knowledge is for, and Microsoft explicitly
scopes RAG away from it. Few-shot examples belong in **instructions**, not in
knowledge sources.

---

## 1. Microsoft scopes RAG to factual Q&A — not reasoning, comparison, or templating

Copilot Studio's knowledge feature is retrieval-augmented generation (RAG), and
Microsoft is explicit about what it's *for* and what it's *not* for:

> *"RAG works best for factual questions and answers, not deep document
> analysis… RAG **isn't intended for**: Full document comparison, Policy
> compliance evaluation, Complex reasoning over long unstructured documents."*
> — [retrieval-augmented-generation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/retrieval-augmented-generation)

Using knowledge as a few-shot / template mechanism falls squarely into the
"complex reasoning over documents" exclusion: you'd be asking the agent to read
example documents, infer a pattern, and reproduce it. RAG is not designed or
optimized for that.

> **Why the mechanics fight you here:** retrieval returns only the **top ~3
> chunks per source** matching the *user's query*. An "example" document isn't a
> factual answer to a user question, so it may not be retrieved at all — and even
> if it is, only a few fragments come back, not the whole exemplar. See
> [03-retrieval-mechanics.md](03-retrieval-mechanics.md).

*(Verified 3-0 against the primary RAG doc. Note: the "examples/templates"
framing is a synthesis gloss on Microsoft's documented "complex reasoning"
exclusion — it reflects design intent, not a hard technical wall. See §4.)*

---

## 2. The supported home for examples: instructions (few-shot prompting)

Microsoft's own guidance for declarative agents recommends **few-shot prompting**
— giving multiple examples to illustrate edge cases — as an **instructions**
technique, not a knowledge technique:

> Microsoft's declarative-agent guidance recommends few-shot prompting for complex
> scenarios — giving multiple examples to illustrate edge cases.
> — [declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions)

So if you want the agent to follow a response *template* or match a desired
*style*, the mechanism is:

- **Put the example(s) directly in the instructions field** as illustrative
  input→output pairs, or
- Use **topics / prompt nodes** to structure a deterministic response shape, or
- Use **prompt library / prompt components** where available.

Examples in instructions are *always in context* and *deterministically present*.
Examples in knowledge are *maybe-retrieved fragments* — the opposite of what you
want from an exemplar.

---

## 3. Why the distinction matters (mechanics, not just policy)

| | **Example in instructions** | **Example in a knowledge source** |
|---|---|---|
| Always available to the model? | Yes — instructions are always in context | No — only if retrieval surfaces it |
| Retrieved whole? | Yes | No — top ~3 chunks per source, fragmented |
| Triggered by user query relevance? | No — always applied | Yes — must match the query to be pulled |
| Optimized by Microsoft for this use? | Yes (few-shot prompting is recommended) | No (RAG is scoped to factual Q&A) |
| Deterministic shaping of response? | Strong | Weak / unreliable |

An example only works as an example if the model *reliably sees it*. Knowledge
retrieval is conditional and fragmentary by design, so it's structurally the
wrong vehicle.

---

## 4. Honest caveat: "can't" vs. "shouldn't"

- **Technically**, nothing stops you from uploading a document full of example
  Q&A pairs. General LLM behavior can still be *nudged* by whatever text lands in
  context.
- **But** Microsoft does not recommend or optimize for it, retrieval may not
  surface your examples when you need them, and you lose the determinism that
  makes examples useful.
- **Therefore** the practical answer is: **don't** use knowledge as your
  example/template mechanism. Put examples in instructions (or topics/prompt
  nodes). Reserve knowledge for facts the agent should retrieve and cite.

---

## 5. Related open question worth flagging

The research surfaced an unresolved edge worth your awareness: **can a knowledge
document that contains directive/persona text leak into behavior?** The docs
assert a clean data-vs-behavior separation but don't address
prompt-injection-via-knowledge. Two consequences:

1. It reinforces that knowledge *isn't a sanctioned behavior/example channel* —
   Microsoft treats knowledge content as data.
2. If you ingest untrusted documents, be aware that directive-looking content in
   them is a governance/security consideration, not a supported feature. (Tracked
   in [06-sources-and-open-questions.md](06-sources-and-open-questions.md).)

---

## Summary

- **Knowledge is for facts, not examples or templates.** Microsoft scopes RAG to
  factual Q&A and explicitly excludes complex reasoning over documents.
- **Few-shot examples belong in instructions** — Microsoft recommends few-shot
  prompting as an instructions technique.
- **Mechanically**, retrieval's conditional, top-N-chunk behavior makes knowledge
  an unreliable place to store exemplars.
- If you want the agent to match a template or style: **instructions, topics, or
  prompt nodes** — not knowledge.
