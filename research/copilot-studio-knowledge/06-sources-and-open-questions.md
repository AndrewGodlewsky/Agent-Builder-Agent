# Sources, Verification Notes & Open Questions

> Provenance and confidence for the findings in docs 00–05, plus unresolved
> questions worth checking before you commit to a design.

---

## Research method

- **Approach:** deep-research harness — fan-out web searches across 5 angles →
  fetch top sources → extract falsifiable claims → **3-vote adversarial
  verification** per claim (a claim survives only if not refuted 2-of-3) →
  synthesize + dedupe.
- **Scale:** 5 search angles, 17 sources fetched, 83 claims extracted, **25
  claims verified → 25 confirmed, 0 refuted, 0 unverified**, 11 findings after
  synthesis/dedup. 99 agent calls total.
- **Confidence:** every retained claim is backed by **primary first-party
  Microsoft documentation** and passed **3-0 unanimous** verification with high
  verifier confidence.
- **Research date:** 2026-07-21.

---

## Primary sources (Microsoft first-party)

| # | URL | Angle | Used for |
|---|---|---|---|
| P1 | [authoring-instructions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions) | Instructions vs. knowledge | Instructions drive behavior; can't reference unattached knowledge |
| P2 | [generative-mode-guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance) | Instructions vs. knowledge | Instructions shape summarization not retrieval; don't list sources; scoping via nodes |
| P3 | [knowledge-copilot-studio (agents-experience)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-copilot-studio) | Knowledge overview | Orchestrator auto-selects sources; `Allow ungrounded responses` |
| P4 | [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio) | Knowledge types | Five source types; per-mode input counts; knowledge = grounding data |
| P5 | [retrieval-augmented-generation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/retrieval-augmented-generation) | RAG mechanics | Four-step pipeline; top-3-per-source; RAG *not* for reasoning; SharePoint 7/200 MB; file/table limits |
| P6 | [generative-ai-public-websites](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-ai-public-websites) | RAG mechanics | Bing Custom Search pipeline; retrieval/summarization separation |
| P7 | [M365 Copilot Retrieval API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview) | RAG mechanics | Separate API; hybrid index; KQL scoping |
| P8 | [requirements-quotas](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas) | Limits | 500 sources / 500 files; 25 SharePoint URLs; 7/200 MB gating (updated 2026-07-21) |
| P9 | [knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint) | Limits / security | Permission-trimming; identity-based retrieval; fallback search |
| P10 | [knowledge-unstructured-data](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data) | Retrieval | File chunking + vector indexing in Dataverse |
| P11 | [declarative-agent-instructions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions) | Examples | Few-shot prompting is an *instructions* technique |
| P12 | [nlu-boost-node](https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-boost-node) | Config | Generative answers node behavior |
| P13 | [Power Platform blog: Knowledge in Copilot Studio](https://www.microsoft.com/en-us/power-platform/blog/2025/03/27/knowledge-in-microsoft-copilot-studio/) | Practitioner | Knowledge overview (first-party blog) |

## Secondary sources (practitioner blogs — corroborating, not load-bearing)

| URL | Note |
|---|---|
| [ciaops.com — crafting effective instructions](https://blog.ciaops.com/2025/08/06/crafting-effective-instructions-for-copilot-studio-agents/) | Instructions define behavior; reference knowledge by name |
| [forwardforever.com — knowledge sources vs. MCP](https://forwardforever.com/knowledge-sources-vs-model-context-protocol-mcp-which-powers-your-copilot-studio-agent-better/) | RAG indexes docs/URLs, retrieves snippets at runtime |
| [cloudwithsingh.ca — knowledge sources field notes](https://cloudwithsingh.ca/field-notes/copilot-studio-knowledge-sources) | Chunking non-configurable/unpublished |
| [ml6.eu — Copilot RAG made easy](https://www.ml6.eu/en/blog/copilot-rag-made-easy) | RAG walkthrough |

---

## Caveats (read before you rely on specifics)

1. **Time-sensitivity.** Copilot Studio evolves rapidly. Several cited pages carry
   preview / "subject to change" banners (notably the agents-experience knowledge
   page), and **quota figures change frequently** — re-verify exact limits against
   live docs before building.
2. **The knowledge/instructions line is cleaner in docs than in practice.**
   Instructions *describe how to use* knowledge, and safety is enforced by
   independent moderation layers — so the "facts vs. behavior" split is a strong
   guiding model, not an absolute wall.
3. **"Knowledge as examples = don't" rests on design intent, not a hard block.**
   Microsoft scopes RAG to factual Q&A and doesn't optimize for examples; general
   LLM behavior can still be nudged by in-context text. The recommendation is
   "shouldn't," grounded in mechanics (conditional, top-N-chunk retrieval), not a
   technical prohibition.
4. **Fallback vs. proactive retrieval framing.** The SharePoint "fallback when no
   topic answers" wording reflects classic/SharePoint generative-answers behavior;
   under modern generative orchestration the orchestrator searches proactively via
   the Universal Search Tool. The fallback framing is *incomplete*, not wrong.
5. **Two retrieval surfaces — don't conflate.** Copilot Studio's built-in
   knowledge feature is distinct from the **M365 Copilot Retrieval API** (a
   developer surface). Azure AI Search is likewise a separate integration path.

---

## Open questions (unresolved — worth checking for your build)

1. **Prompt-injection via knowledge.** Can a knowledge document containing
   directive/persona text leak into behavior? Docs assert clean data-vs-behavior
   separation but don't address injection-through-knowledge. *Relevant if you
   ingest untrusted/third-party documents.*
2. **Multi-source ranking under generative orchestration.** When web search *and*
   multiple knowledge sources are all active, how exactly are results
   ranked/merged across "top 3 per source" and the 25-source runtime limit? Not
   documented in detail.
3. **The supported mechanism for example-driven/template responses.** Since
   knowledge is explicitly *not* the vehicle, what's the best-supported path —
   examples embedded in instructions, topics/prompt nodes, or prompt-library
   components? (Docs point to instructions/few-shot; exact best practice for
   *templated* output is under-specified. Prototype the instructions path first.)
4. **Built-in knowledge vs. Retrieval API / Azure AI Search at scale.** For
   large-scale or highly-customized retrieval, which path does Microsoft
   recommend, and what are the licensing/cost trade-offs? Not resolved here.

---

## How this maps to the research sub-questions

| Sub-question | Answer | Doc |
|---|---|---|
| 1. Knowledge as instructions? | **No** — instructions drive behavior; knowledge only supplies facts and can't steer retrieval | [01](01-knowledge-vs-instructions.md) |
| 2. Knowledge as examples/templates? | **No** — RAG is scoped to factual Q&A; examples belong in instructions | [02](02-knowledge-as-examples.md) |
| 3. How retrieval works | Orchestration-driven, automatic, four-step RAG (rewrite → retrieve top-3/source → summarize → validate) | [03](03-retrieval-mechanics.md) |
| 4. Types & limits | Five source types; 500/500 caps; SharePoint license-gated + permission-trimmed | [04](04-knowledge-types-and-limits.md) |
