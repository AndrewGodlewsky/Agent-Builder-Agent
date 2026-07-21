---
name: project-sharepoint-rag-findings
description: Key verified facts on how SharePoint knowledge/RAG works for Copilot Studio agents (informs builder agent guidance)
metadata:
  type: project
---

Deep-research deliverable (2026-07-21) lives in
`research/sharepoint-rag-optimization/` (8 MD docs, index at `00-index.md`).
Sibling to `research/copilot-studio-knowledge/` (see
[[project-agent-builder-overview]]). All ✅ facts below are primary-sourced
(Microsoft Learn) + passed 3-0 adversarial verification.

**Core mechanics the builder agent should know:**
- **Two distinct SharePoint RAG paths**: (A) *connector/knowledge source* — points
  at a SharePoint URL, queries live via **GraphSearch**, real-time, content stays
  in SharePoint, 25 URLs generative; (B) *file upload* — copies files into
  **Dataverse**, chunks+vector-indexes, **synced every 4–6h**, 512 MB/file. Not
  interchangeable.
- **Only the TOP 3 search results ground each answer.** Precision + dedup matter
  more than volume. Near-duplicate docs are harmful.
- **Permission-trimmed at retrieval** via querying user's Entra ID (delegated);
  needs ≥Read; no local permission storage; **silent "no response"** on no-access
  (no error). Test as a real end user, not admin.
- **M365 Copilot license (same tenant)** → 200 MB SharePoint files (512 MB for
  PDF/PPTX/DOCX) + higher precision, **but requires Enhanced search results ON +
  tenant graph grounding with semantic search ON**. Without license: 7 MB cap.
- **Oversized files fail SILENTLY** — returned by Graph search but not processed by
  generative answers.
- **Structurally impossible (instructions can't fix):** referencing a file by name,
  folder listing/counting, column-value filtering. For structured/tabular queries
  use **Dataverse**, not SharePoint knowledge.
- **Site-owner levers (✅ high-confidence):** search-schema config (crawled→managed
  property mapping, Searchable/Queryable/Retrievable; re-crawl required;
  Refinable/Sortable unsupported in modern search), Copilot Studio **search query
  filters** (Title/Author/Modified by/Modified on), narrow URL scope, dedup.
- **NOT primary-sourced (❓, test don't assume):** scanned-PDF OCR handling,
  heading/alt-text/structure effect on chunking, metadata-for-disambiguation. Much
  of the "author docs better" advice Microsoft simply doesn't document.
- **Retrieval API** = separate code-level path over same tenant index (Preview);
  no image/chart retrieval, table text Office-only — these limits ✅ for the API but
  ❓ whether identical for the built-in connector.

Caveat: limits change fast; re-verify before relying long-term.
