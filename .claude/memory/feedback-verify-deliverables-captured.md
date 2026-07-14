---
name: feedback-verify-deliverables-captured
description: Verify research/rationale is actually written to the right folder before moving on; backfill gaps
metadata:
  type: feedback
---

When producing research or design rationale, don't assume it landed — **verify it's captured in the correct deliverable/research folder and backfill anything missing** before moving to the next ticket.

**Why:** important reasoning produced mid-conversation (e.g. the AgentSpec hybrid-vs-alternatives analysis) is easy to leave only in chat and lose; the `research/` and `templates/` files are the durable record the builder agent will later consume.

**How to apply:** after a decision that rests on analysis, confirm that analysis exists in the files (a quick subagent completeness-check is welcome) and add it to the most relevant file if absent. Label design rationale as such, distinct from web-sourced findings. The user explicitly requested this on 2026-07-14 (subagent confirmed the skeleton-form trade-off was missing from `research/` and appended it as §7).
