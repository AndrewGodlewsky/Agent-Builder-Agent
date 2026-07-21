# Technical Build Review — Agent Builder (Copilot Studio package)

**Date:** 2026-07-21
**Scope:** Technical (not design) review of the shipped `Agent/` package — what could trip you up when actually creating this agent in Microsoft Copilot Studio.
**Method:** Read the full package (`00-agent-settings.md`, `01-instructions.md`, `README.md`, `knowledge/01–05`) and checked the risk claims against current Microsoft Learn docs.

> **Verified up front:** `.md` uploads are fine. Copilot Studio's supported knowledge file types explicitly include "Text (.txt, **.md**, .log)", so uploading the five `.md` knowledge files as-is works. (Source: [Upload files as a knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload).)

---

## Findings (worst-first)

### Build-blocking / setup gaps

**1. Missing prerequisite: Dataverse search must be enabled in the environment.**
Uploading files as an agent-level knowledge source in Copilot Studio *requires Dataverse search* turned on — an admin/environment setting. If it's off, you can't add the knowledge at all. `Agent/README.md:22-25` lists only a Copilot Studio license and "permission to add knowledge sources." This is the most likely thing to stop you at step 4. (Already noted internally at `knowledge/03-artifact-formats.md:377`; it just didn't reach the build guide.)
**Fix:** add "Dataverse search enabled in the target environment (admin action)" to Prerequisites.

**2. Conversation starters: doc says "three," lists four.**
`00-agent-settings.md:23` says "Add these three" then the table has **four** rows (Build / Fix / From my docs / Not sure); `README.md:37` also says "add the three suggested prompts."
**Fix:** pick one — drop a row or change the count to four.

**3. Setup never says to write a Description for each knowledge file.**
Under generative orchestration the agent selects which knowledge source to consult *by name + description* — `knowledge/04-platforms-and-quality.md:84` calls description quality "the main authoring lever," and the Learn upload flow makes Description an explicit step. `README.md:35` just says "upload all five files," which yields five undescribed sources and unreliable routing.
**Fix:** add a one-line description per file to `00-agent-settings.md` and a note in step 4 to enter them.

### Runtime reliability

**4. "Allow ungrounded responses = ON" fights the point of the knowledge base.**
Instructions demand "Ground every fact… never invent platform behaviour, schema fields" (`01-instructions.md:14`), but with ungrounded ON nothing enforces retrieval — the model will emit schema versions, limits, and portal steps from its own (possibly stale) memory instead of the five files. It's a genuine trade-off, not an oversight: ungrounded was turned ON because clarifying/follow-up questions are treated as ungrounded and stop working when it's OFF.
**Fix:** keep ON but harden `# SCOPE & GROUNDING` ("before stating any schema field, version number, or limit, retrieve it from knowledge; if not retrievable, say so"), and lean on Finding 5 so the method doesn't depend on retrieval.

**5. A reasoning-heavy agent is run off RAG over five large, table-dense docs — unnecessarily.**
The operating method (5-layer isolation algorithm, error-code decoder, manifest field tables) lives in knowledge that Copilot Studio *chunks*; semantic retrieval can return a partial chunk instead of a whole table. Key point: **this is a Copilot Studio agent, so the 8,000-char instruction limit does not apply** (that ceiling is declarative-only). `01-instructions.md` currently delegates almost everything to knowledge and stays short for no reason.
**Fix:** promote the non-negotiable procedure — greet/route logic, Workflow A/B steps, the five-layer order — into the instruction body; let knowledge hold *lookup* detail (schemas, error codes, archetypes). Instructions are always in-context; knowledge is best-effort.

**6. Moderation "High" can filter the agent's own responses.**
The agent constantly discusses jailbreak / prompt-injection / XPIA / "attack" — in its knowledge and whenever it helps troubleshoot guardrails — and pasted artifacts may contain injection-looking text. High RAI moderation can trip `OpenAIJailBreak` / `OpenAIndirectAttack` on this content. Documented as a failure mode at `knowledge/05-diagnostics.md:184,196`.
**Fix:** consider Medium, or keep High and expect to notch down; add an instruction line stating that discussing agent security is expected behavior (the documented mitigation).

**7. Five knowledge sources sits at the "~5 usable at a time" ceiling.**
`knowledge/03-artifact-formats.md:375` notes only ~5 sources are effectively usable and generative orchestration filters beyond that. At exactly five you have zero headroom and maximum routing contention.
**Fix:** consolidate into fewer, larger, well-described sources (e.g. merge 01+02 into a build reference, keep 05 diagnostics separate), or use file groups.

### Accuracy / maintenance

**8. Hard-coded versions will drift, and with ungrounded ON that yields *invalid* manifests silently.**
Knowledge pins `declarativeAgent v1.7`, `apiPlugin v2.4`, app manifest `1.19`, the Copilot-Credit rate table, and GPT 5.0→5.1. When Microsoft bumps these, the agent emits stale artifacts confidently — and since "unrecognized properties invalidate the whole document," one blended-from-memory field yields a manifest that fails validation, with **no tool in the agent to catch it** (zero tools shipped by design). Concrete landmine already present: archetype YAML uses lowercase `web_search` / `code_interpreter` (`knowledge/02-archetype-library.md:65,165`) while real manifest names are `WebSearch` / `CodeInterpreter` — echoing the archetype form into JSON output is invalid.
**Fix:** add a "verify current schema version before emitting" self-check; make the AgentSpec→manifest casing rule explicit in `03-artifact-formats.md`. Longer term, a validation flow (noted as a future enhancement) closes the loop.

**9. (minor) Fallback topic under generative orchestration.**
Editing the classic Fallback system topic (`README.md:39`) is harmless, but in generative mode off-topic handling is driven mostly by `# SCOPE`/`# GUARDRAILS` instructions, not that topic — so don't rely on the topic edit as the primary out-of-scope guardrail. Keep the instruction-level refusal as the real control.

---

## Bottom line

- **Findings 1–3** will actually interrupt the build (setup-doc edits).
- **Findings 4 and 5** most affect whether the finished agent behaves well, and they're linked: moving the method into instructions (5) is also the best hedge against the ungrounded-ON hallucination risk (4).
- Nothing here is a redesign — all edits to setup docs, the moderation/grounding settings, and where the method lives.

## Sources
- Upload files as a knowledge source (supported types, Dataverse-search requirement, per-file description) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload
- Knowledge sources summary — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- Internal cross-refs: `Agent/00-agent-settings.md`, `Agent/01-instructions.md`, `Agent/README.md`, `Agent/knowledge/02-archetype-library.md`, `03-artifact-formats.md`, `04-platforms-and-quality.md`, `05-diagnostics.md`
