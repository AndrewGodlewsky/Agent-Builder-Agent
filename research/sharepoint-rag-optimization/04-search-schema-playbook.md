# Site-Owner Playbook: Search Schema & Filters

> The most concrete, verified levers you have as a site owner. This is where
> "advanced things you can do" actually lives.

Confidence legend: ✅ VERIFIED (primary + 3-0) · 📄 DIRECTIONAL · ❓ UNCONFIRMED.

---

## 1. ✅ Managed-property attributes — your core control surface

Each managed property has independent attributes that control how it behaves in
search. These are the dials a site owner turns:

| Attribute | What it does | RAG use |
|---|---|---|
| **Searchable** | Adds content to the **full-text index**; matched by free-text queries | Turn ON for content you want the agent to find by keyword/semantics |
| **Queryable** | Enables **property-scoped queries** (e.g. `author:Smith`) — but the property name must be named in the query | Enables targeted filtering (though Copilot Studio's *own* query limits still apply — see [03](03-licensing-and-limits.md) §4) |
| **Retrievable** | Allows the value to be **returned in results** | Disable to **hide** content from results even if indexed |
| **Refinable / Sortable** | Enable refiners/sorting | ⚠️ **Not supported in the modern search experience** |

> ✅ *"If you set a managed property to be searchable, the content is added to the
> index… set the author property to be queryable… users can query for author:Smith…
> to prevent the content in a managed property from showing up as search results,
> you can disable the retrievable setting."*
> — [manage-search-schema](https://learn.microsoft.com/en-us/sharepoint/manage-search-schema)

> ✅ *"Retrievable | Enables the content… to be returned in search results"* ;
> Refinable and Sortable are both *"Not supported in the modern search
> experience."*
> — [search-schema-overview](https://learn.microsoft.com/en-us/sharepoint/search/search-schema-overview)

> 📄 Minor dependency: **Refinable requires Queryable**, so the attributes aren't
> fully independent — but Refinable/Sortable are moot for modern search anyway.

### 🔧 Actions
- **Make sure the content columns you care about are Searchable** and mapped (see
  §2) so they enter the full-text index.
- **Disable Retrievable** on noisy/internal properties you don't want surfaced in
  grounding.
- **Don't rely on Refinable/Sortable** — they don't work in modern search.

---

## 2. ✅ Map crawled → managed properties, then re-crawl

New metadata only becomes searchable if it's **mapped to a managed property** and
the content is **re-crawled**:

> ✅ *"If you add a managed property, you must map it to a crawled property to get
> content into the index. After the site, library, or list is crawled, users can
> search for the content and metadata of new or changed managed properties…
> [changes] take effect only after the content is re-crawled."*
> — [manage-search-schema](https://learn.microsoft.com/en-us/sharepoint/manage-search-schema)

### 🔧 Actions
1. In the **SharePoint admin center → Search → Manage Search Schema**, find or
   create the managed property for the metadata you want searchable.
2. **Map it to the appropriate crawled property.**
3. **Trigger/await a re-crawl** (SPO controls crawl scheduling per-tenant; you have
   less direct control than on-prem — 📄 you may need to re-save items or wait).
4. Verify the content is now returned by search before expecting the agent to use
   it.

> 📄 Caveat: the crawled/managed mechanics are documented on SharePoint **Server**
> pages. In **SharePoint Online**, the schema is managed per-tenant via the admin
> center with **less crawl-scheduling control**. Attribute *semantics* are
> authoritative; crawl-*timing* specifics are directional.

---

## 3. ✅ Copilot Studio search query filters — the highest-ROI knob

On the **SharePoint knowledge source itself**, you can set search query filter
parameters to shape what's searched. This is a Copilot Studio-side lever (no admin
center needed):

> ✅ *"To improve the performance of your agent's SharePoint knowledge source,
> specify search query parameters… For example, you could specify that you only
> want searches for items that were modified in the last six months."* Filter fields:
> **Title, Author, Modified by, Modified on** — "build your filters to include or
> exclude information."
> — [knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)

### 🔧 Actions (given only top-3 results ground each answer)
- **Filter out stale content**: e.g. only items **Modified on** within the last
  N months, so obsolete docs don't crowd the top 3.
- **Scope by Author** if authoritative content comes from specific owners.
- **Filter by Title** patterns to include/exclude document families.
- Use filters to **shrink the candidate set toward your authoritative content** —
  this directly improves the odds the right doc lands in the top 3.

---

## 4. ✅ Restrict library scope

Because only 3 results ground each answer and near-duplicates are harmful
([01](01-how-sharepoint-rag-works.md) §4):

### 🔧 Actions
- **Point the knowledge source at the narrowest URL** that contains authoritative
  content (a specific library/folder), not the whole site, when possible.
- **Remove or archive superseded/duplicate documents** so a single authoritative
  version wins the top-3 slot.
- Keep **one canonical document per topic** rather than many overlapping ones.

*(📄 The "narrow scope + dedupe" guidance is inference from the ✅ top-3 mechanic,
not a directly-quoted Microsoft instruction — but it follows directly.)*

---

## 5. ✅ Freshness

- ✅ **Connector path is real-time** — content changes are reflected on next query
  (subject to SharePoint's own crawl/index latency).
- ✅ **File-upload path lags 4–6 hours** — don't use it for fast-changing content.
- 🔧 Use the **Modified on** filter (§3) to bias toward fresh content.

---

## 6. What the schema does NOT get you

Be clear-eyed: schema tuning improves **what's findable and returned**, but it
**cannot** override Copilot Studio's structural query limits
([03](03-licensing-and-limits.md) §4):

- Even if you make a column **Queryable**, the agent still **won't** do
  "list/count/filter by column value" queries.
- Schema can't make **file-by-name** questions work.

So schema tuning is about **precision and disambiguation of grounded answers** —
not about enabling database-style queries.

---

## Search-schema playbook checklist

- [ ] ✅ Enhanced search results **ON** + tenant graph grounding **ON** (you're
      licensed — [03](03-licensing-and-limits.md)).
- [ ] ✅ Authoritative content columns are **Searchable** and **mapped** to managed
      properties.
- [ ] ✅ Noisy properties set **not Retrievable**.
- [ ] ✅ **Search query filters** set on the knowledge source (Modified on / Author
      / Title) to exclude stale/irrelevant content.
- [ ] ✅ Knowledge source URL scoped to the **narrowest authoritative** library.
- [ ] ✅ **Duplicates/superseded docs archived** so one canonical doc wins top-3.
- [ ] ✅ Re-crawl completed after any schema change.
- [ ] ✅ Verified content is returned by SharePoint search **as a real end user**
      ([02](02-permission-trimming-and-security.md)).
