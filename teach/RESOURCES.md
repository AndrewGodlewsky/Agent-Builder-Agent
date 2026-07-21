# Copilot Studio Knowledge & SharePoint RAG Resources

Trusted-source index for the Copilot Studio Field Manual. Every external URL
below is cited in the repo's verified research (`research/`). Copilot Studio
moves fast — re-verify limits against the live page before relying on them.

## Knowledge

### Local research (start here)

- [Copilot Studio knowledge research index — this repo](../research/copilot-studio-knowledge/00-index.md)
  One line: the verified ruling that knowledge ≠ instructions ≠ examples, plus retrieval mechanics, source types, and limits. Use for: any "what goes where" decision before touching agent config.
- [SharePoint RAG optimization index — this repo](../research/sharepoint-rag-optimization/00-index.md)
  One line: the two SharePoint RAG paths (connector vs. file upload), site-owner levers, ceilings, and what's structurally impossible. Use for: tuning SharePoint-grounded retrieval quality.
- [Agent-Builder-Agent technical build review — this repo](../research/build-review/copilot-studio-agent-technical-review.md)
  One line: nine Learn-checked findings against the shipped `Agent/` package, worst-first. Use for: the pre-ship checklist and the capstone lesson's case study.

### Microsoft Learn — Copilot Studio core

- [Upload files as a knowledge source — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload)
  One line: supported file types (.md included), the Dataverse-search prerequisite, and the per-file Description step. Use for: any file-upload build; the build review's primary source.
- [Knowledge sources overview — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)
  One line: the five knowledge source types, per-mode input counts, GraphSearch, and knowledge as grounding data. Use for: picking a source type and checking what each mode allows.
- [Knowledge in the agents experience — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-copilot-studio)
  One line: how the orchestrator auto-selects sources and the "Allow ungrounded responses" toggle. Use for: understanding source routing and the grounding trade-off (carries a preview banner).
- [Authoring agent instructions — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions)
  One line: instructions drive behavior and cannot reference knowledge that isn't attached to the agent. Use for: writing the instruction body; settling instructions-vs-knowledge placement arguments.
- [Generative mode guidance — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance)
  One line: instructions shape summarization and tone after retrieval but must not try to steer retrieval itself. Use for: pruning instructions that attempt to influence document retrieval.
- [Retrieval-augmented generation guidance — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/retrieval-augmented-generation)
  One line: the four-step RAG pipeline, top-3-per-source grounding, file/table limits, and why RAG is not a reasoning engine. Use for: predicting what retrieval will and won't return.
- [Generative answers from public websites — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-ai-public-websites)
  One line: the Bing Custom Search pipeline and the retrieval/summarization separation for website sources. Use for: grounding an agent on public web content.
- [Add SharePoint as a knowledge source — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)
  One line: SharePoint connector setup, search query filters, permission trimming, and tenant graph grounding. Use for: configuring the connector path and its filters.
- [Unstructured data knowledge (Dataverse ingestion) — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data)
  One line: how uploaded files are chunked, vector-indexed in Dataverse, and synced every 4–6 hours. Use for: understanding the file-upload path's internals and sync latency.
- [Requirements and quotas — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)
  One line: the hard numbers — 500 sources/files, 25 SharePoint URLs, 7/200 MB gating, unsupported query types. Use for: re-verifying every limit before you commit to it.
- [Generative answers node (boost node) — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-boost-node)
  One line: behavior of the generative answers node, including scoping knowledge per node. Use for: node-level knowledge scoping inside topics.
- [Generative answers with SharePoint/OneDrive — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-generative-answers-sharepoint-onedrive)
  One line: classic generative-answers behavior over SharePoint and OneDrive content. Use for: the fallback-search framing and node-level SharePoint answers (directional, not load-bearing).
- [Troubleshoot: SharePoint knowledge returns no response — Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/sharepoint-no-response)
  One line: the silent no-response causes — top-3 grounding, permissions, license/size gating, oversized files skipped by generative answers. Use for: diagnosing "the agent found nothing" on SharePoint.

### Microsoft Learn — M365 / SharePoint platform

- [M365 Copilot Retrieval API overview — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview)
  One line: the developer-facing retrieval surface — hybrid index, KQL scoping, format limits, permission model (Preview). Use for: deciding Retrieval API vs. built-in knowledge (lesson 10).
- [Declarative agent instructions — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions)
  One line: few-shot examples are an instructions technique, and home of the 8,000-character ceiling — declarative agents only. Use for: examples-in-instructions patterns; not for Copilot Studio limits.
- [Semantic index for Copilot — Microsoft Learn](https://learn.microsoft.com/en-us/microsoftsearch/semantic-index-for-copilot)
  One line: the tenant-wide semantic index — vectorization, automatic build, RBAC-trimmed retrieval. Use for: understanding what an M365 Copilot license actually unlocks for grounding.
- [Manage the search schema — Microsoft Learn](https://learn.microsoft.com/en-us/sharepoint/manage-search-schema)
  One line: mapping crawled to managed properties, re-crawls, and schema management. Use for: the site-owner search-schema playbook (attribute semantics authoritative; crawl mechanics are Server-era, directional for SPO).
- [Crawled and managed properties overview — Microsoft Learn](https://learn.microsoft.com/en-us/sharepoint/technical-reference/crawled-and-managed-properties-overview)
  One line: the crawled-vs-managed property model underpinning what enters the SharePoint index. Use for: schema fundamentals before touching mappings (Server page; semantics carry to SPO).
- [Search schema overview (managed-property attributes) — Microsoft Learn](https://learn.microsoft.com/en-us/sharepoint/search/search-schema-overview)
  One line: what Searchable/Queryable/Retrievable/Refinable actually control. Use for: choosing attribute settings when tuning what retrieval can see and return.
- [Optimize SharePoint content for Copilot — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/copilot/employee-self-service/optimization-sharepoint)
  One line: Microsoft's own content-optimization guidance for Copilot over SharePoint. Use for: document-authoring ideas — directional, not verified for the Copilot Studio pipeline.
- [Optimize content for the Retrieval API — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/optimize-content-retrieval)
  One line: content-structuring advice scoped to the Retrieval API. Use for: authoring hints if you go the API route — parity with the built-in connector is unconfirmed.
- [Microsoft 365 Copilot privacy — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy)
  One line: how Copilot handles tenant data, permissions, and privacy boundaries. Use for: answering stakeholder data-handling questions about grounded agents.

## Wisdom (Communities)

- [Microsoft Copilot Studio community forum — Power Platform Community](https://community.powerplatform.com/)
  Official Microsoft-hosted forums with a dedicated Copilot Studio board; product team members and MVPs answer maker questions. Use for: "is this behavior a bug or by design" questions and release chatter.
- [r/copilotstudio — Reddit](https://www.reddit.com/r/copilotstudio/)
  Practitioner subreddit for Copilot Studio makers; unfiltered field reports on limits, quirks, and workarounds. Use for: reality checks the docs won't give you.
- [Microsoft Tech Community](https://techcommunity.microsoft.com/)
  Microsoft's broader community hub covering M365 Copilot, SharePoint, and Power Platform; blogs and discussion spaces from product teams. Use for: cross-product topics (semantic index, SharePoint search, licensing).

> Note: the user has not yet been asked whether they want to join a community —
> raise it in a future session before recommending participation.

## Gaps

Open questions carried over from the research sets — these drive future research sessions.

From `research/copilot-studio-knowledge/06-sources-and-open-questions.md`:

- Prompt-injection via knowledge: can directive/persona text inside a knowledge document leak into agent behavior? Undocumented; matters when ingesting untrusted docs.
- Multi-source ranking: how are results merged across "top 3 per source," web search, and the 25-source runtime limit under generative orchestration? Not documented in detail.
- Templated output: what is the best-supported mechanism for example-driven/template responses — instructions few-shot, topics/prompt nodes, or prompt library? Prototype the instructions path first.
- Built-in knowledge vs. Retrieval API / Azure AI Search at scale: which does Microsoft recommend, and what are the licensing/cost trade-offs? Unresolved.

From `research/sharepoint-rag-optimization/07-sources-and-open-questions.md`:

- Do the Retrieval API document-type limits (semantic retrieval extensions, no image/chart retrieval) also apply to the built-in SharePoint connector? Test: answer hidden in an image inside a PDF.
- Scanned-PDF OCR: does SharePoint crawl or Dataverse ingestion OCR image-only PDFs? Test: upload a text-free scanned PDF and query it.
- Which document-structuring actions (headings, titles, alt text) measurably help retrieval? Indexing mechanics are verified; authoring guidance is not — test end-to-end.
- Can managed metadata / content types aid source disambiguation despite the column-value-filtering ban? For structured/tabular queries, plan on Dataverse, not SharePoint knowledge.
