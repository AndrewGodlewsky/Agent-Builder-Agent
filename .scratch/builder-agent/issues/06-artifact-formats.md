# 06 · Ready-to-paste artifact & manifest formats

Type: research
Status: resolved
Blocked by: none

## Question

What are the authoritative, current formats for the artifacts the builder must emit so a maker can paste/import them with minimal work?

Resolve, grounded in current Microsoft Learn / schema documentation:

- **M365 declarative agent manifest**: the `declarativeAgent.json` schema — required/optional fields, instructions, `conversation_starters`, `capabilities` (web search, code interpreter, etc.), knowledge (SharePoint/OneDrive, Graph connectors, web), actions (API plugin manifests / `apiPlugin.json`), and how it packages (Teams app manifest, Copilot agent packaging). Give a valid minimal example and a fuller example.
- **Copilot Studio**: what can actually be exported/imported (solution / YAML topic format / agent export), and what parts must be configured by hand in the maker portal (so the builder emits precise click-by-click config where no import format exists).
- **Knowledge & action config**: the exact fields a maker needs for each knowledge-source type and connector/action.

Goal: a definitive "what the builder emits, per surface, in what format" reference. Capture findings to `.scratch/builder-agent/research/06-artifact-formats.md` with source links and example payloads.

## Answer

- **M365 declarative agent = fully file-based, cleanest paste/import path.** Builder emits a `.zip` app package: `manifest.json` (Teams/M365 app manifest, `manifestVersion` ≥ 1.13) → `declarativeAgent.json` (schema **v1.7**, latest as of Jul 2026) → optional `apiPlugin.json` (plugin manifest **v2.4**) → OpenAPI spec + Adaptive Cards + `color.png` (192×192) + `outline.png` (32×32). The app manifest links the DA via the `copilotAgents.declarativeAgents[]` node.
- **DA manifest v1.7** requires `version`/`name`/`description`/`instructions`; capabilities cover `WebSearch`, `OneDriveAndSharePoint`, `GraphConnectors`, `GraphicArt`, `CodeInterpreter`, `Dataverse`, `TeamsMessages`, `Email`, `People`, `Meetings`, `ScenarioModels`, `EmbeddedKnowledge`. Knowledge is declared inline (URLs/IDs) with no portal step. Minimal + fuller examples in findings.
- **API plugin v2.4** adds MCP (`RemoteMCPServer`) support; auth is `None`/`OAuthPluginVault`/`ApiKeyPluginVault` with a `reference_id` (no secrets in the manifest); plugins are only usable as DA actions, not standalone.
- **Copilot Studio is the surface with NO clean full-fidelity import.** Definition moves via an **unmanaged Dataverse solution `.zip`** or a **`pac copilot` YAML workspace** (`.mcs.yml`), and individual **topics paste as YAML** into the code editor — but **connections, connection references, knowledge-source authentication, env-variable current values, generative-AI settings, channels, and the icon do NOT transfer** and must be reconfigured by hand.
- **Managed solutions can't be exported** (keep an unmanaged source); topic names with periods block export; custom connectors must be imported before the agent solution.
- **Knowledge/action config fields** documented per source type: DA manifest (web sites, SPO IDs/URLs, connector IDs, Dataverse host/skill/tables, email mailboxes/folders) and Copilot Studio portal (SharePoint URL + name + description + Entra scopes `Sites.Read.All`/`Files.Read.All`; limits: 500 knowledge objects, ~5 active sources, ≤10 lists).
- Where no import format exists, the builder should emit precise click-by-click maker-portal steps (§4–5 of findings).

Full findings with schemas, citations, and example JSON/YAML payloads: `.scratch/builder-agent/research/06-artifact-formats.md`
