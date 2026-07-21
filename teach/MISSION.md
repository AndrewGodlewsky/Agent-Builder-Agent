# Mission: Copilot Studio Knowledge Architecture & SharePoint RAG

## Why
I'm the builder of the Agent-Builder-Agent, an actively-in-development Copilot
Studio agent. I want to internalize the research in `../research/` so I can make
knowledge-configuration decisions — what goes in instructions vs. knowledge,
which source types to use, how to tune SharePoint retrieval — from mastery,
without re-reading the research docs every time.

## Success looks like
- I can instantly decide whether a given piece of content belongs in instructions or knowledge, and explain why.
- I can pick the right knowledge source type (and SharePoint RAG path) for a scenario and state the trade-offs.
- I can list the site-owner levers that actually improve SharePoint RAG quality — and the query types that are structurally impossible to fix.
- I can recall the load-bearing limits (file-size ceilings, top-3 grounding, source quotas) or know exactly where to look them up.
- I can spot the class of mistakes found in my own agent's build review before they ship.

## Constraints
- Self-paced solo learning in short sessions; each lesson must be completable quickly.
- Lessons are single-file interactive HTML in `./lessons/` (offline-friendly, Windows system fonts only, no external requests).
- Grounded in the repo's verified research; Copilot Studio moves fast, so limits must be re-verified against live Microsoft Learn docs before relying on them.

## Out of scope
- Copilot Studio topic/flow authoring and Power Platform administration beyond knowledge configuration.
- Declarative agents for Microsoft 365 (except where contrasted with Copilot Studio custom agents).
