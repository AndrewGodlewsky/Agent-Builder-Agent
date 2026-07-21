# Knowledge Types, Limits & Config Trade-offs

> **Sub-question 4:** Supported source types, their limits, and configuration
> trade-offs.

> ⚠️ **Copilot Studio quotas change frequently and several cited pages carry
> preview / "subject to change" banners. Treat every number below as
> "accurate as of 2026-07 — re-verify against live docs before you build."**
> Primary quota source:
> [requirements-quotas](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)
> (updated 2026-07-21).

---

## 1. Supported knowledge source types

Copilot Studio supports **five** knowledge source types
([knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)):

| Source type | Retrieval backend | Notes |
|---|---|---|
| **Public website** | Bing Custom Search | Restricted to configured domains; limited to **two subpage depth** |
| **Documents (uploaded files)** | Dataverse (chunked + vector-indexed) | Stored per-agent in Dataverse |
| **SharePoint** | GraphSearch | **Identity/permission-trimmed** (see §4) |
| **Dataverse tables** | Retrieval-augmented technique over structured data | Query structured records |
| **Enterprise data via connectors** | Indexed by Microsoft Search | Graph connectors surface enterprise systems |

> A separate developer surface — the **M365 Copilot Retrieval API** and
> **Azure AI Search** — can also provide grounding for custom/large-scale
> scenarios, but those are distinct from the five built-in source types above.
> See [03-retrieval-mechanics.md](03-retrieval-mechanics.md) §8.

---

## 2. Per-source input counts depend on orchestration mode

The number of sources/inputs you can attach differs between **generative** and
**classic** orchestration. Representative figures from the knowledge doc:

| Source type | Generative orchestration | Classic orchestration |
|---|---|---|
| Public website | 25 | 4 |
| SharePoint | 25 URLs | 4 |
| Dataverse | Unlimited | 2 sources, up to 15 tables |

*(These are per-source-type input limits, distinct from the agent-wide hard caps
in §3.)*

**Trade-off:** generative orchestration unlocks substantially more inputs (and
proactive, automatic retrieval), which is one more reason it's the recommended
default for knowledge-heavy agents.

---

## 3. Hard quotas (per agent)

From [requirements-quotas](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)
and [retrieval-augmented-generation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/retrieval-augmented-generation):

| Limit | Value |
|---|---|
| **Knowledge sources per agent** (all types combined) | **500** |
| **Uploaded files per agent** | **500** |
| **Max size per uploaded file** | **512 MB** (Dataverse storage) |
| **Dataverse tables per source** | **15** |
| **Public website subpage depth** | **2** |
| **SharePoint site URLs per agent** (generative orchestration) | **25** |

---

## 4. SharePoint: license-gated file size + permission trimming

Two SharePoint-specific behaviors matter a lot for planning:

### a) File-size ceiling is gated by M365 Copilot licensing

> Without a same-tenant Microsoft 365 Copilot license, generative answers can only
> use SharePoint files **under 7 MB**. With the license (plus tenant graph
> grounding and semantic search), files up to **200 MB** are supported.
> — [retrieval-augmented-generation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/retrieval-augmented-generation)

| Scenario | Max SharePoint file size for generative answers |
|---|---|
| **No** same-tenant M365 Copilot license | **7 MB** |
| **With** M365 Copilot license + tenant graph grounding + semantic search | **200 MB** |

**Trade-off:** if you plan to ground on large SharePoint documents, your
effective ceiling depends on licensing — verify the tenant's M365 Copilot status
before committing to a SharePoint-heavy design.

### b) Retrieval is permission-trimmed (identity-based)

> *"The agent surfaces only content that the user has permission to access… the
> user must have Read permissions… If the user doesn't have permission… the agent
> responds with 'no response'… calls that use generative answers are made on
> behalf of the user."*
> — [knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)

This is a **security-relevant** property, distinct from behavior control:

- Retrieval runs **on behalf of the querying user's identity**.
- Users only see content they have **at least Read** access to.
- No access → the agent returns **"no response"** for that content.

**Implication:** you cannot use SharePoint knowledge to broadcast restricted
content to users who lack permissions — the trimming is enforced at retrieval.
Good for governance; something to account for when testing (an admin tester may
see results a regular user won't).

---

## 5. Config trade-offs cheat-sheet

| Decision | Options | Trade-off |
|---|---|---|
| Orchestration mode | Generative vs. classic | Generative = more inputs, proactive/automatic retrieval, node-level scoping. Classic = fewer inputs, fallback-only search. **Generative recommended for knowledge-heavy agents.** |
| Grounding strictness | `Allow ungrounded responses` on/off | Off = must ground every turn (high assurance, may refuse). On = can answer from model knowledge (flexible, less contained). |
| Retrieval scope | Agent-level list vs. generative answers node | Agent-level = all sources searched. Node = restrict to specific sources (overrides agent-level). |
| SharePoint big files | License present or not | 7 MB vs. 200 MB ceiling. |
| Source type | Website / files / SharePoint / Dataverse / connectors | Match to where the authoritative data lives; each has its own backend + limits. |
| Large-scale / custom retrieval | Built-in knowledge vs. M365 Retrieval API / Azure AI Search | Built-in = point-and-click, capped. API/Azure AI Search = code path, more control, more setup + licensing/cost. |

---

## 6. Practical limits worth designing around

- **Top-3-chunks-per-source** (from [03](03-retrieval-mechanics.md)) means adding
  more sources broadens coverage but each contributes little depth. Curate
  sources; don't dump everything in.
- **Chunking is not tunable** — you can't control how files are split.
- **512 MB per file** is generous for upload, but SharePoint's 7/200 MB
  generative-answer ceiling is the real constraint for large docs.
- **500 sources / 500 files per agent** is a ceiling, not a target — retrieval
  quality favors curated, well-named, well-described sources over volume.

---

## Summary

- **Five built-in source types:** public website, uploaded files (Dataverse),
  SharePoint, Dataverse tables, enterprise connectors (Microsoft Search).
- **Caps:** 500 sources & 500 files per agent; 512 MB/file; 15 Dataverse
  tables/source; website depth 2; 25 SharePoint URLs (generative).
- **SharePoint is special:** file-size ceiling is **license-gated (7 MB → 200
  MB)** and retrieval is **permission-trimmed per user**.
- **Generative orchestration** unlocks more inputs and proactive retrieval — the
  recommended default.
- **Re-verify all numbers against live docs** — this area changes fast.
