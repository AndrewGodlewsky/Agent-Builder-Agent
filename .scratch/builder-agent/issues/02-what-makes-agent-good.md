# 02 · What makes an agent "good"

Type: research
Status: resolved
Blocked by: none

## Question

What are the principles and best practices that separate a good Microsoft agent from a mediocre one, and how do they map onto the two target surfaces?

Resolve, grounded in current Microsoft Learn guidance plus reputable practitioner sources:

- **Instruction writing**: structure of an effective instruction/system prompt (role, goal, scope, rules, tone, guardrails, refusal/fallback behavior); length and specificity trade-offs; Microsoft's own recommended patterns.
- **Knowledge grounding**: choosing and scoping knowledge sources, avoiding hallucination, citation behavior, freshness, and when to use knowledge vs. actions.
- **Conversation / topic design**: designing helpful flows, disambiguation, handoff, graceful failure; classic vs. generative orchestration guidance.
- **Guardrails & safety**: content moderation, staying in scope, handling out-of-scope requests, authentication-gated data.
- **Evaluation**: how authors test and measure agent quality (test conversations, analytics, iteration loops).

Extract the **invariant structure** — the elements every good agent shares — because that becomes the base skeleton (ticket 03).

Capture findings to `.scratch/builder-agent/research/02-what-makes-agent-good.md` with source links.

## Answer

- **Same discipline, different mechanics.** A good agent on both surfaces = clear role/goal, tight scope grounded only in configured tools/knowledge, explicit rules + tone + output format, guardrails, examples, and iterative evaluation. Surfaces differ in mechanics: M365 declarative has an **8,000-char** instruction limit and auto-upgraded model; Copilot Studio picks **classic vs. generative orchestration** and controls fallback/citations/moderation via system settings, not instructions.
- **Instructions:** Microsoft's own components are **Purpose → General guidelines (directions/tone/restrictions) → Skills**, plus conditional Steps, Error handling, Examples, Vocabulary, Follow-up. Rules: say what to DO not avoid; strict Markdown structure (sections/bullets/steps); atomic tasks; every step = **Goal/Action/Transition**; always specify tone+verbosity+format (Output Contract); few-shot for complex; add a self-check gate. Specificity beats length; never offload instructions into knowledge (XPIA risk).
- **Knowledge grounding:** relevance over quantity ("less is more"), scope tightly, keep fresh, honor per-user permissions. Reduce hallucination by testing with/without sources, using **Allow ungrounded responses = off** / Official sources, and never reshaping system citations. Knowledge = ground facts (RAG); Actions = do things (mark writes `isConsequential`).
- **Conversation/orchestration:** classic = predictable topic-based; generative (default) = LLM chains tools/knowledge, autonomous, context-aware follow-ups. Disambiguate with one question at a time; confirm before consequential steps; edit the **Fallback system topic** for graceful failure; route out-of-scope to humans.
- **Guardrails & safety:** in-scope-only instruction + refusal fallback; Copilot Studio content moderation **Lowest→Highest (default High)** at agent/topic/prompt level; per-user Entra auth for auth-gated data; constrain tool/parameter use against jailbreak/injection; RAI validation at publish.
- **Evaluation:** iterate create→test→refine; use built-in test chat on starters + edge/long/irrelevant prompts + across apps; structured test sets (≤100 cases, prompt+expected+acceptance+method, LLM "general quality" judge); four-stage lifecycle (foundational core → baseline+RCA → expand across robustness/architecture/edge → continuous ops); run multiple times, **target 80–90% pass**; adversarial "Always Fail" set for guardrails.

**Candidate base skeleton (invariant elements for ticket 03):** 1) Role/Persona · 2) Purpose/Objective · 3) Scope & grounding boundary · 4) Response rules/constraints · 5) Tone, verbosity & output format (Output Contract) · 6) Capability/knowledge/tool references · 7) Workflow steps (Goal→Action→Transition, conditional) · 8) Guardrails, safety & out-of-scope/refusal-fallback · 9) Domain vocabulary (conditional) · 10) Examples — valid+invalid (conditional) · 11) Self-evaluation gate (conditional) · 12) Conversation starters (agent-level, min 3) · 13) Error handling & follow-up/closing (conditional).

Full findings with citations: `.scratch/builder-agent/research/02-what-makes-agent-good.md`
