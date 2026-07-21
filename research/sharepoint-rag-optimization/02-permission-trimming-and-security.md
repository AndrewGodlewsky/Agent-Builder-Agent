# Permission Trimming & Security at Retrieval

> How SharePoint knowledge respects permissions, why it can silently return
> nothing, and what that means for oversharing.

Confidence legend: ✅ VERIFIED (primary + 3-0) · 📄 DIRECTIONAL · ❓ UNCONFIRMED.

---

## 1. ✅ Permissions are enforced at retrieval time, per user

Across **every** SharePoint path (connector, file-upload, and the Retrieval API),
permission trimming happens **live, at query time**, using the **querying user's
Microsoft Entra ID (delegated permissions)**:

- The system performs a **live delegated-permission check against the source**
  before returning or summarizing anything.
- The user must have **at least Read** permission on the relevant sites/files.
- **No permission information is stored locally** — even for Path B, where content
  is copied into Dataverse, "all permission checks live with the source."

> ✅ *"Even though the system stores chunks and indexes locally in Dataverse, it
> performs a live check on the queries to make sure the current user has access to
> the data before providing a summary or response… The system doesn't store content
> permission information locally… all permission checks live with the source."*
> — [knowledge-unstructured-data](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data)

> ✅ *"The agent surfaces only content that the user has permission to access… At a
> minimum, the user must have Read permissions."*
> — [knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)

> ✅ *"The permissions model in Microsoft 365 ensures that individuals can only get
> results from the content they are allowed to access… [the Retrieval API] keeps
> your data in place."*
> — [Retrieval API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview)

**Takeaway:** you cannot use a SharePoint knowledge source to broadcast restricted
content to users who lack access. The trimming is identity-based and enforced at
the source, every query. This is a governance strength — and a testing gotcha
(§3).

---

## 2. ✅ The silent "no response" — the #1 troubleshooting trap

When the user lacks access, the agent does **not** error. It returns **nothing** —
silently:

> ✅ *"Generative answers over SharePoint rely on delegated permissions… a user
> must have read permissions on the relevant sites and files, or no search results
> will be returned… nor any errors or exceptions."*
> — [sharepoint-no-response](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/sharepoint-no-response)

> ✅ *"If the user doesn't have permission… the agent responds with 'no response.'"*
> — [knowledge-add-sharepoint](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)

Combined with the **top-3-results** rule ([01](01-how-sharepoint-rag-works.md) §4):
if a user can only see documents that rank 4th+, they get **no answer** even though
relevant content exists — because the top 3 (which they can't see) were filtered
out and nothing remains to ground on.

---

## 3. ✅/📄 Testing implication: test as a real end user

Because trimming is per-identity:

- ✅ An **admin/site-owner tester will see results a regular user won't.** Always
  test with an account that has the *actual* permissions of your target audience.
- 📄 If answers work for you but users report "no response," **suspect
  permissions first**, before content or config.

---

## 4. 📄 Oversharing — the flip side

Permission trimming is only as good as your SharePoint permissions. Multiple
practitioner sources (directional, not primary-verified) stress that Copilot/agents
**surface content users technically *can* access but perhaps *shouldn't***:

- If a library is over-permissioned (e.g. "Everyone" has Read), the agent will
  happily ground answers on it for everyone.
- Site owners should **audit and tighten permissions before rollout** — the agent
  makes latent oversharing suddenly very visible and very queryable.

*(Sources: practitioner blogs on Copilot + SharePoint permissions — directional.
Microsoft's own privacy doc confirms the trimming model but the oversharing
*remediation* guidance is community-sourced.)*

---

## 5. ✅ Sensitivity labels (connector path)

The SharePoint connector path **respects sensitivity labels** as part of its
filtering — another enforcement layer beyond Read permissions.
([knowledge-unstructured-data](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data))

---

## Security summary

| Behavior | Detail | Confidence |
|---|---|---|
| When trimming happens | At retrieval / query time | ✅ |
| Identity used | Querying user's Entra ID (delegated) | ✅ |
| Minimum access needed | Read | ✅ |
| Permission storage | None local — checked at source | ✅ |
| No-access behavior | Silent "no response," no error | ✅ |
| Interaction with top-3 | Inaccessible top hits → user may get nothing | ✅ (inference from two ✅ facts) |
| Sensitivity labels | Respected (connector path) | ✅ |
| Oversharing risk | Real; tighten permissions pre-rollout | 📄 |
| Testing | Test as a real end user, not admin | ✅/📄 |
