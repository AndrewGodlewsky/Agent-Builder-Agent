# 04 · Improvement / optimization levers

Type: research
Status: resolved
Blocked by: none

## Question

For agents that already **work** but could be **better**, catalog the optimization levers the "improve" (goal-first) framing pulls on.

Resolve, grounded in current (2026) Microsoft Learn documentation + reputable practitioner sources:

- The **quality eval loop**: how Microsoft recommends iterating an agent to a good pass rate (the ~80–90% target from v1 research 02 §5), building a small test set, measuring, and tightening.
- **Grounding precision**: narrowing/curating knowledge sources, scoped web search, strict grounding ("Allow ungrounded responses" off), reducing wrong-source retrieval.
- **Instruction / output tuning**: tightening `# SCOPE` / `# RESPONSE RULES` / `# OUTPUT FORMAT`, tone and verbosity control, staying under the 8,000-char declarative limit while improving.
- **Cost / latency / Copilot-Credit optimization**: what drives credit consumption (classic 1 / generative 2 / action 5 / tenant-graph 10 from v1 research 01), how to reduce it, latency levers, when a cheaper surface/orchestration suffices.
- Frame each lever as: **goal the maker states → lever → the AgentSpec change it implies**, so it plugs into the same change-set output as troubleshooting.

Capture findings to `.scratch/builder-agent-v2/research/04-improvement-levers.md` with source links.

## Answer

Findings: [`../research/04-improvement-levers.md`](../research/04-improvement-levers.md). Grounded in current (Feb–Jul 2026) Microsoft Learn; credit rates verified live.

- **A real "improve" framework now exists (new since v1).** Microsoft shipped **evaluation-driven triage & remediation** guidance (`evaluation-triage-*`, ms.date 2026-03-30) — 4 layers (interpret scores → triage failure → map to remediation → analyze patterns) — and moved eval methodology to a cross-product Agents hub (`/agents/agent-evaluation/`). The governing contract is **`change X → rerun Y → expect Z`**: no lever is applied without a test proving it moved the number. The builder's improve-mode should adopt this spine.
- **Quality eval loop:** build a **small test set** (1 prompt per key scenario, incl. refuse/route + adversarial safety cases) → baseline pass rate → expand across **Foundational core / Robustness / Architecture / Edge-case** categories → rerun ×N and average, **target 80–90 %**. Hard readiness gates: **safety/compliance <95 % = Block**, **core business <80 % = Iterate**. With **>15 fails, fix by shared root cause**, not one-by-one. Category-of-failure tells you which lever: core=broke, robustness=too strict, architecture=component bug, edge=weak guardrails.
- **Grounding precision:** curate/narrow the corpus ("less is more"; >25 sources get GPT-filtered so **descriptions are the lever**); align **source vocabulary to how users ask**; strict grounding via **Allow ungrounded responses = OFF** + "answer only from sources" (Copilot Studio only — **Agent Builder can't hard-block**; two caveats: OFF doesn't guarantee zero general knowledge and it **blocks context-only follow-ups**); scope/disable **Web Search**; **tenant-graph semantic search** boosts SharePoint precision but costs **10 credits/msg + latency**; **Official-source** marking is **classic-orchestration only**.
- **Instruction/output tuning:** always specify **tone + verbosity + Output Contract** (`# OUTPUT FORMAT`); fix named failure modes — over-eager tool use → gate in `# RESPONSE RULES`; verbose → length calibration; inconsistent tone → consolidate into one block. Steer **reasoning depth via phrasing** (minimal-reasoning cuts latency/cost).
- **The 8,000-char "instruction budget" problem (key 2026 insight):** remediation *adds* rules until the prompt overloads and regresses working areas — the fix is **Consolidate / Prioritize (first+last) / Simplify / Externalize to knowledge / test the full suite**, never offload instructions into a knowledge doc (XPIA-unsafe, not honored). Model auto-upgrades (GPT 5.0→5.1) can regress a working agent → literal-execution header + the **Pattern 9 audit prompt** as an off-the-shelf improve engine.
- **Cost/latency/credits (verified live, ms.date 2026-06-11, unchanged from v1):** classic **1** / generative **2** / agent action **5** / tenant-graph **10** / agent-flow **13 per 100** / AI-tools **1·15·100 per 10** / content-processing **8/page**; reasoning models bill **feature-rate + premium token meter**; overage disables agents at **125 %** of prepaid. Levers: keep B2E users **M365-Copilot-licensed** (free path), **downgrade answer type** (5× spread classic→action), avoid tenant-graph/reasoning-by-default, move fixed sequences to **agent flows**, set **per-agent monthly caps** in PPAC, forecast with the **usage estimator**.
- **Cheaper surface/orchestration suffices when** the job is single-intent Q&A over a fixed corpus → **classic orchestration** (predictable, cost-effective) or **Agent Builder** (generative answers free in-M365). Escalate to full Copilot Studio only when a hard capability forces it; a surface *downgrade* is itself a cost lever (flag the metering flip — the "map fog" edge case).
- Delivered a **10-row change-set catalog** (goal → lever → AgentSpec zone → verify) that plugs directly into ticket 06's diagnose→revise flow and ticket 07's `05-diagnostics.md` knowledge file.
