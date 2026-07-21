# Copilot Studio Knowledge — Source Types & Document Types, with Pros & Cons

**Research date:** 2026-07-21
**Question:** What types of documents / knowledge sources can Copilot Studio use for knowledge, and what are the pros and cons of each?
**Grounding:** First-party Microsoft Learn (pages dated 2026-04 → 2026-07). Extends [`04-knowledge-types-and-limits.md`](04-knowledge-types-and-limits.md) with a decision-oriented pros/cons view.

> ⚠️ **Copilot Studio limits change fast and several pages carry "subject to change" / preview banners.** Re-verify every number against live docs before you build.

---

## The question has two layers — this doc covers both

1. **Knowledge *source* types** — *where* the knowledge comes from (uploaded files, SharePoint, a website, Dataverse, a connector). This is the bigger architectural decision. → **Part 1**
2. **Document / *file-format* types** — *what kind of file* you feed a file-based source (PDF, Word, Excel, `.md`, `.csv`…). → **Part 2**

Two cross-cutting truths first, because they shape every pro/con below:

- **RAG is for factual Q&A, not reasoning.** Microsoft explicitly scopes it *away* from full-document comparison, policy-compliance evaluation, and complex reasoning over long documents. Prose the model can quote beats dense tables/spreadsheets it must interpret. (See [`02`](02-knowledge-as-examples.md), [`03`](03-retrieval-mechanics.md).)
- **Retrieval pulls only the top ~3 chunks per source per turn.** More sources = broader coverage but shallower depth each; curate, don't dump.

---

# PART 1 — Knowledge source types

Copilot Studio's **Add knowledge** dialog exposes several source families. The five "core" agent-level generative sources are: **Public website, Uploaded documents, SharePoint, Dataverse, Enterprise connectors.** There are also **file/folder-sync sources** (OneDrive, SharePoint files), **third-party KB connectors** (Confluence/Salesforce/ServiceNow/Zendesk), and **classic-only sources** (Azure OpenAI, Bing Custom Search, Custom Data).

## Quick comparison

| Source | Inputs (generative / classic) | Auth & permission model | Freshness | Best for |
|---|---|---|---|---|
| **Public website** | 25 / 4 | None (public) | Bing index (near-real-time-ish) | Public product docs, marketing/support sites |
| **Uploaded files** | Unlimited (not counted in the 25-source filter) | **None — anyone with agent access sees it** | **Static** (re-upload to update) | Curated, stable docs; widest file-type support |
| **OneDrive / SharePoint file-folder sync** | up to 5 items per add | Per-user Entra ID (permission-trimmed) | **Auto-synced** | A few living files/folders that change |
| **SharePoint (full connector)** | 25 URLs / 4 | Per-user Entra ID (permission-trimmed) | Real-time (GraphSearch, no re-index) | Whole sites/policies libraries, governed content |
| **Dataverse (tables)** | Unlimited / 2 sources × 15 tables | Per-user Entra ID | Real-time | Structured business records |
| **Enterprise connectors (Graph/Microsoft Search)** | Unlimited / 2 | Per-user Entra ID | Per-connector index | Jira, GitHub, CRM, other indexed systems |
| **3rd-party KB connectors** (Confluence/Salesforce/ServiceNow/Zendesk) | collection-level | Per-user creds; published articles only | Connector-driven | External knowledge bases |
| **Classic-only** (Azure OpenAI 5, Bing Custom Search 2, Custom Data 3) | classic node only | Varies | Varies | Only via a generative-answers node's "Classic data" option |

---

## 1. Public website (Bing-grounded)

**Pros**
- Zero auth, zero storage — just paste a URL.
- Real-time-ish: reflects Bing's index of the live site, so no manual refresh.
- Generous input count in generative mode (25 sites).
- Runs in parallel with the separate **Web Search** ("Use information from the web") toggle, interleaving results.

**Cons**
- **Bing-indexed content only** — unindexed, JS-heavy, or new pages ground poorly/stale.
- **Two-level URL depth cap** (`site.com/a/b` OK; `/a/b/c` not). No deep-site targeting.
- **Public pages only** — anything needing auth (SharePoint, wikis) is rejected; a redirect to another top-level domain drops the content.
- **Forums/social URLs** produce noisy or rejected answers; search-engine URLs are useless.
- No permission model — everything is public by definition.

## 2. Uploaded files (stored in Dataverse)

**Pros**
- **Widest file-type support of any path** (see Part 2) — includes `.md`, `.txt`, `.csv`, `.json`, `.yaml`, `.html`, etc.
- **Not counted against the 25-source generative filter** — you can attach many without diluting source-selection.
- Up to **500 files / 512 MB each**; point-and-click, no connector setup.
- Fully self-contained — good for curated reference material you control.

**Cons**
- **Static.** If the file changes you must **manually re-upload**; no sync. This is the #1 maintenance trap.
- **No permission trimming** — *anyone with access to the agent* can retrieve the content. Don't put access-restricted material here.
- **Requires Dataverse search enabled** in the environment (admin action) — a common silent blocker.
- Consumes Dataverse storage; encrypted / sensitivity-labeled / password-protected files won't index (show "ready" but return nothing).

## 3. OneDrive / SharePoint **file-and-folder sync** (Upload files → OneDrive/SharePoint)

*(This is distinct from the full "SharePoint" connector below — it pulls specific files/folders into Dataverse.)*

**Pros**
- **Auto-synced** — edits to the source file flow through without re-uploading (the big win over plain upload).
- **Permission-trimmed** per user (verifies the querying user can open the file).
- Add folders (not just individual files); a folder counts as one item.
- **PDFs added via SharePoint here get page-level citations** (jump to the exact page).

**Cons**
- **Narrow file types: only Word, PowerPoint, PDF, Excel.** No `.md`/`.txt`/`.csv`/`.html`.
- **Only ~5 items per add** action (browse selection).
- **Document libraries not supported** (SharePoint file path); MP4-containing files unsupported.
- Sensitivity-labeled / password-protected files won't index.
- Indexing latency on first setup (builds Dataverse schema).

## 4. SharePoint — full connector (Add knowledge → SharePoint)

**Pros**
- **Point at whole sites/subpaths** (`/sites` includes `/sites/policies`) — GraphSearch, **no re-indexing**, real-time.
- **Permission-trimmed** per user; supports **sensitivity labels**.
- **Advanced filters** (Title / Author / Modified by / Modified on) and **variable-driven URLs** (scope by product/region/env at runtime).
- **SharePoint lists** supported (up to 10; real-time tabular data).
- Best retrieval quality of the SharePoint options when paired with **tenant graph grounding + semantic search**.

**Cons**
- **File-size ceiling is license-gated:** **7 MB** without a same-tenant M365 Copilot license, **200 MB** with the license + tenant-graph grounding + semantic search.
- **Blocked entirely if Restricted SharePoint Search is on**; **guests unsupported** in SSO apps; **Generic OAuth not supported** (Entra ID only) for manual auth.
- Lists > 35,000 rows degrade quality/latency; max 10 lists.
- Requires user auth configured (`Sites.Read.All`, `Files.Read.All` for manual setup).
- Transcripts **don't log the source content** used (`search_results` redacted) — harder to audit answers.

## 5. Dataverse tables

**Pros**
- **Query structured business records** with a RAG technique built for tables; **unlimited** sources in generative mode.
- Real-time, permission-trimmed via Entra ID.
- Natural home if your data already lives in Power Platform / Dynamics 365.

**Cons**
- Classic mode capped hard (2 sources × 15 tables).
- Requires Dataverse search enabled.
- Structured-record retrieval ≠ prose Q&A; expectations differ from document grounding.

## 6. Enterprise data via connectors (Microsoft Graph / Microsoft Search)

**Pros**
- Surfaces **indexed enterprise systems** (Jira, GitHub, ServiceNow, CRM, etc.) already crawled by Microsoft Search; **unlimited** in generative mode.
- Permission-trimmed; scope by connector attribute (project, repo, KB).

**Cons**
- **Admin must enable/configure** the connector and its index — not a maker self-serve step.
- Retrieval quality depends on the connector's own indexing/freshness.
- Classic mode: only 2 per agent.

## 7. Third-party knowledge-base connectors (Confluence, Salesforce, ServiceNow, Zendesk)

**Pros**
- Direct line to popular external KBs; permission-verified per user.

**Cons**
- **Collection-level only** — you can't pick individual articles; **only *published* articles** (no drafts/archived).
- Confluence is **cloud-only**; each needs a connection set up.

## 8. Classic-only sources (Azure OpenAI, Bing Custom Search, Custom Data)

**Pros**
- Enable niche scenarios (custom search config, Azure OpenAI-backed data).

**Cons**
- **Not supported as agent-level generative knowledge** — only inside a generative-answers node via the **"Classic data"** option. If you're on generative orchestration (the default), these are effectively second-class.

---

# PART 2 — Document / file-format types

*Which file formats a path accepts depends on the path.* This is the single most confusing thing about "what documents can I use."

## Supported formats by ingestion path

| Path | Supported file types |
|---|---|
| **Upload files** (Add knowledge → files) | Word (doc/docx), Excel (xls/xlsx), PowerPoint (ppt/pptx), **PDF**, **Text (.txt, .md, .log)**, **HTML (html/htm)**, **CSV**, **XML**, OpenDocument (odt/ods/odp), **EPUB**, **RTF**, Apple iWork (pages/key/numbers), **JSON**, **YAML (yml/yaml)**, **LaTeX (.tex)** |
| **OneDrive / SharePoint file-sync** | **Only** Word, PowerPoint, PDF, Excel |
| **SharePoint full connector / website** | N/A — points at live sites, not uploaded files |

**Universal file rules:** ≤ **512 MB**; **no** image/video/audio/executable files (images only work **embedded in a PDF** with alt-text); **no** encrypted / sensitivity-labeled / password-protected files (they show "ready" but return nothing).

## Pros/cons by format

| Format | Pros | Cons / caveats |
|---|---|---|
| **PDF** | Universally supported on every file path; **page-level citations** when added via SharePoint file-sync; supports embedded annotated images | Scanned/image-only PDFs need alt-text to be searchable; very long PDFs still chunked (top-3 retrieval) |
| **Word (docx)** | Clean prose → **ideal for RAG**; supported everywhere | Complex layouts/tables can chunk awkwardly |
| **PowerPoint (pptx)** | Supported everywhere; good for slide-based SOPs | Sparse text per slide; speaker notes/visual meaning may be lost |
| **Excel / CSV** | Good for lookups/structured lists | **RAG is weak at spreadsheet reasoning**; large sheets degrade; consider a SharePoint **list** or **Dataverse table** instead |
| **Markdown / TXT / LaTeX** | **Upload-only**; great for clean, chunkable prose you author yourself | **Not accepted by OneDrive/SharePoint sync** — so `.md` can't auto-sync; convert to docx/pdf if you need sync |
| **HTML** | Upload-only; captures rendered docs | Markup noise can pollute chunks |
| **JSON / YAML / XML** | Upload-only; structured config/data | RAG treats them as text — good for *lookup*, poor for *reasoning over structure* |

**Design takeaway on formats:** author knowledge as **clean prose** (docx/PDF/`.md`) organized under clear headings — that chunks and retrieves best. Push **tabular/structured** data to a **SharePoint list** or **Dataverse table**, not a spreadsheet upload. Use **PDF via SharePoint file-sync** when you want page-level citations.

---

## Decision cheat-sheet

- **Public info on a website you own** → Public website (mind the 2-level depth + Bing indexing).
- **A handful of living docs that change** → OneDrive / SharePoint **file-sync** (auto-sync + permission-trimmed), accepting the Word/PPT/PDF/Excel-only limit.
- **A whole governed SharePoint site / policy library** → **SharePoint full connector** (check the 7 MB vs 200 MB license gate).
- **Curated, stable reference you author** (incl. `.md`/`.txt`/`.json`) → **Uploaded files** — but remember it's **static** and **not permission-trimmed**.
- **Structured records** → **Dataverse table** or **SharePoint list**, not a spreadsheet.
- **An external system already indexed** (Jira/GitHub/CRM) → **Graph/Microsoft Search connector**.
- **Confluence/Salesforce/ServiceNow/Zendesk KB** → the matching 3rd-party connector (published articles, collection-level).

## Cross-cutting caveats to design around

- **Permission model differs by source:** uploaded files = *everyone with the agent*; every other internal source = *per-user Entra ID trimming*. Choose deliberately for anything sensitive.
- **Freshness differs:** website/SharePoint/Dataverse/connectors are live; **uploaded files are frozen at upload**.
- **Dataverse search must be on** for file/Dataverse-backed sources.
- **The 25-source rule:** in generative mode, >25 sources get filtered by an internal GPT model — **uploaded files are exempt** from that count.
- **Chunking isn't tunable**, and only ~**top-3 chunks/source** are retrieved per turn.
- **Citations can't be piped into other tools/actions.**
- **`Allow ungrounded responses` OFF** blocks any turn that didn't call a source/tool (and disables follow-up questions) — but doesn't *guarantee* zero general-knowledge blending.

## Sources

- Knowledge sources summary (source table, orchestration limits, ungrounded/web/moderation/tenant-graph/official) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- Upload files as a knowledge source (file types, 512 MB, 500 files, image rules) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload
- Add SharePoint as a knowledge source (full connector: auth, filters, lists, variables, Restricted Search, guests) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint
- Add unstructured data (OneDrive/SharePoint file-sync file types, page-level PDF citations, 3rd-party KBs) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-unstructured-data
- Add a public website (URL depth, Bing indexing, redirects, forums) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-public-website
- RAG guidance (what RAG is/isn't for; 7 MB vs 200 MB SharePoint ceiling) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/retrieval-augmented-generation
- Quotas — https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas
- Related internal research: [`04-knowledge-types-and-limits.md`](04-knowledge-types-and-limits.md), [`03-retrieval-mechanics.md`](03-retrieval-mechanics.md)
