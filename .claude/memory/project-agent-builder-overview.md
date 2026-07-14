---
name: project-agent-builder-overview
description: What the Agent-Builder-Agent project is and where its wayfinder map + deliverables live
metadata:
  type: project
---

This repo builds a **Copilot Studio "builder agent"** that converses with a maker and hands them **ready-to-paste artifacts** to create their own **M365 declarative agent** or **Copilot Studio agent** (both surfaces, full depth). Destination = a build-ready spec + template library the user assembles inside Copilot Studio — planning + assets only, **no live-tenant provisioning** (that's explicitly out of scope).

The work is run as a **wayfinder effort** (mattpocock skills). Orient by reading the map first:
- Map: `.scratch/builder-agent/map.md`
- Tickets: `.scratch/builder-agent/issues/` · Research: `.scratch/builder-agent/research/`
- Deliverables: `.scratch/builder-agent/templates/` (base skeleton + `archetypes/library.md`) and `builder-spec/` (capstone)

Deliverable stack: (1) research KB on both surfaces + agent-quality principles; (2) two-layer template library — the [[project-agentspec-hybrid-decision]] base skeleton + 6 archetypes; (3) the builder agent's own spec (capstone, ticket 07 — closes the map).

Builder's end user = **mixed audience** (non-technical makers + technical builders; it detects skill level, offers quick vs. guided paths). Tracker = local markdown under `.scratch/` (no GitHub issues).
