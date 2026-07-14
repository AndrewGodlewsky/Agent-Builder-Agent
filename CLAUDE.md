## Keeping the README Current

Whenever a unit of work is completed, evaluate whether it changes anything the
`README.md` should reflect — the project's purpose, structure, setup/usage
steps, available agents or deliverables, features, dependencies, or workflow.

**Decision:**
- If the completed work does **not** change what the README documents, do
  nothing and continue.
- If it **does**, the README is now stale and must be brought back in sync.

**When an update is needed, delegate it to a sub agent** (via the Agent tool)
rather than editing the README inline. Dispatch a sub agent whose task is to:
1. Read the current `README.md` and review what just changed.
2. Update `README.md` so it accurately reflects the current state of the
   project — add, revise, or remove sections as needed.
3. Keep the existing tone and structure; make the smallest set of edits that
   makes the README correct and complete.
4. Report back what was changed (or that no change was warranted after closer
   inspection).

The goal: the README should always reflect the current state of the project
after any completed work.

## Repo Memory

Claude stores project knowledge in `.claude/memory/` (committed to git).
At the start of every session, read `.claude/memory/MEMORY.md` to load context.
Use `/repo-memory` to save or retrieve memories.

### Recalling Information

Before answering questions about project decisions, conventions, or context,
check `.claude/memory/` first — read `MEMORY.md` for the index, then open
relevant files. This is the team's shared knowledge base.

### When to Save

| What | Type |
|------|------|
| Architectural decisions and their rationale | `project` |
| Team conventions, what to avoid or repeat | `feedback` |
| Links to external systems, dashboards, docs | `reference` |
| Personal preferences (add user_*.md to .gitignore if private) | `user` |
| Chosen libraries/frameworks and why alternatives were rejected | `project` |
| Things that were tried and didn't work (anti-patterns for this codebase) | `feedback` |
| Preferred naming conventions, code style, and formatting rules | `feedback` |
| Things that Claude got wrong multiple times and required correction | `feedback` |
| External API docs, service dashboards, internal wikis | `reference` |
| Environment setup notes (non-obvious deps, quirks, build steps) | `reference` |
| Domain knowledge the user has that I shouldn't re-explain | `user` |

### What NOT to Save
- Code patterns readable from the codebase
- Git history (git log / git blame are authoritative)
- Ephemeral task state or in-progress work
- Anything already in this CLAUDE.md
