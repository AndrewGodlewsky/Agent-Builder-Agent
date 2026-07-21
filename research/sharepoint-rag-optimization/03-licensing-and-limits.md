# Licensing, Limits & What's Structurally Impossible

> What your M365 Copilot license unlocks, the file-size ceilings, the critical
> toggle, and the query types you simply cannot support.

Confidence legend: ✅ VERIFIED (primary + 3-0) · 📄 DIRECTIONAL · ❓ UNCONFIRMED.

> ⚠️ **These numbers change frequently.** Verified accurate as of 2026-07;
> re-check [requirements-quotas](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)
> before you rely on them.

---

## 1. ✅ What the M365 Copilot license (same tenant) unlocks — YOU HAVE THIS

You told me the tenant has M365 Copilot in the same tenant, so the following are
all available — **but two require you to flip settings ON**:

| Capability | Without license | **With license (your case)** |
|---|---|---|
| SharePoint file ceiling (generative answers) | **7 MB** | **200 MB** |
| PDF / PPTX / DOCX ceiling | 7 MB | **512 MB** |
| Enhanced search results | must be **OFF** | must be **ON** |
| Tenant graph grounding with semantic search | n/a | **available — turn ON** |
| Retrieval quality | baseline | **higher precision, more context** |

> ✅ *"For better search results from SharePoint and support of files up to 200 MB
> in size, use a Microsoft 365 Copilot license in the same tenant… and turn on
> tenant graph grounding with semantic search."*
> — [requirements-quotas](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)

> ✅ *"SharePoint and Microsoft Copilot connectors support files up to 512 MB if
> they have PDF, PPTX, or DOCX extensions."*
> — [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)

> ✅ *"If you have a Microsoft 365 Copilot license… the maximum file size is 200
> MB. You must also turn on the Enhanced search results feature."*
> — [sharepoint-no-response](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/sharepoint-no-response)

### 🔧 Action: turn ON "Enhanced search results" + "Tenant graph grounding with semantic search"

These are the two switches that convert your license into actual capability. If
Enhanced search results is left OFF (the no-license default), you're capped at 7 MB
**even though you're licensed**. Tenant graph grounding costs "a small increase in
latency" in exchange for "greater volume of context, with greater precision."
([knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint))

---

## 2. ✅ The file-size gotcha for large PDFs

Oversized files don't fail loudly — they fail **invisibly**:

> ✅ *"Larger files can be stored in SharePoint and are returned by a Microsoft
> Graph search, but aren't processed by generative answers. As an alternative, you
> can upload your own files, which can be up to 512 MB in size."*
> — [sharepoint-no-response](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/sharepoint-no-response)

So a 300 MB scanned PDF in SharePoint will:
- ✅ **appear as a search hit** (Graph returns it), but
- ✅ **not be processed** by generative answers → no grounded content from it.

**This is worse than a hard error** because it looks like it "found" the doc. See
[05](05-document-optimization-playbook.md) for large-PDF strategy.

---

## 3. ✅ Ceilings at a glance

| Limit | Value | Path |
|---|---|---|
| SharePoint generative answers, general files | 200 MB (licensed) / 7 MB (not) | Connector |
| SharePoint generative answers, PDF/PPTX/DOCX | 512 MB | Connector |
| File-upload knowledge | 512 MB per file | Dataverse |
| SharePoint URLs per agent (generative) | 25 | Connector |
| Results grounding an answer | Top 3 | Both |
| File-upload sync cadence | 4–6 hours | Dataverse |

---

## 4. ✅ What is STRUCTURALLY IMPOSSIBLE (and can't be fixed with instructions)

This is critical for your agent design. Some query types **cannot be answered** by
a SharePoint knowledge source — no prompt, instruction, or setting changes this:

> ✅ *"Queries to a SharePoint knowledge source that reference a file or document
> name can't be answered. For example, if a user asks, 'What is the mitigation
> provided in file-name.pdf?'"*
>
> *"Metadata filtering at the folder or knowledge source level isn't supported. The
> agent can't answer queries related to what files exist in a folder and provide a
> count of the files in the folder."*
>
> *"Queries related to column metadata filtering properties aren't supported"* (e.g.
> "List all files with a column name of X and a value of Y").
> — [requirements-quotas](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)

| ❌ Cannot be answered | Example |
|---|---|
| Reference a file **by name** | "What's in *policy-v3.pdf*?" |
| **List** files in a folder | "What documents are in the HR folder?" |
| **Count** files | "How many files are in this library?" |
| **Filter by column value** | "List all files where Status = Approved" |

**Tension to note (open question):** SharePoint's search schema *can* make column
metadata queryable, yet Copilot Studio explicitly **doesn't support** column-value
filtering at the knowledge-source level. So even if you build managed properties
for metadata, the agent won't do "list/filter by column" queries. If you need those,
you need a **different mechanism** (a Dataverse table, a Power Automate flow, or a
custom tool) — not SharePoint knowledge. Tracked in
[07](07-sources-and-open-questions.md).

---

## 5. 📄 Reminder: instructions can't steer retrieval

From the broader research (see
[`../copilot-studio-knowledge/01-knowledge-vs-instructions.md`](../copilot-studio-knowledge/01-knowledge-vs-instructions.md)):
agent instructions govern **summarization after retrieval**, not retrieval itself.
Microsoft says to **remove any instruction that tries to influence document
retrieval.** So you cannot instruction your way around the limits in §4 — you must
design around them structurally.

---

## Licensing & limits summary

- ✅ **You're licensed** → 200 MB / 512 MB ceilings + higher precision, **but you
  must turn ON Enhanced search results + tenant graph grounding.**
- ✅ **Oversized files fail silently** — appear in search, don't ground answers.
- ✅ **Top-3-only** grounding makes precision paramount.
- ✅ **File-by-name, folder listing/counting, column-value filtering are
  impossible** — design around them; instructions can't help.
