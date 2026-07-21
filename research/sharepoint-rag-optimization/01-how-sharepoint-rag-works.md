# How SharePoint RAG Actually Works (Internals)

> The mechanics behind SharePoint → Copilot Studio grounding. Understand these and
> every optimization decision downstream makes sense.

Confidence legend: ✅ VERIFIED (primary + 3-0) · 📄 DIRECTIONAL · ❓ UNCONFIRMED.

---

## 1. ✅ Two architecturally distinct paths

Copilot Studio can ground on SharePoint two fundamentally different ways. **They
do not work the same and are not interchangeable.**

### Path A — SharePoint knowledge source (the connector / GraphSearch path)

- You point the agent at a **SharePoint URL**.
- At query time it **queries SharePoint's live search infrastructure in real time
  via GraphSearch**.
- Content **stays in SharePoint**; nothing is copied.
- Authenticates via the **agent user's Microsoft Entra ID**.
- Supports advanced filters (title, author, modified by/date) and sensitivity
  labels.
- Limits: **25 URLs** in generative orchestration / 4 in classic.

### Path B — File upload (the Dataverse path)

- Files are **copied into Dataverse**, where they are **chunked and vector-indexed
  into a semantic index**.
- Retrieval matches **query intent against those embeddings**.
- Content is **synchronized every 4–6 hours** (not real time).

> ✅ *"Option 1 (file upload) searches a Dataverse semantic index built from
> embedded vectors of the ingested content copied from SharePoint… synchronized
> every four to six hours… Option 2 (connector) directly queries SharePoint search
> infrastructure in real time… content resides in SharePoint."*
> — [knowledge-unstructured-data](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data),
> [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)

**Why this matters for you:** if you have full site-owner control and want live,
permission-trimmed grounding over a document library, **Path A (connector)** is
the natural fit — and it's the path where search-schema tuning ([04](04-search-schema-playbook.md))
pays off. Path B is better for a small, curated, stable set where you want the
512 MB ceiling and don't mind a 4–6h sync lag.

---

## 2. ✅ The tenant semantic index (what Path A rides on)

Because you're **M365 Copilot licensed**, Microsoft automatically builds a
**tenant-level semantic index** — and this is what gives Path A its power:

- Generated **automatically, no admin action**, from **text-based SharePoint
  Online files**, for every subscription with a paid Copilot license.
- Creates **vectorized indices**: each item becomes a **numerical vector**; vectors
  are stored in a **multi-dimensional space where semantically similar items
  cluster together**.
- Enables **similarity search across billions of vectors** — retrieval "beyond
  exact keyword matching."

> ✅ *"A semantic index is created for every subscription at the tenant and user
> level… an organization-wide index generated from text-based SharePoint Online
> files… The indexing process requires no administrative involvement… A vector is a
> numerical representation… stored in multi-dimensional spaces where semantically
> similar data points are clustered together."*
> — [semantic-index-for-copilot](https://learn.microsoft.com/en-us/microsoftsearch/semantic-index-for-copilot)

> 📄 Minor nuance: the tenant index also includes **Copilot connector data**, so
> it's not *exclusively* SharePoint-file-derived.

**Implication:** you can't "build" or "rebuild" this index — it's automatic. Your
lever is making your *content* and *search schema* clean enough that the right
vectors surface (docs [04](04-search-schema-playbook.md),
[05](05-document-optimization-playbook.md)).

---

## 3. ✅ The crawled → managed property model (how content enters the index)

SharePoint search indexing is governed by a two-tier property model. This is the
backbone of everything a site owner can tune:

```
  Document / list item
        │
        │  (crawl extracts content + metadata)
        ▼
  ┌──────────────────────┐
  │ CRAWLED PROPERTY     │   e.g. author, title, subject — raw extracted data
  └──────────────────────┘
        │
        │  MAP  ← you control this in the search schema
        ▼
  ┌──────────────────────┐
  │ MANAGED PROPERTY     │   what actually enters the search index
  │ (Searchable /        │
  │  Queryable /         │
  │  Retrievable / …)    │
  └──────────────────────┘
        │
        ▼
     Search index  →  GraphSearch  →  Copilot Studio
```

> ✅ *"A crawled property is content and metadata extracted from an item during a
> crawl… To include the content and metadata of crawled properties in the search
> index, you map crawled properties to managed properties. The index only includes
> content and metadata from the managed properties."*
> — [crawled-and-managed-properties-overview](https://learn.microsoft.com/en-us/sharepoint/technical-reference/crawled-and-managed-properties-overview),
> [manage-search-schema](https://learn.microsoft.com/en-us/sharepoint/manage-search-schema)

**Two consequences:**
1. **Only managed-property content is searchable.** If metadata isn't mapped to a
   managed property, the agent effectively can't see it.
2. **Changes require a re-crawl.** A new managed property mapping only takes effect
   *after the content is re-crawled*.

> 📄 Caveat: this crawled/managed model is documented on **SharePoint Server**
> pages, but the **attribute semantics carry over to SharePoint Online**. SPO
> manages the schema per-tenant via the admin center with **less crawl-scheduling
> control** than on-prem — treat the *attribute meanings* as authoritative and the
> *crawl-timing mechanics* as directional. (See [04](04-search-schema-playbook.md).)

---

## 4. ✅ Only the top 3 results ground each answer

This is the single most consequential retrieval fact for tuning:

> ✅ *"When Copilot Studio searches SharePoint, only the top three search results
> are used to summarize and generate a response. If no search results are returned,
> the generative answers node doesn't provide a response."*
> — [sharepoint-no-response](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/sharepoint-no-response)

**Everything about optimization flows from this:**
- More documents ≠ better answers. If the right doc isn't in the **top 3**, it
  doesn't ground the answer at all.
- **Near-duplicate documents are actively harmful** — they crowd each other out of
  the top 3 and split relevance.
- **Disambiguation and precision** (clear titles, distinct content, filtered
  scope) are worth more than volume.

---

## 5. Chunking & embedding — what we know and don't

- ✅ **Path B (file upload):** files are **chunked and embedded as vectors** in
  Dataverse; retrieval matches query intent to chunks.
  ([knowledge-unstructured-data](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data))
- ✅ **Path A / tenant index:** content is **vectorized** into the semantic index
  (§2).
- ❓ **Chunk size / chunking strategy is not documented or configurable.** You
  cannot tune how documents are split. (Consistent with the broader-research
  finding that chunking is unpublished.)
- ❓ **Whether document structure (headings, sections) affects chunk boundaries**
  is **not confirmed by any primary source.** It's plausible and standard-RAG
  intuition, but Microsoft doesn't document it. See open questions in
  [07](07-sources-and-open-questions.md).

---

## 6. ✅ Permission trimming happens at retrieval (summary)

Both paths **permission-trim at query time** using the querying user's identity —
covered in full in [02-permission-trimming-and-security.md](02-permission-trimming-and-security.md).
Key point for internals: even Path B, which copies content into Dataverse, does a
**live permission check against SharePoint** at query time and stores no
permission info locally.

---

## Internals summary

| Fact | Value | Confidence |
|---|---|---|
| Number of SharePoint paths | 2 (connector/GraphSearch vs. file-upload/Dataverse) | ✅ |
| Connector retrieval timing | Real time | ✅ |
| File-upload sync cadence | Every 4–6 hours | ✅ |
| Tenant semantic index | Auto-built from text-based SPO files (licensed) | ✅ |
| What enters the index | Only mapped **managed properties** | ✅ |
| Schema changes | Require re-crawl | ✅ |
| Results grounding an answer | **Top 3 only** | ✅ |
| Chunk size / structure effect | Not documented / not tunable | ❓ |
