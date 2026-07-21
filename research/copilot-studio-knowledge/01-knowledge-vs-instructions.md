# Knowledge as Instructions — Where's the Line?

> **Sub-question 1:** Can knowledge sources drive agent behavior the way
> instructions do? Where is the boundary?

**Verdict:** No. Instructions drive behavior; knowledge supplies facts. They are
architecturally distinct and non-interchangeable. Instructions can *point at*
knowledge and shape how its output is presented, but knowledge can never *define*
behavior.

---

## 1. Instructions are the behavior mechanism — not knowledge

Per Microsoft's authoring-instructions doc, an agent depends on **instructions**
to:

- **Decide** which resources (tools, knowledge, topics, or other agents) to call
- **Fill inputs** for any tool it invokes
- **Generate** the response

> *"Agents depend on instructions to: Decide what resources… to call… Fill inputs
> for any tool… Generate a response."*
> — [authoring-instructions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions)

Knowledge, by contrast, is **grounding data**. It supplies the content an answer
is built from; it does not decide anything.

> *"Without knowledge, the agent relies only on its general training and
> instructions."*
> — [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)

So the roles are cleanly split:

- **Knowledge** = *what the agent knows* (facts, documents, enterprise data).
- **Instructions** = *how the agent behaves* (routing, tone, formatting, flow,
  when to use which resource).

*(Verified 3-0 across four primary Microsoft Learn docs.)*

---

## 2. Instructions can *reference* knowledge — but only knowledge that exists

Instructions can direct the agent to a specific knowledge source **by name** (via
the slash `/` menu in the instructions editor, which surfaces knowledge sources
as a distinct object type). But:

> *"An agent can't act on instructions to use tools, knowledge sources… it
> doesn't have."*
> — [authoring-instructions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions)

Implication: you cannot "smuggle" knowledge into behavior through instructions,
and you cannot instruct the agent to consult a source you never attached.
Instructions and knowledge are two separate configuration surfaces that reference
each other — not one that contains the other.

---

## 3. The precise boundary: instructions shape *summarization*, not *retrieval*

This is the sharpest line in the docs, and the one most relevant to builders:

> *"Use agent instructions… to influence answer summarization after document
> retrieval… **Agent instructions can't modify search retrieval logic. Remove any
> instructions that attempt to influence document retrieval.**"*
> — [generative-mode-guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance)

So the pipeline splits into two governance zones:

```
  [ user turn ]
       │
       ▼
  ┌─────────────────────────┐
  │ RETRIEVAL                │  ← instructions CANNOT touch this
  │ (query rewrite, search,  │     (ranking, which chunks come back,
  │  ranking, top-N chunks)  │      search restriction — all automatic)
  └─────────────────────────┘
       │
       ▼
  ┌─────────────────────────┐
  │ SUMMARIZATION            │  ← instructions DO shape this
  │ (tone, formatting,       │     ("custom instructions for tone,
  │  brevity, safety)        │      formatting, safety, or brevity")
  └─────────────────────────┘
       │
       ▼
  [ grounded, cited answer ]
```

Custom instructions act at the **summarization step** — they control tone,
formatting, safety, and brevity of the answer *after* the facts are retrieved.
They do **not** control *which* facts come back or *how* they're ranked.

> *RAG doc, step 3: "Applies custom instructions for tone, formatting, safety, or
> brevity."*
> — [retrieval-augmented-generation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/retrieval-augmented-generation)

**Practical takeaway:** If you find yourself writing instructions like *"prefer
document X over document Y"* or *"search only the policy folder"*, you're trying
to influence retrieval — which won't work and which Microsoft says to remove.
Scope retrieval structurally instead (see §5 and
[03-retrieval-mechanics.md](03-retrieval-mechanics.md)).

---

## 4. You don't need to *describe* your knowledge sources in instructions

A common instinct is to list every attached source and explain it in the
instructions. Microsoft says this is unnecessary:

> *"You don't need to define the available tools or knowledge sources in the
> instructions, since this information is already available to the agent… focus
> on adding instructions only for cases where you want to give the agent hints
> when the right tool or knowledge source might be ambiguous."*
> — [generative-mode-guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance)

The orchestrator already routes using each source's **name and description**. So:

- **Don't** enumerate sources in instructions as boilerplate.
- **Do** add a disambiguation hint *only* when the correct source is genuinely
  ambiguous (e.g., "for HR policy questions use the *Employee Handbook*, not the
  *Vendor Contracts* source").

*(Minor caveat from the same doc: listing tools can still make follow-up phrasing
more natural, so "only" is slightly absolute — but the guidance direction is
clear: describe sources sparingly, and only for routing ambiguity.)*

---

## 5. How to *scope* which knowledge is used (since instructions can't)

Because instructions can't steer retrieval, scoping is done **structurally**:

- **Default:** generative orchestration searches **all** knowledge sources listed
  on the agent's Knowledge page.
- **To restrict to specific sources:** put those sources into a **generative
  answers node** inside a topic. Sources defined at the node level **override**
  the agent-level sources (which then act as a fallback).
  — [generative-mode-guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance)

This is the supported substitute for the (unsupported) instinct to steer
retrieval through instructions.

---

## Summary of the boundary

| Concern | Controlled by | Notes |
|---|---|---|
| Which resource to call | Instructions (routing) + orchestrator | Instructions add hints only when ambiguous |
| What content is retrieved | **Retrieval logic (automatic)** | Instructions **cannot** influence this |
| How chunks are ranked | **Retrieval logic (automatic)** | Instructions **cannot** influence this |
| Tone / formatting / brevity of the answer | **Instructions (summarization step)** | This is where custom instructions bite |
| Which sources are in scope | **Structure** (agent-level list vs. generative answers node) | Not instructions |
| Behavior / persona / flow | **Instructions** | Knowledge cannot define this |

**Bottom line:** Knowledge cannot act as instructions. The only overlap is that
instructions shape how retrieved knowledge is *presented* — never what is
*retrieved*.
