# SharePoint → Copilot Studio RAG: Internals & Site-Owner Optimization

**Research question:** How does SharePoint search (Graph, crawling, indexing)
work as a knowledge source for Copilot Studio agents, and what advanced
site-owner actions improve RAG quality from uploaded documents?

**Your context (assumed throughout):**
- **Microsoft 365 Copilot license in the same tenant** → tenant graph grounding +
  semantic index + the 200 MB SharePoint ceiling are all available to you.
- **Full site-owner control** of the SharePoint site → search-schema and
  library-level actions are on the table.
- Documents: **large PDFs, Office docs, and native SharePoint pages/lists.**

Research date: 2026-07-21. Primary claims are drawn from first-party Microsoft
docs and passed **3-0 unanimous adversarial verification** (25 claims verified, 0
refuted). **This area moves fast — re-verify limits before relying on them.**

---

## ⚠️ How to read the confidence markers in this set

The research was rigorous about what is and isn't primary-sourced. Every claim in
these docs is tagged:

- **✅ VERIFIED** — backed by primary Microsoft documentation, passed 3-0
  adversarial verification. Trust these.
- **📄 DIRECTIONAL** — from Microsoft optimization docs that were fetched but
  whose specific claims didn't make the verified top-25, or from general SharePoint
  search mechanics. Reasonable, but confirm against your tenant.
- **❓ UNCONFIRMED** — the research question asked about it (e.g. OCR for scanned
  PDFs, alt-text/heading structuring) but **no primary source confirmed it**.
  Treat as hypothesis to test, not fact. Tracked as open questions in doc 07.

**Do not let the volume of guidance obscure this:** the load-bearing, trustworthy
core is the ✅ items. Much of the "authoring your documents for better chunks"
advice you'd expect is ❓ — Microsoft simply doesn't document it clearly.

---

## The single most important thing to understand

**There are TWO different SharePoint RAG paths, and they work completely
differently.** Almost every optimization decision depends on which one you use:

| | **Path A — SharePoint knowledge source (connector)** | **Path B — File upload** |
|---|---|---|
| How it connects | Points at a **SharePoint URL**, queries SharePoint search live via **GraphSearch** | **Copies files into Dataverse**, builds its own semantic index |
| Timing | **Real time** | Synced every **4–6 hours** |
| Where content lives | Stays in SharePoint | Copied into Dataverse |
| Rides on | Tenant semantic index (M365 Copilot) | Its own Dataverse vector index |
| Your site-owner levers | Search schema, search query filters, permissions | File hygiene, chunking-friendly formatting |
| Best for | Living document libraries, permission-trimmed enterprise content | Curated, stable document sets |

Full detail in **[01-how-sharepoint-rag-works.md](01-how-sharepoint-rag-works.md)**.

---

## TL;DR — the highest-leverage site-owner actions (all ✅ unless noted)

1. **Turn ON tenant graph grounding with semantic search** (you're licensed) —
   unlocks 200 MB files, higher-precision retrieval. Requires "Enhanced search
   results" ON. ([03](03-licensing-and-limits.md))
2. **Only the top 3 search results ground each answer** — so **retrieval
   precision and disambiguation matter enormously.** Curate hard; reduce
   near-duplicate documents. ([01](01-how-sharepoint-rag-works.md),
   [04](04-search-schema-playbook.md))
3. **Configure search query filters** (Title, Author, Modified by, Modified on) on
   the SharePoint knowledge source to exclude stale/irrelevant content.
   ([04](04-search-schema-playbook.md))
4. **Use the search schema** — map crawled→managed properties, tune
   Searchable/Queryable/Retrievable — to control what enters the index and what's
   returned. ([04](04-search-schema-playbook.md))
5. **Keep large PDFs under the ceiling** — files over the limit still appear as
   search hits but **won't be processed by generative answers** (a silent gotcha).
   For big files, consider the 512 MB file-upload path. ([03](03-licensing-and-limits.md),
   [05](05-document-optimization-playbook.md))
6. **Know what's structurally impossible:** referencing a file by name, folder
   listing/counting, column-value filtering — these **cannot** be answered and
   **cannot** be fixed with instructions. Design around them.
   ([03](03-licensing-and-limits.md))

---

## Documents in this set

1. **[01-how-sharepoint-rag-works.md](01-how-sharepoint-rag-works.md)** —
   Internals: the two paths, GraphSearch, the tenant semantic index, crawled vs.
   managed properties, chunking/embedding, sync cadence, top-3 grounding.
2. **[02-permission-trimming-and-security.md](02-permission-trimming-and-security.md)** —
   How retrieval-time permission trimming works, delegated permissions, the silent
   "no response," and oversharing implications.
3. **[03-licensing-and-limits.md](03-licensing-and-limits.md)** —
   What your M365 Copilot license unlocks, file-size ceilings (7/200/512 MB), the
   Enhanced search results toggle, and the query types that are structurally
   unsupported.
4. **[04-search-schema-playbook.md](04-search-schema-playbook.md)** —
   Site-owner actions via the search schema and Copilot Studio filters — the most
   concrete, verified levers you have.
5. **[05-document-optimization-playbook.md](05-document-optimization-playbook.md)** —
   By document type (large PDFs, Office docs, pages/lists): what's verified, what's
   directional, and what's unconfirmed-but-worth-testing.
6. **[06-retrieval-api-vs-builtin.md](06-retrieval-api-vs-builtin.md)** —
   The M365 Copilot Retrieval API as an alternative grounding path, its format
   limits, and when to reach for it vs. built-in SharePoint knowledge.
7. **[07-sources-and-open-questions.md](07-sources-and-open-questions.md)** —
   Full citations, verification stats, caveats, and the four open questions worth
   resolving against your own tenant.

---

## Relationship to the other research set

This subfolder is the **deep SharePoint-specific dive**. The broader
knowledge-vs-instructions research (retrieval basics, all source types, the ruling
that knowledge ≠ instructions/examples) lives in
[`../copilot-studio-knowledge/`](../copilot-studio-knowledge/00-index.md). Start
there for fundamentals; use this set for SharePoint RAG tuning.
