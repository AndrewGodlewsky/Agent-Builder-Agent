# Knowledge Source Names & Descriptions (for Copilot Studio)

When you link each knowledge file to the Agent Builder in Copilot Studio, you set a **Name** and a **Description**. The Description is not just documentation — under **generative orchestration** the agent uses it to decide *which* knowledge source to search for a given turn. So each description below states **what the document contains** and **when the agent should consult it**, using the exact terms a build/improve/fix conversation would surface.

**How to use:** for each of the five knowledge sources, paste the **Name** into the name field and the **Description** into the description/relevance field (Knowledge → the source → Edit). Keep the names exact so they read cleanly in the agent's activity map. Works for either format (the raw `.md` in `Agent/knowledge/` or the SharePoint-ready `.docx` in `Agent/knowledge/docx/`).

---

## 1 · `01-agentspec-skeleton`

**Name:** `AgentSpec Skeleton and Question-to-Field Mapping`

**Description:**
The structure the agent fills when **building a new agent**. Defines the AgentSpec: a config envelope (name, description, surface, knowledge, capabilities, actions, conversation starters) plus a free-text Markdown instruction body with its standard sections (`# ROLE`, `# OBJECTIVE`, `# SCOPE & GROUNDING`, `# RESPONSE RULES`, `# OUTPUT FORMAT`, `# CAPABILITIES & KNOWLEDGE`, `# WORKFLOW`, `# GUARDRAILS`, and conditional sections). Includes the interview question-to-field mapping (which maker answer fills which field), which sections are core vs. optional, how each element maps to the M365 declarative vs. Copilot Studio surface, and a worked example. **Consult when:** deciding what to ask the maker, mapping their answers to spec fields, or structuring the instruction body of a new agent.

---

## 2 · `02-archetype-library`

**Name:** `Starter Agent Archetype Library`

**Description:**
Six ready-to-tailor starting templates for a **new agent**, each a complete AgentSpec with filled config and instructions. The archetypes: Knowledge Q&A Assistant (declarative), IT Helpdesk Agent (declarative + read action + workflow), Employee Onboarding Agent (Copilot Studio + write flows), Research/Analyst Assistant (declarative + web search + code interpreter), Autonomous Monitoring Agent (Copilot Studio + event trigger), and Compose-from-scratch (bare skeleton fallback). Includes a coverage grid of which surface and capabilities each targets. **Consult when:** proposing a starting point for a new agent — match the maker's goal to the nearest archetype and tailor it, or fall back to compose-from-scratch.

---

## 3 · `03-artifact-formats`

**Name:** `Output Artifact and Manifest Formats`

**Description:**
The exact, ready-to-paste output formats the agent emits, per surface. Covers the M365 declarative agent manifest **`declarativeAgent.json` (schema v1.7)** — root fields, character limits, and the full capabilities list (WebSearch, OneDriveAndSharePoint, GraphConnectors, Dataverse, CodeInterpreter, GraphicArt, etc.); the **`apiPlugin.json` (schema v2.4)** action/plugin manifest with runtimes, auth, and functions; the Microsoft 365 app package (`manifest.json`, icons) for sideloading; and Copilot Studio movement (solution export/import, `pac copilot` CLI, paste-able topic YAML) plus the click-by-click config for knowledge/actions that don't import. Includes minimal and fuller JSON examples. **Consult when:** emitting build artifacts, writing a manifest, or checking an exact schema field, limit, or version.

---

## 4 · `04-platforms-and-quality`

**Name:** `Platform Comparison, Surface Rule, and Agent Quality`

**Description:**
Two references in one. First, the platform building blocks and the **surface-choice delta rule** — M365 declarative agent vs. Copilot Studio agent: capabilities, hard limits (8,000-char instructions, grounding/token/timeout ceilings), knowledge-source limits, orchestration modes, channels, autonomy, multi-agent, and Copilot Credits licensing — with the rule for when a scenario forces Copilot Studio vs. stays declarative. Second, agent-quality best practices: writing effective instructions, knowledge grounding ("less is more," strict grounding), guardrails and content moderation, and evaluation. **Consult when:** deriving which surface an agent should use, advising on a platform limit or license, or applying instruction/knowledge/guardrail/quality best practices.

---

## 5 · `05-diagnostics`

**Name:** `Diagnostics for Improving and Fixing Agents`

**Description:**
The reference for **improve/fix mode** — diagnosing and improving an already-built agent. Covers the failure taxonomy (symptom → likely layer → root cause → fix); per-surface evidence capture (M365 Developer Mode `-developer on` card; Copilot Studio activity map, rationale, snapshot, transcripts); the **entitlement pre-check** for silent license/permission gaps; the **five-layer isolation method** (Moderation → Action → Orchestration → Grounding → Instructions, Instructions diagnosed last); the Copilot Studio error-code decoder; improvement levers with an evaluation loop; and surface-flip escalation when an agent hits the declarative ceiling. **Consult when:** the maker reports something wrong or wants an existing agent improved — to isolate the failing layer, decode an error, or propose one evidence-backed change.

---

## Notes on writing good descriptions (why these are shaped this way)

- **Lead with content, end with a "consult when" trigger.** Generative orchestration matches the user's turn against the description, so naming the situations that should call the source (build vs. improve/fix, "writing a manifest," "deciding the surface," "decode an error") improves routing.
- **Use exact product/format terms** (`declarativeAgent.json`, v1.7, "five-layer," "Copilot Credits") — they're the words that match real queries.
- **Keep each source distinct.** Overlapping descriptions make the orchestrator pick the wrong source; the five above are deliberately scoped to build-structure (01), starting templates (02), output formats (03), platform/quality (04), and diagnostics (05).
