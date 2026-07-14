# 01 · Failure-mode taxonomy + fix patterns (M365 declarative + Copilot Studio)

_Research findings — grounded in current Microsoft Learn documentation + Microsoft Q&A + practitioner sources (fetched 2026-07-14). Cited doc `ms.date` values range Nov 2025 – Jun 2026; the Copilot Studio **error-codes** page is dated 2026-06-04 and the extensibility **known-issues** page 2026-03-16._

> **Purpose & fit.** This is the diagnostic core of Builder Agent v2 (`../map.md`). It catalogs how *already-built* agents misbehave, mapping each **symptom → root cause (in AgentSpec terms) → fix pattern**, with surface-specific notes. It **extends** — does not repeat — the two grounding files: `../builder-agent/research/01-platform-building-blocks.md` (the platform limits and the declarative-vs-Copilot-Studio delta) and `02-what-makes-agent-good.md` (the instruction/knowledge/guardrail best practices and the hybrid AgentSpec skeleton). Where a limit or best practice is already established there, this file cites it as `[BB §x]` / `[WMG §x]` rather than re-deriving it.

> **AgentSpec zones used as the root-cause vocabulary** (from the hybrid spec, `[WMG §6]`): `# SCOPE` (role/purpose/in-scope boundary), `# GROUNDING` (grounding posture + which sources), `KNOWLEDGE` (the configured knowledge sources/config), `ACTIONS` (API plugins / tools / flows), `# GUARDRAILS` (restrictions, refusal/fallback, injection defense), **orchestration setting** (declarative fixed pipeline vs. Copilot Studio classic/generative), **moderation level** (Copilot Studio Lowest→Highest, default High). A root cause is expressed as "which zone is wrong," which is exactly what the diagnose→revise engine emits as a change-set.

> **Surface reminder.** *Declarative agent* = rides Copilot's fixed, sequential grounding-then-tool pipeline; maker controls only instructions, knowledge, plugins `[BB A.6]`. *Copilot Studio agent* = its own runtime with **classic** (topic/trigger-phrase) or **generative** (LLM planner) orchestration, topics, tools, agent flows, triggers `[BB Part B]`. Many symptoms look identical on both surfaces but have **different root layers** — that split is the point of the "surface-specific" column.

---

## 0. Master quick-reference (symptom → primary zone → one-line fix)

| # | Symptom | Primary AgentSpec zone | One-line fix |
|---|---|---|---|
| 1 | Over-declines / refuses valid queries | `# SCOPE` + `# GUARDRAILS` (+ moderation level; + "Allow ungrounded" off) | Loosen the in-scope boundary; state expected behavior; re-enable ungrounded/follow-ups if grounding was forced off |
| 2 | Hallucinates / ungrounded answers | `# GROUNDING` + `KNOWLEDGE` (grounding posture) | Turn **Allow ungrounded responses OFF** (Studio); add/scope the authoritative source; move to Studio if strict grounding needed |
| 3 | Ignores / under-uses knowledge | `KNOWLEDGE` config + instruction references | Fix licensing/permissions/auth (silent-fail); name the source in instructions; scope tighter |
| 4 | Retrieves *wrong* knowledge | `KNOWLEDGE` (too many/overlapping sources) + `# GROUNDING` | Prune/de-duplicate sources; sharpen source names+descriptions; scope to folders/sites; tenant-graph semantic search |
| 5 | Wrong / failed / skipped tool-or-action call | `ACTIONS` (metadata, schema, auth) + orchestration | Sharpen tool name+description; enable "decide dynamically"; fix OpenAPI/auth; read the error code |
| 6 | Generative orchestration loops / stalls | orchestration setting + topic/flow design | Ensure topics reach a terminal node; cap steps; simplify instructions; watch `InfiniteLoopInBotContent` |
| 7 | Moderation over-blocks / fallback fires too often | moderation level + `# GUARDRAILS` + Fallback topic | Lower moderation from High; clean injection-looking knowledge; edit the **Fallback system topic**, not instructions |
| 8 | Tone / format / output drift | `# GUARDRAILS` output contract (+ model auto-upgrade) | Add explicit tone/verbosity/format contract; add literal-execution header after model upgrades |
| 9 | 8,000-char instruction truncation | instruction body length (declarative only) | Cut to essentials; move logic to topics/flows (Studio) — never offload to knowledge |
| 10 | Latency / Copilot-Credit blowout | `ACTIONS` + orchestration + metered features | Replace flows with HTTP node; cache in variables; cut premium features; use estimator |
| 11 | Surface mismatch (built declarative, needed Studio) | orchestration setting (whole-surface) | Re-platform to Copilot Studio when autonomy/loops/strict-grounding/external-channels required |

---

## 1. Over-declines / refuses valid queries

**What the maker sees:** the agent says "I can't help with that," "that's outside my scope," or gives the fallback message to questions that are clearly in its remit.

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| `# SCOPE` boundary written too narrowly | The in-scope rule ("Only respond to messages relevant to X, otherwise say you can't help" `[WMG §4]`) is the primary refusal lever. If X is under-specified, valid adjacent questions fall outside it. | Broaden/enumerate in-scope topics; add positive examples of valid-but-adjacent queries; add a few-shot **Valid** example that currently gets refused. |
| `# GROUNDING` posture = **Allow ungrounded responses OFF** (Copilot Studio) | With this OFF, the agent **blocks any turn where it didn't call a knowledge source or tool** — and it also **disables follow-up/clarifying questions** because those count as ungrounded `[WMG §2]`. Legit chit-chat, clarifications, and reasoning-only answers get suppressed. | If the agent genuinely needs to answer beyond retrieved content, turn ungrounded **ON**; if it must stay strict, add explicit topics/tools for the valid cases so a grounded path exists. ([knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)) |
| moderation level too **High** | Default is **High**; higher = fewer answers, stricter filtering `[WMG §4]`. A domain with medical/violence/legal vocabulary trips content filters on benign queries. | Lower agent (or topic-level) moderation one notch; state that the behavior/vocabulary is expected in instructions. (See §7.) |
| `# GUARDRAILS` over-restrictive rules | "Never do X" rules or a `literal-execution header` can over-generalize and cause blanket refusal. | Replace prohibitions with scoped positive instructions ("say what to DO, not what to avoid" `[WMG §1]`). |

**Surface-specific**
- **Declarative:** no "Allow ungrounded" toggle — refusals are driven by `# SCOPE`/`# GUARDRAILS` wording and by Copilot's own RAI. Agent Builder can only *prioritize* sources, not force grounding `[BB A.4]`, so over-decline here is almost always instruction-driven.
- **Copilot Studio:** first suspect the **Allow ungrounded responses** switch and **moderation level**; both are settings, not instructions. Evaluation signal: an *architecture/robustness* eval category failing = "too strict" `[WMG §5]`.

---

## 2. Hallucinates / answers ungrounded

**What the maker sees:** plausible but unsupported answers; the agent invents facts when the source lacks them, or blends model knowledge with retrieved content. A documented pattern: the agent **starts with the right (grounded) answer, then switches mid-response** to an ungrounded one. ([Q&A: starts right then switches](https://learn.microsoft.com/en-us/answers/questions/5635444/copilot-studio-agent-why-does-it-start-with-the-ri), [Q&A: inconsistent/hallucinatory](https://learn.microsoft.com/en-us/answers/questions/5654951/inconsistent-and-hallucinatory-responses-from-copi))

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| `# GROUNDING` posture allows model knowledge | **Allow ungrounded responses ON** (Studio default) lets the model answer from general knowledge when no source is hit. | Set **Allow ungrounded responses OFF** to block any turn not grounded in a source/tool — the strict-grounding control Agent Builder lacks. Caveat: OFF is **not a guarantee** of zero general knowledge (model may still blend) and it disables follow-ups `[WMG §2]`. ([knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio), [faqs-generative-answers](https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-answers)) |
| `KNOWLEDGE` missing/insufficient for the question | No source covers the query, so the model fills the gap. | Add the authoritative source; test the same query **with and without** the source to confirm grounding actually flips behavior `[WMG §2]`, `[BB A.4]`. |
| `# GUARDRAILS` lacks a "don't invent" instruction | No explicit "if the answer isn't in the sources, say you don't know" rule. | Add an explicit uncertainty rule + route-to-human; add a self-check gate `[WMG §1]`. |
| `# GROUNDING` citation tampering | Instructions that mention "citation/reference" or reshape citation format can make the orchestrator treat responses as ungrounded and **discard** them `[WMG §1]`. | Remove any citation-shaping language from instructions. |

**Surface-specific**
- **Declarative:** Agent Builder's "Only use specified sources" **only prioritizes**, it cannot fully block general model knowledge — Microsoft explicitly says use Copilot Studio for strict grounding `[BB A.4]`. So on declarative, hallucination is partly a **surface-ceiling** problem (see §11), mitigated only by tighter instructions + better sources.
- **Copilot Studio:** the fix is a **setting** (ungrounded OFF) plus optional **tenant graph grounding with semantic search** to raise retrieval precision `[BB B.3]`.

---

## 3. Ignores or under-uses a knowledge source

**What the maker sees:** the source is attached, but the agent never cites it or answers as if it weren't there. Frequently this is a **silent failure**, not a visible error.

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| `KNOWLEDGE` **licensing** gap (silent) | **SharePoint/OneDrive grounding requires an active Copilot license.** Without it (e.g. CDX demo tenants), the agent provisions fine but **grounded retrieval fails silently** and returns the generic "Sorry, I wasn't able to respond." | Assign a Copilot license (or **Microsoft 365 Copilot Developer License** for test tenants). ([known-issues](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues)) |
| `KNOWLEDGE` **auth/permissions** (silent) | SharePoint grounding needs **User authentication** (service principals unsupported), the signed-in user must have **≥Read** on the site, and the URL in `items_by_url` must be reachable. Any gap → silent failure. | Verify user access, switch connection to User auth, confirm Read permission. ([known-issues](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues)) |
| `KNOWLEDGE` data defect | A **SharePoint file with null characters in its filename returns no results.** | Rename the file. ([known-issues](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues)) |
| Instruction doesn't reference the source | Best practice is to **name each knowledge source in the instructions** with a when-to-use hint `[WMG §1]`. Unreferenced sources get under-used, especially with many sources. | Add "Use `<SourceName>` for <question type>" to instructions. |
| `# GROUNDING` too many sources dilute selection | Generative orchestration filters sources with an internal GPT model when there are **>25**; over-broad corpora add noise ("less is more") `[BB B.3]`, `[WMG §2]`. | Prune to the sources needed for expected questions; scope tightly (specific sites/folders/channels). |

**Surface-specific**
- **Declarative:** the silent SharePoint/OneDrive failure modes above are declarative-specific and licensing/auth-driven — check those **first**. Per-agent caps also matter (SharePoint 100 items/+1 list truncated at 20k rows; OneDrive 50; embedded 20) `[BB A.4]`.
- **Copilot Studio:** runtime knowledge failures surface as **error codes** you can read — `SharePointSearchFailed`, `SharePoint429/500/503`, `DataverseSearchFailed`, `DataverseStructured401/429/500/503`, `FoundryIQSearchFailed`, `BingSearchFailed`. 401 = reauth/permission; 429 = throttling (retry/backoff); 5xx = service-side (retry). ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes))

---

## 4. Retrieves the *wrong* knowledge

**What the maker sees:** the agent answers confidently from the wrong document/site/connector, or mixes sources.

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| `KNOWLEDGE` sources overlap / weak descriptions | Generative orchestration picks sources by **name + description** (the primary authoring lever) `[BB B.2]`. Overlapping or vaguely-named sources → wrong pick. | Give each source a distinct, specific name + description; remove near-duplicates. ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions)) |
| `# GROUNDING` scope too broad | "All my chats" / whole-site sources pull adjacent-but-wrong material. | Scope to specific Teams channels/threads, SharePoint folders/sites `[WMG §2]`. |
| `KNOWLEDGE` retrieval precision low | Default retrieval may rank the wrong chunks. | Enable **tenant graph grounding with semantic search** (Studio) for higher precision on SharePoint/connector files `[BB B.3]`. |
| Custom-metadata query unsupported (declarative) | "Get ServiceNow tickets assigned to me" fails when "Assigned To" is **custom metadata not mapped to connection schema labels** — a documented known issue. | Query by title/description match instead; map metadata to label properties where possible. ([known-issues](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues)) |
| Stale web grounding | Scoped web search grounds on **Bing-indexed** content only — stale for dynamic/JS pages `[BB A.4]`. | Don't rely on scoped web search for recency; use a connector/API for live data. |

**Surface-specific**
- **Declarative:** limited retrieval knobs — the fix is mostly **source pruning + scoping** and instruction hints; no semantic-search toggle in Agent Builder.
- **Copilot Studio:** name/description tuning + semantic search + (classic only) marking a trusted source **"Official"** so it's used without verification — **not compatible with generative mode** `[WMG §2]`, `[BB B.2]`.

---

## 5. Wrong / failed / skipped tool-or-action call

**What the maker sees:** the agent doesn't call the tool it should, calls the wrong one, passes bad inputs, or the call errors out.

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| `ACTIONS` metadata weak | Generative orchestration builds its plan from each tool's **name, description, inputs, outputs**; ambiguous metadata → wrong/skipped tool. Selecting the wrong tool is a named failure mode. | Make name+description accurate and specific; disambiguate across all tools. ([faqs-generative-orchestration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-orchestration), [advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions)) |
| `ACTIONS` not agent-level / dynamic use off | A tool added only to a **topic** (or with "Allow agent to decide dynamically" **unchecked**) is only used when explicitly called — the planner won't pick it. | Add the tool at **agent level** and enable "Allow agent to decide dynamically when to use the tool." ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions)) |
| `ACTIONS` too many tools | Orchestrator handles **max 128 tools**, but Microsoft recommends **≤25–30** for quality; declarative injects only the **first 5 plugins**, then semantic-matches, and degrades past ~10 functions/plugin `[BB A.5]`. | Cut tool count; split into connected agents past ~30–40 choices `[BB B.7]`. |
| `ACTIONS` schema/auth defects | Declarative API plugins **don't support** nested objects, `oneOf/allOf/anyOf`, circular refs, API keys in headers/query/cookies, non-Authcode/PKCE OAuth, dual-auth. Studio tool calls fail with HTTP/auth error codes. | Flatten schema; use supported auth; read the error code (below). ([known-issues](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues)) |
| Missing inputs → over-eager or stalled call | Model calls a tool without required inputs, or loops asking. | Add "only call the tool if inputs are available, else ask" `[WMG §1]`; use conversation history to fill inputs `[WMG §3]`. |

**Copilot Studio error-code map for tool/action failures** ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes)):

| Code | Meaning | Fix |
|---|---|---|
| `HTTP400BadRequest` / `HTTP422` | Malformed / semantically invalid request | Validate params/types before the call; test with known-good data |
| `HTTP401` / `InvalidAuthenticationToken` / `MsalUiException` | Missing/expired/interactive-auth token | Reauthenticate; recreate connection |
| `HTTP403Forbidden` | Authenticated but lacks permission | Grant roles/consent; check delegation |
| `HTTP404NotFound` | Bad resource id/URL | Prefer dynamic resource selection over typed IDs |
| `HTTP429TooManyRequests` / `QuotaExceeded` | Throttling / quota exhausted | Backoff + retry; reduce call volume; upgrade quota |
| `HTTP5xx` / `ExecutionTimeout` / `OperationTimeout` / `HTTP408/504` | Service-side / timeout | Retry with backoff; narrow query; paginate |
| `FlowActionTimedOut` | Agent flow > **100 s** | Optimize flow; move post-result logic after "Return value(s) to Copilot Studio" |
| `FlowActionBadRequest` / `FlowActionException` / `BindingKeyNotFoundError` | Flow input/output mismatch | Only Text/Boolean/Number params supported; **remove & re-add the flow** to refresh bindings |
| `FlowMakerConnectionBlocked` | Flow uses maker credentials the admin blocked | Share flow with **run-only** permissions |
| `AsyncResponsePayloadTooLarge` / `TooMuchDataToHandle` | Tool/connector output too big for the model context | Scope output to needed fields; use connector filters |
| `ConnectedAgent*` | Sub-agent not found/not published/auth mismatch/**chaining unsupported** | Publish sub-agent; match auth; flatten (no multi-level chaining) |

**Surface-specific**
- **Declarative:** **Power Automate Flows as actions are not fully supported** — may not run or return results, and newly-created flows may not appear in Add Action; workaround is editing the flow's description outside Copilot Studio. Also an **unofficial/observed** limit: the orchestrator silently stops after the **3rd distinct API action** in a turn (community Q&A, not documented) `[BB A.5]`, ([known-issues](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues), [Q&A: silent stop after 3rd action](https://learn.microsoft.com/en-us/answers/questions/5652631/m365copilot-declarative-agent-orchestrator-silentl)). Because the declarative pipeline is **sequential and can't do chained/looped tool ops** `[BB A.6]`, multi-tool workflows are a surface-ceiling issue (§11).
- **Copilot Studio:** use the **activity map** in the test pane to see exactly which tool the planner selected and where it failed; error codes above are your evidence. ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions))

---

## 6. Generative-orchestration loops or stalls

**What the maker sees (Copilot Studio generative only):** the agent asks the same structured question repeatedly and never advances, or dialog execution terminates mid-task. A documented pattern: orchestration **repeats questions and ignores valid user responses.** ([Q&A: repeats questions/ignores responses](https://learn.microsoft.com/en-us/answers/questions/2258167/generative-ai-orchestration-repeats-questions-and))

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| Topic/flow doesn't reach a terminal node | `InfiniteLoopInBotContent`: "Action … was executed more than `{MaxTurnCount}` times in a row" → cycle detected, dialog terminated. | Ensure the topic **ends correctly** and links to topics that end correctly (e.g. **Escalate** system topic). ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes)) |
| Orchestration re-asks filled slots | Planner references **last 10 turns**; if the captured answer isn't bound to the expected input, it re-prompts. | Bind captured values to variables/inputs; make questions map cleanly to tool inputs; test the slot-fill path. ([faqs-generative-orchestration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-orchestration)) |
| Too many consecutive actions | Autonomous chains have a max-turn cap; long chains stall. Practitioner + docs guidance: keep to **<15 consecutive actions/topics** for reliability `[BB B.6]`. | Reduce chain length; split into connected agents; add decision boundaries/guardrails. ([generative-orchestration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration)) |
| Over-complex instructions | Dense/conflicting instructions confuse the planner. | **Bisect:** remove all instructions, add back individually, test between each. ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions)) |
| Rate-limit stall (not a loop) | `GenAIToolPlannerRateLimitReached` — "usage limit for generative orchestration reached." | Per-environment quota; retry, add capacity (see §10). ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes)) |

Classic-orchestration analog: error **2000** ("trapped in an infinite loop") and **2021** (">50 dialogs in a turn") / **2022** (">30 messages in a turn"). ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes))

**Surface-specific**
- **Declarative:** **cannot loop by design** — the fixed sequential pipeline has no iterative reasoning `[BB A.6]`. So "loops/stalls" as a symptom is essentially **Copilot Studio-generative-only**; on declarative the equivalent failure is a *silently truncated* multi-step attempt (§5), which is a signal to re-platform (§11).
- **Copilot Studio:** generative orchestration is **English-only** and less deterministic; where a guaranteed path is needed, author an explicit **topic** or use classic orchestration `[WMG §3]`, ([faqs-generative-orchestration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-orchestration)).

---

## 7. Moderation over-blocks / fallback fires too often

**What the maker sees:** "The content was filtered due to Responsible AI restrictions (ContentFiltered)" on benign input, or the default fallback message firing constantly.

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| moderation level too **High** | Default High; content is checked **twice** (user input + before response). Domain vocabulary (violence/medical/legal) trips filters. RAI checks **can't be disabled**, but the level is tunable within bounds. | Lower moderation at **agent or topic** level (topic overrides agent); state the expected behavior in instructions. ([troubleshoot RAI filter](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai), [knowledge-copilot-studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)) |
| `KNOWLEDGE` looks like an injection | Sources containing links/commands/instruction-like phrases trigger **`OpenAIndirectAttack`** (indirect prompt-injection / XPIA); high-risk with generative orchestration + email triggers (unmoderated content sent externally). | Clean knowledge of instruction-like text; if testing, ensure your instructions align with intended behavior so your own content isn't read as an attack. ([troubleshoot RAI filter](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai), [error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes)) |
| False-positive on first attempt | Known issue: the RAI filter may incorrectly flag valid input on the first try. | Make prompts more specific; add **condition nodes** to validate input format before the generative step. ([troubleshoot RAI filter](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai)) |
| `# GUARDRAILS` fallback misrouted | The **default fallback** ("I'm not sure how to help… try rephrasing") is triggered by unmatched intents, not editable via instructions. | Edit the **Fallback system topic** (not instructions) `[WMG §1,§3]`; tighten trigger phrases / add topics for the missed intents. |

The specific ContentFiltered sub-codes (all → "reinforce RAI guidelines / adjust moderation"): `OpenAIHate`, `OpenAIJailBreak`, `OpenAIndirectAttack`, `OpenAISelfHarm`, `OpenAISexual`, `OpenAIViolence`. ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes))

**Evidence capture:** connect **Azure Application Insights** and run KQL over RAI exceptions + conversation transcripts to find which message tripped the filter; blocked-query counts are also in the **Power Platform admin center** `[WMG §4]`, ([troubleshoot RAI filter](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai)).

**Surface-specific**
- **Declarative:** moderation is **not maker-configurable** — RAI is Copilot's, applied at publish and runtime `[WMG §4]`, `[BB A.1]`. Over-blocking here can only be mitigated via instruction wording (state expected behavior) and cleaning knowledge (XPIA sanitization applies to knowledge, which is why you must **never offload instructions into knowledge** `[BB A.2]`).
- **Copilot Studio:** moderation level and Fallback topic are both editable — this is where the real fix lives.

---

## 8. Tone / format / output-contract drift

**What the maker sees:** inconsistent verbosity, format changes between runs, repetitive verbatim phrasing, or behavior that shifted after a platform update.

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| `# GUARDRAILS` output contract missing | If tone/verbosity/format are unspecified, the model **infers** them → inconsistency across model versions. | Add an explicit **Output Contract** (goal, format, detail level, tone, include/exclude, example shape) `[WMG §1]`. |
| Model **auto-upgrade** drift (declarative) | Copilot periodically auto-upgrades the model; **GPT 5.0→5.1** shifted from literal following to intent-first reasoning, reordering/adding steps `[BB A.3]`, `[WMG §1]`. | Add a **literal-execution header** ("interpret instructions literally; don't infer intent or fill missing steps; don't call tools unless a step says so") as an interim stabilizer; re-test after each upgrade. |
| Repetitive/verbose output | Under-constrained generation. | Add concise constraints; vary phrasing with **few-shot** examples `[WMG §1]`. |
| Tasks not atomic | "Extract metrics and summarize" merged/reinterpreted. | Split into atomic steps (Goal/Action/Transition) `[WMG §1]`. |

**Surface-specific**
- **Declarative:** most exposed to **silent model auto-upgrades** (you don't choose the model) — drift is a recurring, version-dependent risk; the literal-execution header is the standard mitigation.
- **Copilot Studio:** you can **pin/choose the model** (e.g. Claude Sonnet 4.5/4.6, Opus, GPT variants) via prompt/model settings, which reduces surprise drift; changing citation-related wording can still cause responses to be discarded as ungrounded `[WMG §1]`, ([prompt-model-settings](https://learn.microsoft.com/en-us/microsoft-copilot-studio/prompt-model-settings)).

---

## 9. 8,000-character instruction truncation effects

**What the maker sees (declarative only):** later instructions seem ignored; the agent follows early rules but drops workflow steps/guardrails defined near the end.

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| Instruction body over the **8,000-char** hard limit | Declarative instructions are capped at 8,000 chars (hard) `[BB A.3]`, `[WMG §1]`. Content beyond it is lost; even near the limit, signal gets diluted. | **Specific beats long** `[WMG §1]`: cut redundancy, tighten to essentials, use Markdown headers/atomic steps; drop examples for simple cases to save budget. |
| Logic that belongs elsewhere crammed into instructions | Complex branching/business rules don't fit and don't execute reliably in a fixed pipeline anyway `[BB A.6]`. | **Re-platform to Copilot Studio** and move logic into **topics/flows/triggers** where the instruction budget is much larger and logic is deterministic `[BB C.1]` (see §11). |
| Instructions offloaded to knowledge to dodge the limit | **Anti-pattern.** Knowledge is untrusted, XPIA-sanitized, and **not honored as system instructions** — explicit Microsoft warning. | Never offload; keep governing instructions in the manifest `[BB A.2]`, `[WMG §1]`. |

**Surface-specific**
- **Declarative:** this symptom is essentially **declarative-only** and a hard ceiling `[BB A.3]`.
- **Copilot Studio:** free-text instructions are far larger and logic lives in topics/flows, so truncation is rarely the issue; over-long instructions instead cause **planner confusion** (§6) — fix by bisecting, not by trimming to a char count.

---

## 10. Latency or Copilot-Credit blowout

**What the maker sees:** slow responses, or "This agent is currently unavailable. It has reached its usage limit," or unexpectedly high credit consumption.

| Root cause (AgentSpec zone) | Why | Fix pattern |
|---|---|---|
| `ACTIONS` synchronous flow overhead | Off-agent calls are **synchronous** — nothing else happens until they return; Power Automate flows add considerable overhead. | Use the lighter **HTTP Request node** for simple single lookups; **cache** results in variables instead of repeated calls; set a **timeout** on externally-set global variables; send a "one moment" holding message. ([optimize-minimize-latency](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/optimize-minimize-latency)) |
| Metered features drive credit burn | Billing per action (Studio, since Sept 2025 Copilot Credits): Classic answer **1**, Generative answer **2**, Agent action **5**, Tenant graph grounding **10**, Agent flow **13/100 actions**, AI tools basic **1**/standard **15**/premium **100** per 10 responses; reasoning models add a token meter `[BB B.10]`. | Prefer cheaper capabilities where quality allows; avoid premium AI tools/reasoning models on hot paths; model spend with the **Agent usage estimator**. ([requirements-messages-management](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management), [agent-usage-estimator](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-usage-estimator)) |
| orchestration setting = generative everywhere | Generative planning costs more than classic per turn and adds a planner round-trip. | Use **classic** orchestration / explicit topics for high-volume deterministic paths `[WMG §3]`. |
| Overage / rate limits hit | Consumption > capacity → **overage; enforcement disables the agent at 125% of prepaid capacity**; per-environment generative AI + orchestration quotas throttle per minute/hour. | Add prepaid **capacity packs** or switch to **pay-as-you-go** (prod/sandbox only); request a rate-limit increase (PAYG envs only); reduce tool calls. ([throttling-errors-agents](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/licensing/throttling-errors-agents), [requirements-messages-management](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management)) |
| Event triggers over-fire | Each trigger payload is a **billed** message; frequent/recurrence triggers hit quota `[BB B.6]`. | Throttle trigger frequency; keep payloads small via variables. |

Relevant error codes: `EnforcementMessageC2` (not enough prepaid capacity), `GenAISearchandSummarizeRateLimitReached`, `GenAIToolPlannerRateLimitReached`, `OpenAIRateLimitReached`, `QuotaExceeded`. ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes))

**Surface-specific**
- **Declarative:** **no separate metering for most capabilities** — cost is the per-user M365 Copilot license `[BB C.1]`. Latency is bounded by the pipeline's **45 s timeout / 4,096 token / 50-record / 25-response** envelope `[BB A.6]`; blowout usually means the scenario is too heavy for declarative (§11), not a tuning problem.
- **Copilot Studio:** credits are the real exposure — **M365 Copilot-licensed users incur no charge** for core B2E usage, but unlicensed users and metered features (flows, premium tools, tenant-graph grounding, triggers) consume tenant credits `[BB B.10]`.

---

## 11. Surface mismatch (built declarative when it needed Copilot Studio)

**What the maker sees:** the agent hits a wall that no amount of instruction/knowledge tuning fixes — it can't loop, can't act autonomously, can't strictly ground, can't reach an external channel, or silently truncates multi-step work.

This is a **meta-symptom**: several of the above (§2 hallucination ceiling, §5 multi-tool truncation, §6 "can't loop," §9 truncation) are actually the declarative **surface ceiling** manifesting. The fix is not a field change — it's **re-platforming**.

| Trigger observed | Declarative limit hit | Re-platform because |
|---|---|---|
| Needs iterative/looped/multi-step orchestration | Sequential pipeline, no loops; "not suitable for complex multistep operations" `[BB A.6]` | Copilot Studio generative orchestration chains topics/tools/agents |
| Needs autonomous / event-triggered / proactive behavior | Declarative is **user-initiated only** `[BB A.6]` | Studio event triggers + generative orchestration `[BB B.6]` |
| Needs **strict grounding** (block general knowledge) | Agent Builder can't fully block model knowledge `[BB A.4]` | Studio **Allow ungrounded OFF** `[BB B.3]` |
| Needs deterministic automation | Only single-step API plugins | Studio **agent flows** (deterministic) `[BB B.4]` |
| Needs multi-agent / external channels / group use | Declarative is individual, M365 channels only `[BB A.6]` | Studio A2A/connected agents + web/WhatsApp/Slack/SMS/voice `[BB B.7,B.8]` |
| Instruction logic exceeds 8,000 chars | Hard cap `[BB A.3]` | Logic moves to topics/flows/triggers `[BB C.1]` |

**Diagnostic tell:** if the maker's evidence shows the agent doing *part* of a multi-step task then stopping, or inventing answers that only strict grounding would prevent, and the scenario matches any C.3 trigger `[BB C.3]` — the root cause is **surface**, and the change-set is "re-platform to Copilot Studio," not a `# SCOPE`/`KNOWLEDGE` edit. Copilot Studio is the superset surface and can even emit a declarative agent, so framing is "does the scenario need capabilities only the custom-engine runtime provides" `[BB C.4]`.

---

## 12. Cross-cutting diagnostic method (how to read each surface's own signals)

Feeds the map's "how to read the surfaces' own test/analytics signals" deliverable:

- **Declarative:** the generic runtime error **"Sorry, I wasn't able to respond."** almost always means a **silent grounding failure** (license/auth/permission) — check §3 first. There's **no error-code surface** and no maker-visible moderation; evidence is the pasted transcript + the known-issues list. ([known-issues](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues))
- **Copilot Studio:** rich, readable signals — (1) **error codes** in the test pane / topic checker (the §5–§10 tables map code→zone); (2) the **activity map** shows the plan, tool selection, and where a *content-filtered* block occurred; (3) **Azure Application Insights** (KQL over RAI exceptions/transcripts); (4) **Power Platform admin center** for blocked-query counts and credit consumption; (5) the **Evaluate tab** (test sets, LLM-judge "General quality") whose failing **category** localizes the layer — core=broken, robustness=too strict, architecture=tool/knowledge/routing bug, edge=weak guardrails `[WMG §5]`. ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes), [advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions))
- **Universal isolation test:** run the query **with and without** each source/tool/instruction block, and **bisect** instructions (remove all, add back one at a time) — the cheapest way to localize a root cause to one zone `[WMG §2]`, ([advanced-generative-actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions)).

---

## 13. Version-dependent / preview / ambiguous flags

- **Model auto-migration (declarative):** GPT 5.0→5.1 already changed instruction interpretation; expect ongoing drift on each auto-upgrade — the literal-execution header is a *moving-target mitigation*, not a permanent fix `[BB A.3]`.
- **Copilot Studio model choice:** Claude Sonnet 4.5/4.6 and Opus now GA for model selection — availability and defaults shift; verify per environment. ([prompt-model-settings](https://learn.microsoft.com/en-us/microsoft-copilot-studio/prompt-model-settings))
- **Unofficial/observed:** declarative orchestrator silently stopping after the **3rd distinct API action** (community Q&A only, not documented) `[BB A.5]`; treat as needs-confirmation. ([Q&A](https://learn.microsoft.com/en-us/answers/questions/5652631/m365copilot-declarative-agent-orchestrator-silentl))
- **"Allow ungrounded OFF" is not absolute:** it blocks ungrounded *turns* but does **not** guarantee zero general-knowledge blending, and it disables follow-up questions — a documented caveat, not a bug `[WMG §2]`.
- **Government tenants:** authenticated custom actions, usage-billing extensibility features, and Agents-Toolkit publishing are **unsupported in M365 Government** — a whole class of "action doesn't work" that is tenant-type, not config. ([known-issues](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues))
- **Generative orchestration is English-only** and the default for new agents; several classic-only features (Official-source marking, custom entities, disambiguation) are gapped `[BB B.2]`, ([faqs-generative-orchestration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-orchestration)).
- **Billing/enforcement** (Copilot Credits, 125% overage disable, per-env quotas) current as of Jun 2026 rate tables — re-verify before quoting specific rates `[BB B.10]`.
- **`FlowActionTimedOut` = 100 s**, `AIModelActionRequestTimeout` = 100 s, classic dialog cap = **50 topics/turn**, messages = **30/turn** — hard platform numbers as of the 2026-06-04 error-codes page. ([error-codes](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes))

---

## Key source URLs

**Microsoft Learn — troubleshooting / known issues (primary for this ticket):**
- Known Issues in M365 Copilot Extensibility — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/known-issues
- Understand Error Codes (Copilot Studio) — https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/authoring/error-codes
- Resolve responsible AI content filter errors — https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/generative-answers/agent-response-filtered-by-responsible-ai
- Resolve usage limit / agent unavailable errors — https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/licensing/throttling-errors-agents
- Optimize agents to minimize latency — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/optimize-minimize-latency
- FAQ for generative orchestration — https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-orchestration
- FAQ for generative answers — https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-answers

**Microsoft Learn — behavior/config (cross-referenced):**
- Orchestrate agent behavior with generative AI — https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions
- Knowledge sources summary (moderation, ungrounded) — https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- Add knowledge to a declarative agent — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge
- Write effective instructions for declarative agents — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions
- Billing rates and management — https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management
- Agent usage estimator — https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-usage-estimator
- Change the model version and settings — https://learn.microsoft.com/en-us/microsoft-copilot-studio/prompt-model-settings
- Apply generative orchestration capabilities — https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration

**Practitioner / community (corroborating symptoms):**
- Q&A: agent starts right then switches mid-response — https://learn.microsoft.com/en-us/answers/questions/5635444/copilot-studio-agent-why-does-it-start-with-the-ri
- Q&A: inconsistent/hallucinatory responses — https://learn.microsoft.com/en-us/answers/questions/5654951/inconsistent-and-hallucinatory-responses-from-copi
- Q&A: generative orchestration repeats questions / ignores responses — https://learn.microsoft.com/en-us/answers/questions/2258167/generative-ai-orchestration-repeats-questions-and
- Q&A: declarative orchestrator silently stops after 3rd API action — https://learn.microsoft.com/en-us/answers/questions/5652631/m365copilot-declarative-agent-orchestrator-silentl

**Prior knowledge base (extended here):**
- `../builder-agent/research/01-platform-building-blocks.md` (`[BB …]`)
- `../builder-agent/research/02-what-makes-agent-good.md` (`[WMG …]`)
