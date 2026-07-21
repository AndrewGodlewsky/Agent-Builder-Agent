# Sources, Verification & Open Questions

> Provenance, confidence, caveats, and the four questions worth resolving against
> your own tenant before you commit to a design.

---

## Research method

- **Approach:** deep-research harness — 6 search angles → fetch top sources →
  extract falsifiable claims → **3-vote adversarial verification** → synthesize +
  dedupe.
- **Scale:** 6 angles, 22 sources fetched, 107 claims extracted, **25 verified →
  25 confirmed, 0 refuted, 0 unverified**, 11 findings after synthesis. 105 agent
  calls.
- **Confidence:** every ✅ claim is backed by **primary Microsoft documentation**
  and passed **3-0 unanimous** verification.
- **Research date:** 2026-07-21.

---

## Primary sources (Microsoft first-party)

| Area | URL |
|---|---|
| SharePoint knowledge internals (two paths, sync, permission check) | [knowledge-unstructured-data](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data) |
| Knowledge source types, GraphSearch, ceilings, Enhanced search results | [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio) |
| Add SharePoint knowledge, filters, permission trimming, tenant graph grounding | [knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint) |
| Quotas, ceilings, unsupported query types | [requirements-quotas](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas) |
| Top-3 results, silent no-response, license/size, oversized-file behavior | [sharepoint-no-response (troubleshoot)](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/sharepoint-no-response) |
| Tenant semantic index, vectorization, auto-build, RBAC trimming | [semantic-index-for-copilot](https://learn.microsoft.com/en-us/microsoftsearch/semantic-index-for-copilot) |
| Search schema, crawled→managed mapping, re-crawl, attributes | [manage-search-schema](https://learn.microsoft.com/en-us/sharepoint/manage-search-schema) |
| Crawled vs. managed properties model | [crawled-and-managed-properties-overview](https://learn.microsoft.com/en-us/sharepoint/technical-reference/crawled-and-managed-properties-overview) |
| Managed-property attributes (Searchable/Queryable/Retrievable/Refinable) | [search-schema-overview](https://learn.microsoft.com/en-us/sharepoint/search/search-schema-overview) |
| Retrieval API, format limits, KQL, permission model | [Retrieval API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview) |

### Optimization pages (fetched, directional — didn't produce verified top-25 claims)
- [Optimize SharePoint content for Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/employee-self-service/optimization-sharepoint)
- [Optimize content for the Retrieval API](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/optimize-content-retrieval)
- [Generative answers with SharePoint/OneDrive](https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-generative-answers-sharepoint-onedrive)
- [M365 Copilot privacy](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy)

### Practitioner blogs (corroborating only, not load-bearing)
sharepointmaven.com · sharegate.com · devblogs.microsoft.com/ise · bajonczak.com ·
epcgroup.net · m365.fm · moxie365.com — used mainly for the oversharing/permissions
directional guidance in [02](02-permission-trimming-and-security.md) §4.

---

## Caveats (read before relying on specifics)

1. **Time-sensitivity is significant.** Most sources carry 2026 dates, several
   updated within weeks of the research date. The **200 MB / 7 MB / 512 MB**
   ceilings, **top-3** count, **25-URL** limit, and **4–6h** sync cadence should be
   re-verified before you rely on them long-term.
2. **Search-schema docs are SharePoint Server pages.** `search-schema-overview` and
   `crawled-and-managed-properties-overview` carry an "Applies to: SharePoint in
   Microsoft 365 — NO" banner. The **crawled/managed model and attribute semantics
   carry over to SPO**, but SPO manages the schema per-tenant via the admin center
   with **less crawl-scheduling control**. Treat attribute *semantics* as
   authoritative, crawl-*mechanics* as directional.
3. **Two paths have different mechanics.** "Top-3 results" and the GraphSearch
   permission model are documented for the **connector** path; the **file-upload**
   path has its own semantic index over embedded vectors with 4–6h sync. Don't
   assume behaviors transfer between them.
4. **Retrieval API format limits ≠ confirmed for the built-in connector.** The
   `.doc/.docx/.pptx/.pdf/.aspx/.one` semantic-retrieval list, Office-only table
   text, and no-image/chart retrieval are **explicitly scoped to the Retrieval
   API**. Whether Copilot Studio's built-in SharePoint knowledge behaves
   identically is **not confirmed**. The Retrieval API is also in **Preview**.
5. **"Better quality / greater precision" is Microsoft's self-assessment.** Tenant
   graph grounding's precision claims have no independent benchmark.
6. **Several requested playbook items were NOT primary-sourced.** OCR of scanned
   PDFs, heading/alt-text/title structuring for chunking, and managed-metadata
   content types for disambiguation were asked about but **no surviving claim
   confirmed them.** They're marked ❓ throughout and listed below — **test them,
   don't assume them.**

---

## Open questions (unresolved — resolve against your tenant)

1. **Do the Retrieval API document-type limits also apply to the built-in
   SharePoint connector?** (Semantic retrieval only for certain extensions;
   no image/chart/table retrieval outside Office formats.) No surviving claim
   confirmed equivalence. → **Test:** put an answer only in an image inside a PDF
   and see if the agent can use it.
2. **How is scanned-PDF OCR handled?** No confirmed claim states whether
   SharePoint's crawl OCRs image-only PDFs, or whether Copilot Studio's Dataverse
   ingestion does. Critical for large scanned PDFs. → **Test:** upload a scanned,
   text-free PDF and ask a question only that PDF answers.
3. **What document-structuring actions measurably help retrieval?** Headings,
   titles, alt text, chunking-friendly formatting — the verified claims establish
   indexing *mechanics* but not primary-sourced authoring guidance. → Read the
   three MS optimization pages ([05](05-document-optimization-playbook.md) §5);
   otherwise treat as ❓.
4. **Can managed metadata / content types disambiguate sources despite the
   column-filtering ban?** There's real tension: the search schema *can* make
   columns queryable, yet Copilot Studio explicitly **doesn't support** column-value
   filtering at the knowledge-source level. How (if at all) metadata helps
   disambiguation for grounding — vs. needing a Dataverse table for structured
   queries — is unresolved. → For structured/tabular queries, plan on **Dataverse**,
   not SharePoint knowledge.

---

## How this maps to your research goals

| Your goal | Answer location | Confidence of core |
|---|---|---|
| Understand Graph/indexing internals | [01](01-how-sharepoint-rag-works.md) | ✅ High |
| Permission trimming mechanics | [02](02-permission-trimming-and-security.md) | ✅ High |
| Advanced site-owner actions | [04](04-search-schema-playbook.md) | ✅ High (schema/filters) |
| Per-document-type optimization | [05](05-document-optimization-playbook.md) | ⚠️ Mixed — much is ❓ |
| Retrieval API vs. built-in | [06](06-retrieval-api-vs-builtin.md) | ✅ High (API) / ❓ (connector parity) |

**The honest bottom line:** the **high-confidence, high-leverage** wins are
*configuration* (turn on the licensed features, set search filters, tune the
schema, scope narrowly, deduplicate, fix permissions) — all in
[03](03-licensing-and-limits.md)/[04](04-search-schema-playbook.md). The
*document-authoring* wins you'd expect (OCR, structure, alt text) are real RAG
practice but **not Microsoft-documented for this pipeline** — do them because
they're cheap and sensible, and **validate with end-to-end tests**, not because a
spec guarantees they help.
