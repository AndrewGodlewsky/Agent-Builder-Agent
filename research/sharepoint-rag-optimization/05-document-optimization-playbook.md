# Document Optimization Playbook — By Type

> How to prepare large PDFs, Office docs, and SharePoint pages/lists for better
> retrieval. **Read the confidence markers carefully here** — this is the area
> where Microsoft documents the *least*, so much of the intuitive advice is
> ❓ UNCONFIRMED.

Confidence legend: ✅ VERIFIED (primary + 3-0) · 📄 DIRECTIONAL · ❓ UNCONFIRMED.

---

## ⚠️ Honest framing first

The research specifically hunted for primary-sourced guidance on authoring
documents for better chunks/embeddings — OCR of scanned PDFs, heading/alt-text
structuring, title hygiene, chunking-friendly formatting. **Microsoft largely does
not document this.** So this doc separates:

- The **few ✅ verified** file-handling facts,
- **📄 directional** guidance from Microsoft optimization pages,
- **❓ unconfirmed** RAG best-practice that is *sensible to test* but not
  Microsoft-stated.

Don't treat ❓ items as established fact. They're a **test list**, not a spec.

---

## 1. Large PDFs

### ✅ Verified
- **File-size ceilings apply** and matter most here: **512 MB** for PDF via the
  connector (licensed) or file-upload; general SharePoint files 200 MB.
  ([03](03-licensing-and-limits.md))
- **Oversized PDFs fail silently** — returned by Graph search but **not processed**
  by generative answers. ([03](03-licensing-and-limits.md) §2)

### 🔧 Actions (mix of ✅-derived and ❓)
- ✅ **Keep PDFs under the ceiling.** For a genuinely huge PDF, **split it** into
  smaller topic-scoped PDFs so each is processable *and* more precisely
  retrievable (helps the top-3 odds).
- ❓ **OCR scanned/image-only PDFs.** RAG needs *text*; an image-only PDF has none.
  **Whether SharePoint's crawl or Copilot Studio's ingestion OCRs image-only PDFs
  is NOT confirmed by any primary source** (open question). **Safest assumption:
  OCR them yourself** (make them text-searchable) before uploading. Test a scanned
  PDF end-to-end before trusting it.
- ❓ **Text-based > scanned.** Prefer born-digital, selectable-text PDFs over scans.
  (Standard RAG intuition; not Microsoft-documented.)

---

## 2. Office docs (Word / PowerPoint / Excel)

### ✅ Verified
- **PPTX/DOCX get the 512 MB ceiling** (licensed). ([03](03-licensing-and-limits.md))
- 📄 For the **Retrieval API** (a related path — [06](06-retrieval-api-vs-builtin.md)),
  **table text is retrievable only from .doc/.docx/.pptx**, and **images/charts
  are not retrievable at all.** This is ✅ for the Retrieval API but **❓ for
  Copilot Studio's built-in connector** (not confirmed identical).

### 🔧 Actions (❓ unless noted — sensible to test)
- ❓ **Put answers in text, not only in images/diagrams.** Since image/chart
  retrieval is unsupported on the Retrieval API and likely limited elsewhere,
  content trapped in a PowerPoint diagram or an embedded image may not ground
  answers. Add a text caption or notes.
- ❓ **Use real headings and clear structure** in Word docs. Standard RAG practice
  suggests structure aids chunk boundaries — but **Microsoft doesn't confirm** it
  affects Copilot Studio chunking. Worth doing anyway (it's free and helps humans).
- ❓ **Excel is weak for narrative RAG.** Spreadsheets are tabular; RAG is scoped to
  factual Q&A over text (see broader research). For structured/tabular lookups,
  prefer a **Dataverse table** knowledge source over an Excel file in SharePoint.
- ❓ **Descriptive titles** (document Title property, not just filename) — plausibly
  helps retrieval/disambiguation; the connector exposes a **Title** filter
  (✅ that Title is used as a filter field —
  [knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)),
  so keeping Title meaningful is low-risk, high-plausibility.

---

## 3. SharePoint pages / lists

### ✅ Verified
- The **tenant semantic index is built from text-based SharePoint Online files** —
  ✅ native SharePoint page text is exactly the kind of content it's built for.
  ([01](01-how-sharepoint-rag-works.md) §2)
- **List column metadata is searchable only if mapped to managed properties** and
  re-crawled ([04](04-search-schema-playbook.md)) — but ✅ **column-value filtering
  queries are still unsupported at the knowledge-source level**
  ([03](03-licensing-and-limits.md) §4).

### 🔧 Actions
- ✅ **Pages are good RAG citizens** — clean, text-based, semantically indexed. Use
  them for authoritative narrative content (policies, how-tos).
- ✅ **Don't expect list "database" queries.** Lists are not a query surface for the
  agent — "list all items where X" won't work. Use Dataverse for that.
- 📄 **Keep page content focused** — one topic per page improves top-3 precision.

---

## 4. Cross-cutting: the top-3 discipline

Every doc-prep decision should serve one goal: **make the single authoritative
answer land in the top 3 search results.** ([01](01-how-sharepoint-rag-works.md) §4)

- ✅ **Deduplicate.** Near-identical docs split relevance and crowd the top 3.
- ✅ **One canonical doc per topic.**
- ✅ **Filter out stale versions** ([04](04-search-schema-playbook.md) §3).
- ❓ **Right-size documents** — very large omnibus docs may retrieve a chunk that
  misses the point; topic-scoped docs plausibly retrieve more precisely. (Test.)

---

## 5. 📄 Microsoft's own optimization pages (directional)

Microsoft publishes optimization guidance that was fetched but whose specific
claims didn't survive into the verified top-25 (so: directional, worth reading
against your tenant):

- [Optimize SharePoint content for Copilot (employee self-service)](https://learn.microsoft.com/en-us/microsoft-365/copilot/employee-self-service/optimization-sharepoint)
- [Optimize content for the Retrieval API](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/optimize-content-retrieval)
- [Generative answers with SharePoint/OneDrive (Copilot Studio)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-generative-answers-sharepoint-onedrive)

**🔧 Action:** read these three directly — they're the closest Microsoft gets to a
document-authoring playbook, and they may confirm some of the ❓ items above for
your specific setup.

---

## Document optimization summary

| Action | Type | Confidence |
|---|---|---|
| Keep files under size ceiling; split huge PDFs | All / PDF | ✅ |
| OCR scanned PDFs before upload | PDF | ❓ (assume yes; test) |
| Put answers in text, not only images/charts | Office | ❓ (Retrieval API says images unsupported ✅) |
| Use Dataverse (not Excel/lists) for tabular lookups | Excel/lists | ❓/✅ (list queries unsupported ✅) |
| Meaningful Title property | Office/all | 📄 (Title is a filter field ✅) |
| Headings/structure | Word | ❓ (do it anyway) |
| Deduplicate; one canonical doc per topic | All | ✅ (follows from top-3) |
| Read MS optimization pages | All | 📄 |
