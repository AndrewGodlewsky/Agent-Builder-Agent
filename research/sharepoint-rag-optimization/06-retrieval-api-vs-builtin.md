# Retrieval API vs. Built-in SharePoint Knowledge

> When to use Copilot Studio's built-in SharePoint knowledge source vs. the
> Microsoft 365 Copilot Retrieval API — and the format limits that decide it.

Confidence legend: ✅ VERIFIED (primary + 3-0) · 📄 DIRECTIONAL · ❓ UNCONFIRMED.

---

## 1. ✅ What the Retrieval API is

The **Microsoft 365 Copilot Retrieval API** is a **distinct grounding option** —
not the same as Copilot Studio's point-and-click SharePoint knowledge source:

- Returns **relevant text chunks from the same hybrid/semantic index that powers
  M365 Copilot** — the tenant index you already have (licensed).
- **No separate replicated/chunked/secured index** — "keeps your data in place."
- Grounds from **SharePoint, OneDrive, and Copilot connectors**.
- Scopable with **Keyword Query Language (KQL)** (URLs, date ranges, file types).
- **Currently in Preview.**

> ✅ *"Returns relevant text chunks from the hybrid index that powers Microsoft 365
> Copilot… without the need to replicate, index, chunk, and secure your data in a
> separate index."*
> — [Retrieval API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview)

---

## 2. ✅ The Retrieval API's format limits (important)

The API has **explicit document-type limits** — and these are the sharpest
constraints to weigh:

> ✅ *"Semantic retrieval and hybrid retrieval is only supported for .doc, .docx,
> .pptx, .pdf, .aspx, and .one file extensions. All other file extensions only
> support lexical retrieval… Retrieval from text in tables is limited to .doc,
> .docx, and .pptx… Retrieval from nontextual content, including images and charts,
> is not supported."*
> — [Retrieval API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview)

| Content | Semantic/hybrid retrieval? |
|---|---|
| .doc/.docx/.pptx/.pdf/.aspx/.one | ✅ Yes |
| Other extensions | Lexical only |
| Table text | Only .doc/.docx/.pptx |
| Images / charts | ❌ Not supported |

> ⚠️ **These limits are documented for the Retrieval API specifically.** Whether
> Copilot Studio's **built-in** SharePoint connector has the *same* format handling
> is **❓ NOT confirmed** (open question in [07](07-sources-and-open-questions.md)).
> Don't assume they're identical — but the overlap (same underlying index) makes
> these limits a reasonable *worst-case* planning assumption.

---

## 3. ✅ Decision: which path?

| Use... | When |
|---|---|
| **Built-in SharePoint knowledge source** (connector) | Default for Copilot Studio agents. Point-and-click, real-time, permission-trimmed, 25 URLs, top-3 grounding. Best when the maker experience and native integration matter. |
| **File upload (Dataverse)** | Small, curated, stable document sets; need the 512 MB ceiling; OK with 4–6h sync; want content isolated in Dataverse. |
| **Retrieval API** | **Custom / code-built** grounding (e.g. a pro-code agent or app) where you want to query the M365 hybrid index directly with **KQL scoping** and no separate index to maintain. More control, more build effort, Preview status. |

> 📄 For most site-owner-driven Copilot Studio scenarios, the **built-in
> connector** is the right default and the search-schema/filters playbook
> ([04](04-search-schema-playbook.md)) is where your effort pays off. Reach for the
> Retrieval API only if you're building a custom grounding pipeline and need
> KQL-level control.

---

## 4. ✅ Common thread: they all ride your tenant semantic index

Whether via the connector, the tenant index, or the Retrieval API, licensed
grounding rides the **same automatically-built tenant semantic index**
([01](01-how-sharepoint-rag-works.md) §2). So **improving your SharePoint content
and permissions improves all three paths at once** — the doc-hygiene and
permission work is never wasted regardless of which grounding surface you pick.

---

## Summary

- The **Retrieval API** is a separate, code-level grounding path over the same
  tenant index; **Preview**; KQL-scopable; **no image/chart retrieval**, table text
  only in Office formats.
- For built-in Copilot Studio agents, the **connector is the default**; the
  Retrieval API is for **custom pipelines**.
- **Format limits (images/charts unsupported, table text Office-only) are ✅ for the
  Retrieval API but ❓ for the built-in connector** — plan conservatively.
- All licensed paths share the tenant semantic index, so **content + permission
  hygiene helps universally.**
