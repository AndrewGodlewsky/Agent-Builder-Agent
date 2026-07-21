# How Retrieval Actually Works — Grounding, RAG, and Orchestration

> **Sub-question 3:** How does retrieval work? Grounding, RAG, and when/how
> knowledge is pulled into responses.

**Verdict in one line:** Retrieval is **orchestration-driven and automatic** —
the runtime decides *per turn* whether knowledge is needed, rewrites the query,
searches configured sources (top ~3 results each), summarizes with your custom
instructions, and validates for safety before answering with citations.

---

## 1. Retrieval is decided per turn by the orchestrator

Under enhanced (generative) orchestration — the current default — the runtime
evaluates **at question time** whether knowledge is needed and which sources to
search:

> *"The enhanced orchestration runtime automatically determines which knowledge
> sources to search based on the user's question."*
> — [knowledge-copilot-studio (agents-experience)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-copilot-studio)

You do not manually wire "call knowledge here" for the default path — the
orchestrator invokes search proactively when it judges the turn needs grounding.
*(This is a shift from the older classic model where knowledge search ran only as
a fallback — see §5.)*

---

## 2. The four-step RAG pipeline

Every knowledge-grounded turn runs through four steps:

```
  ┌──────────────────────────────────────────────────────────────┐
  │ 1. QUERY REWRITING                                            │
  │    User's raw message → optimized search query                │
  │    (adds conversation context: prior turns, location, time)   │
  └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ 2. CONTENT RETRIEVAL                                          │
  │    Rewritten query runs against ALL configured sources.       │
  │    Copilot Studio pulls the TOP THREE results per source.     │
  └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ 3. SUMMARIZATION / RESPONSE GENERATION                       │
  │    Retrieved chunks → grounded answer.                        │
  │    ← YOUR CUSTOM INSTRUCTIONS apply here                       │
  │      (tone, formatting, safety, brevity)                      │
  └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ 4. SAFETY / GOVERNANCE VALIDATION                            │
  │    Grounding, provenance & relevance checks → cited answer    │
  └──────────────────────────────────────────────────────────────┘
```

> *"After rewriting the query, the system runs it against all the knowledge
> sources you set up. Copilot Studio gets the top three results from each
> source."*
> — [retrieval-augmented-generation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/retrieval-augmented-generation)

**Key consequence of "top 3 per source":** more sources ≠ more depth per source.
Each source contributes at most ~3 chunks. This is why knowledge is good for
*factual snippet retrieval* and bad for *whole-document reasoning* (see
[02-knowledge-as-examples.md](02-knowledge-as-examples.md)).

**Recall from [01](01-knowledge-vs-instructions.md):** custom instructions apply
at **step 3 only**. They cannot touch steps 1–2 (retrieval).

---

## 3. How files become retrievable (indexing)

For uploaded unstructured files:

- Files are **chunked** into pieces for faster processing and **vector-indexed**
  (semantic embeddings), stored in **Dataverse**.
- At query time, Copilot Studio retrieves the **most relevant chunks** matching
  the user's query intent, and grounds the response on them.
  — [knowledge-unstructured-data](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data)

Chunk size is **not configurable** and not published by Microsoft (per
practitioner reporting) — you cannot tune the chunking.

---

## 4. Public-website retrieval (Bing Custom Search) — a concrete pipeline

When public websites are a knowledge source, retrieval uses **Bing Custom
Search** with a pipeline that *separates retrieval from summarization*:

1. **Message moderation** on the incoming message.
2. **Query optimization** — adds conversation context (e.g., location, time).
3. **Convert to a search query** restricted to your **configured domains** only.
4. **Collate top results** with **grounding, provenance, and semantic-similarity
   cross-checks**.
5. **Summarize** into a grounded, cited response, with **relevance validation**.

> *"Copilot Studio uses retrieval augmented generation, which separates the steps
> of retrieving search results and summarizing… restricted to the customer's
> configured domains… Performs grounding check, provenance checks, and semantic
> similarity cross checks."*
> — [generative-ai-public-websites](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-ai-public-websites)

---

## 5. Fallback vs. proactive search — an important nuance

You'll see two different framings in the docs; both are correct for their
context:

- **Classic / SharePoint generative-answers wording:** knowledge search runs as a
  **fallback** — it triggers *when no topic answers* the user (and for SharePoint,
  it searches the configured URL plus all subpaths).
  — [knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)
- **Modern generative orchestration (current default):** the orchestrator invokes
  knowledge search **proactively** (via the Universal Search Tool) rather than
  strictly as a last resort.

**So:** if you're on generative orchestration, think "the orchestrator searches
knowledge whenever it judges the turn needs it," not "knowledge only fires when
topics miss." The fallback framing is *incomplete* for the modern default, not
wrong for classic.

---

## 6. Gating: "Allow ungrounded responses"

Retrieval/grounding is gated by an **Allow ungrounded responses** setting:

> *"When you turn off this setting, the agent blocks any response generated in a
> turn where it didn't use a knowledge source or tool… the fallback topic
> triggers."*
> — [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)

- **Off** → the agent *must* ground on a knowledge source or tool every turn, or
  it refuses (and routes to the fallback topic). Use this for high-assurance,
  "answer only from approved content" agents.
- **On** → the agent may answer from general model knowledge when nothing is
  retrieved. More flexible, less contained.

---

## 7. Scoping which sources are searched

- **Default:** all sources on the agent's Knowledge page are searched.
- **To restrict:** use a **generative answers node** in a topic — node-level
  sources **override** agent-level sources (agent-level then acts as fallback).
  Microsoft recommends configuring nodes with specific sources for best results.
  — [generative-mode-guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance)

Remember: this structural scoping is the **only** supported way to steer
retrieval — instructions cannot (see [01](01-knowledge-vs-instructions.md) §3).

---

## 8. A separate surface: the M365 Copilot Retrieval API

For Microsoft-365-grounded scenarios, there's a **distinct developer API** (not
the same as Copilot Studio's built-in knowledge feature):

- The **M365 Copilot Retrieval API** returns relevant text chunks from the **same
  hybrid index that powers M365 Copilot** — using query understanding and query
  transformations "more difficult to achieve with lexical search or even basic
  RAG."
- It grounds from **SharePoint, OneDrive, and Copilot connectors** *without
  re-indexing or duplicating data*, supports natural-language queries, and can be
  scoped with **Keyword Query Language (KQL)** to filter by URL, date range, and
  file type.
  — [M365 Copilot Retrieval API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview)

**Don't conflate the two.** Copilot Studio's built-in knowledge is the
point-and-click feature; the Retrieval API is a code path for custom grounding at
scale. Which to use is an open design question (see
[06-sources-and-open-questions.md](06-sources-and-open-questions.md)).

---

## Summary

- Retrieval is **automatic and orchestration-driven** — decided per turn.
- **Four steps:** query rewrite → retrieve (top 3/source) → summarize (your
  instructions apply here) → safety validate.
- Files are **chunked + vector-indexed in Dataverse**; chunking isn't tunable.
- **Top-3-per-source** is the defining constraint — favors snippet facts, not
  whole-document reasoning.
- **Scope structurally** (generative answers node), not via instructions.
- **`Allow ungrounded responses`** decides whether the agent may answer without
  grounding.
- The **M365 Retrieval API** is a separate, code-level grounding surface.
