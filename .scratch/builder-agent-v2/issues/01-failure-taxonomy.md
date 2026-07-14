# 01 · Failure-mode taxonomy + fix patterns

Type: research
Status: resolved
Blocked by: none

## Question

Build the catalog of common ways already-built **M365 declarative agents** and **Copilot Studio agents** misbehave, each mapped to its **AgentSpec root cause** and a **fix pattern**. This is the core of the diagnostic knowledge base.

Resolve, grounded in current (2026) Microsoft Learn documentation + reputable practitioner sources:

- The recurring **symptoms** makers report: refuses valid queries / over-declines; hallucinates or answers ungrounded; ignores or under-uses a knowledge source; retrieves the wrong knowledge; wrong / failed / skipped tool-or-action call; orchestration loops or stalls (Copilot Studio generative); moderation over-blocks or fallback fires too often; tone / format / output-contract drift; instruction-length (8,000-char) truncation effects; latency or Copilot-Credit blowout; surface mismatch (built declarative when it needed Copilot Studio).
- For **each symptom**: the likely **root cause(s)** expressed in **AgentSpec terms** (which field/zone — `# SCOPE`, `# GROUNDING`, `KNOWLEDGE`, `ACTIONS`, `# GUARDRAILS`, orchestration setting, moderation level) and a concrete **fix pattern**.
- Note **surface-specific** causes (declarative fixed-orchestrator limits vs. Copilot Studio generative-orchestration / topic / flow causes).
- Cross-reference the existing knowledge base (`../builder-agent/research/01-platform-building-blocks.md`, `02-what-makes-agent-good.md`) so this extends rather than repeats it.

Capture findings to `.scratch/builder-agent-v2/research/01-failure-taxonomy.md` as a **symptom → root cause → fix** table/catalog with source links; flag anything version-dependent or ambiguous.

## Answer

Full catalog: [`../research/01-failure-taxonomy.md`](../research/01-failure-taxonomy.md) — an 11-symptom **symptom → root-cause (AgentSpec zone) → fix** catalog with a master quick-reference table, per-symptom tables, a Copilot Studio error-code→zone map, a cross-cutting diagnostic-method section, and version/preview flags. Grounded in the current (2026-06) Copilot Studio **error-codes** page, the M365 extensibility **known-issues** page, RAI/latency/throttling/generative-orchestration docs, and corroborating Microsoft Q&A. Key findings:

- **The same symptom often has a different root layer per surface** — that split is the catalog's core value. Declarative failures are usually **instruction/knowledge/licensing** (no maker-visible error codes, no configurable moderation, fixed sequential pipeline); Copilot Studio failures are usually **settings/orchestration/metadata** and expose readable **error codes** + an **activity map** as evidence.
- **Silent grounding failure is the #1 declarative "ignores knowledge" cause:** SharePoint/OneDrive grounding needs an **active Copilot license**, **User auth** (no service principals), and **≥Read** permission — any gap returns the generic *"Sorry, I wasn't able to respond."* with no error. (Also: null chars in a SharePoint filename → no results.)
- **Hallucination / over-decline are two sides of the grounding posture:** Copilot Studio's **Allow ungrounded responses** toggle is the pivot (OFF blocks ungrounded turns *and* disables follow-ups → over-declines; ON permits general-knowledge blending → hallucination). **Agent Builder can't fully block model knowledge**, so strict grounding is a reason to re-platform.
- **Tool/action failures decode via the error-code table:** a `HTTP4xx/5xx`, `Flow*`, `ConnectedAgent*`, `TooMuchDataToHandle`, `ExecutionTimeout` code maps directly to a fix; wrong/skipped tool is almost always **weak name/description metadata** or a tool not added at **agent level** with "decide dynamically." Declarative caveats: **flows-as-actions not fully supported**, first-5-plugin injection, and an observed silent stop after the **3rd distinct API action**.
- **Loops/stalls are Copilot-Studio-generative-only** (`InfiniteLoopInBotContent` / max-turn cycle, or slots re-asked because captured values aren't bound); declarative **can't loop by design**, so its equivalent is silent multi-step truncation — a re-platform signal.
- **Moderation over-block** = default **High** level + knowledge that reads like injection (`OpenAIndirectAttack`) + first-attempt false positives; fix by lowering the level, cleaning knowledge, adding input-validation condition nodes, and editing the **Fallback system topic** (not instructions). RAI is **not maker-configurable on declarative**.
- **Tone/format drift** is driven by a missing **output contract** plus **silent model auto-upgrades** (GPT 5.0→5.1) on declarative; mitigate with an explicit contract + literal-execution header. **8,000-char truncation** is declarative-only — trim, move logic to Studio topics/flows, **never offload instructions into knowledge** (XPIA).
- **Latency/credit blowout:** synchronous flow overhead (use the **HTTP node** + variable caching), metered features (agent actions=5, tenant-graph grounding=10, premium AI tools=100/10, flows=13/100 credits), and **125% overage disables the agent**; model spend with the **Agent usage estimator**. Declarative has no per-capability metering (cost = the per-user license) but a hard 45s/4,096-token/50-record envelope.
- **Surface mismatch is a meta-symptom:** several ceilings (no loops, no autonomy, no strict grounding, 8k limit, multi-tool truncation) are the declarative surface showing through — the correct change-set is "re-platform to Copilot Studio," not a field edit.
