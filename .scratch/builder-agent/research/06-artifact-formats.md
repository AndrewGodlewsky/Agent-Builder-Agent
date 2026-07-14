# 06 · Ready-to-paste artifact & manifest formats — Findings

Research date: 2026-07-14. All schema facts grounded in current Microsoft Learn docs (dated May–Jul 2026 revisions). Source URLs inline and in the Sources section.

## TL;DR — what the builder emits, per surface

| Surface | Clean import format? | What the builder emits |
| --- | --- | --- |
| **M365 declarative agent** (Copilot Chat / Teams / Office) | **YES** — file-based | A `.zip` **app package**: `manifest.json` (Teams/M365 app manifest) + `declarativeAgent.json` (schema **v1.7**) + optional `apiPlugin.json` (plugin manifest **v2.4**) + OpenAPI spec + `color.png` (192×192) + `outline.png` (32×32). Sideload/upload directly. |
| **M365 API plugin / action** | **YES** — file-based | `apiPlugin.json` (v2.4) + an OpenAPI 3.0 description (or MCP tool list). Referenced from the DA manifest `actions[]`. |
| **Copilot Studio agent** (Power Platform) | **PARTIAL** — Dataverse solution `.zip` OR `pac copilot` YAML workspace | A **solution .zip** (unmanaged) containing the agent + its `botcomponent` YAML, OR a `pac copilot` file workspace (`.mcs.yml` files) packable to a solution. **Connections, knowledge-source auth, and generative settings do NOT travel** and must be reconfigured by hand. |
| **Copilot Studio individual topic** | **YES (paste)** — YAML snippet | A single-topic **YAML** block (`kind: AdaptiveDialog …`) pasted into the topic **code editor**. |
| **Knowledge sources & connections (either surface)** | **NO clean import for runtime binding** | The builder emits **precise click-by-click config** (URLs, IDs, scopes, descriptions). See §5. |

**Bottom line on "no clean import path":** **Copilot Studio runtime wiring** is the weak spot. The agent definition and topics move via solution/YAML, but **connections (connection references), knowledge-source authentication, custom-connector secrets, environment-variable current values, generative-AI orchestration settings, channel config, and the agent icon do not import** — the builder must emit step-by-step maker-portal instructions for those. The M365 declarative-agent path, by contrast, is fully file-based and paste/sideload-ready.

---

## 1. M365 Declarative Agent manifest (`declarativeAgent.json`) — schema v1.7

Latest version is **v1.7** (Learn page `ms.date: 2026-05-14`). No v1.8 exists as of Jul 2026. v1.7 added `editorial_answers`, `behavior_overrides.default_response_mode`, and `conversation_starters[].depends_on`.

- Schema URL (put in `$schema`): `https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.7/schema.json`
- Reference: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-manifest-1.7

### Root object — required vs optional

| Property | Req? | Notes / limits |
| --- | --- | --- |
| `version` | **Required** | Set to `"v1.7"`. |
| `name` | **Required** | Localizable. ≤ 100 chars, ≥ 1 non-whitespace. |
| `description` | **Required** | Localizable. ≤ 1,000 chars. |
| `instructions` | **Required** | ≤ 8,000 chars. The system prompt / behavior guidance. |
| `id` | Optional | Manifest identifier. |
| `capabilities` | Optional | Array; at most one of each derived type (see §1.1). |
| `conversation_starters` | Optional | ≤ 12 objects; `text` required, `title` + `depends_on` optional. |
| `actions` | Optional | 1–10 objects referencing/ inlining plugin manifests (§2). |
| `behavior_overrides` | Optional | `suggestions.disabled`, `special_instructions.discourage_model_knowledge`, `default_response_mode` (`Auto`\|`Quick response`\|`Think deeper`). |
| `disclaimer` | Optional | `text` ≤ 500 chars, shown at conversation start. |
| `sensitivity_label` | Optional | `{ "id": "<purview-guid>" }`. Only applies with embedded files (not yet enabled). |
| `editorial_answers` | Optional | Predefined Q&A pairs (`url` OR `answers[]`, ≤ 300), semantic-similarity matched. |
| `worker_agents` | Optional (preview) | Reference other DAs by `id` or `file`. |
| `user_overrides` | Optional | JSONPath toggles that let end users remove a capability in-session. |

Default string cap for unspecified properties is **4,000 chars**. Unrecognized properties invalidate the whole document. Localizable strings can use `[[key_name]]` localization keys.

### 1.1 Capabilities (knowledge + skills baked into the manifest)

Base type = capabilities object; each entry keyed by `name`. Available types:

| `name` | Purpose | Key sub-fields |
| --- | --- | --- |
| `WebSearch` | Ground on the web | `sites[]` (≤ 4), each `{ "url": "https://…" }` — max 2 path segments, no query string. Omit `sites` = search all web. |
| `OneDriveAndSharePoint` | SPO/OneDrive grounding | `items_by_url[]` (`{url}`) and/or `items_by_sharepoint_ids[]` (`site_id`,`web_id`,`list_id`,`unique_id`,`search_associated_sites`,`part_type`,`part_id`). Omit both = all SPO/OneDrive. |
| `GraphConnectors` | Copilot connectors | `connections[]` each `{ "connection_id": "…" }` (+ optional `additional_search_terms` KQL, `items_by_*` filters). Omit = all connectors. |
| `GraphicArt` | Image generation | `name` only. |
| `CodeInterpreter` | Python execution / data analysis / charts | `name` only. |
| `Dataverse` | Query Dataverse tables | `knowledge_sources[]`: `host_name`, `skill`, `tables[].table_name`. `skill` is obtained by publishing a Dataverse-knowledge agent in Copilot Studio and reading the downloaded `declarativeAgent.json`. |
| `TeamsMessages` | Teams chat/channel search | `urls[]` (≤ 5) each `{url}`. Omit = all Teams messages. |
| `Email` | Mailbox search | `shared_mailbox` (SMTP), `group_mailboxes[]` (≤ 25 SMTP), `folders[].folder_id`. |
| `People` | Org people info | `include_related_content` (bool). |
| `Meetings` | Meeting info | `items_by_id[]` (≤ 5): `{ id, is_series }`. |
| `ScenarioModels` | Task-specific models | `models[].id`. |
| `EmbeddedKnowledge` | Local files in package (**not yet available**) | `files[].file` (≤ 10, ≤ 1 MB each; docx/pptx/xlsx/txt/pdf). |

Note: capabilities beyond `WebSearch` require a Copilot license or metered-usage tenant.

### 1.2 MINIMAL valid declarativeAgent.json

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.7/schema.json",
  "version": "v1.7",
  "name": "Repairs agent",
  "description": "Helps track tickets and repairs.",
  "instructions": "You look at ServiceNow and Jira tickets to help the user keep track of open items."
}
```

### 1.3 FULLER declarativeAgent.json (capabilities + actions + starters + overrides)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.7/schema.json",
  "version": "v1.7",
  "name": "Northwind Support Agent",
  "description": "Answers product and policy questions grounded in SharePoint, the web, and the Northwind API.",
  "instructions": "You are a support expert. Prefer grounded answers from the provided knowledge. Use the listRepairs and createRepair actions when the user asks about repair tickets. Do not invent policy.",
  "conversation_starters": [
    { "title": "Getting Started", "text": "How do I open a support ticket?" },
    {
      "title": "Latest policy",
      "text": "What is the current return policy?",
      "depends_on": [ { "name": "capabilities", "id": "WebSearch" } ]
    }
  ],
  "capabilities": [
    { "name": "WebSearch", "sites": [ { "url": "https://contoso.com/support" } ] },
    { "name": "OneDriveAndSharePoint",
      "items_by_url": [ { "url": "https://contoso.sharepoint.com/sites/ProductSupport" } ] },
    { "name": "GraphConnectors", "connections": [ { "connection_id": "jiraTickets" } ] },
    { "name": "CodeInterpreter" },
    { "name": "GraphicArt" }
  ],
  "actions": [
    { "id": "repairsPlugin", "file": "repairs-api-plugin.json" }
  ],
  "behavior_overrides": {
    "suggestions": { "disabled": false },
    "special_instructions": { "discourage_model_knowledge": true },
    "default_response_mode": "Auto"
  },
  "disclaimer": { "text": "AI-generated. Verify policy details before acting." },
  "user_overrides": [
    { "path": "$.capabilities[?(@.name == 'WebSearch')]", "allowed_actions": [ "remove" ] }
  ]
}
```

---

## 2. API plugin manifest (`apiPlugin.json`) — schema v2.4

Latest is **v2.4** (Learn `ms.date: 2026-07-01`). v2.4 added **MCP server** support (`RemoteMCPServer` runtime) and file-referenced Adaptive Card templates.

- Schema URL: `https://developer.microsoft.com/json-schemas/copilot/plugin/v2.4/schema.json`
- Reference: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-manifest-2.4
- Important constraint: **API plugins are only supported as actions inside declarative agents**, not standalone in M365 Copilot.

### Root object

| Property | Req? | Notes |
| --- | --- | --- |
| `schema_version` | **Required** | `"v2.4"`. |
| `name_for_human` | **Required** | ≤ 20 chars used. Localizable. |
| `namespace` | **Required** | Regex `^[A-Za-z0-9]+`; prevents function-name collisions. |
| `description_for_human` | **Required** | ≤ 100 chars used. |
| `description_for_model` | Optional | ≤ 2048 chars; guidance for the LLM on when to use it. |
| `functions[]` | Optional | If omitted + an OpenAPI runtime present, functions are inferred from operations. |
| `runtimes[]` | Optional | How functions are invoked (OpenApi / LocalPlugin / RemoteMCPServer). |
| `capabilities.conversation_starters[]` | Optional | Plugin-level starters. |
| `logo_url`, `contact_email`, `legal_info_url`, `privacy_policy_url` | Optional | Metadata. |

### Runtimes & auth

- `runtimes[].type`: `OpenApi` \| `LocalPlugin` \| `RemoteMCPServer`.
- `auth.type`: **`None`** \| **`OAuthPluginVault`** \| **`ApiKeyPluginVault`**. For the vault types, set `reference_id` (a token obtained separately) — **no secrets are stored in the manifest**.
- OpenApi spec: `spec.url` (GET-fetched) OR inline `spec.api_description`; optional `progress_style`.
- MCP spec: `spec.url` + `mcp_tool_description.file` or inline `mcp_tool_description.tools[]` (name/description/inputSchema matching `tools/list`).
- LocalPlugin spec: `local_endpoint: "Microsoft.Office.Addin"`, optional `allowed_host[]`.

### Function object highlights

`name` (must match OpenAPI `operationId` when bound), `description`, `parameters` (JSON-schema subset: type/properties/required, param types string/array/boolean/integer/number, `enum`, `default`), `returns`, `states` (`reasoning`/`responding`/`disengaging` with `description`/`instructions`/`examples`), and `capabilities`:
- `confirmation` (`type` None\|AdaptiveCard, `title`, `body`, `isNonConsequential`)
- `response_semantics` (`data_path` JSONPath, `properties.title/subtitle/url/thumbnail_url/...`, `static_template` inline Adaptive Card **or** `{ "file": "./cards/x.json" }`)
- `security_info.data_handling[]` (`GetPublicData`,`GetPrivateData`,`DataTransform`,`DataExport`,`ResourceStateUpdate`)

### MINIMAL apiPlugin.json (OpenAPI-backed, no auth)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/plugin/v2.4/schema.json",
  "schema_version": "v2.4",
  "name_for_human": "Repairs API",
  "namespace": "repairs",
  "description_for_human": "Search and create repair tickets.",
  "description_for_model": "Use to list repair tickets by assignee/state and to create new repairs.",
  "runtimes": [
    {
      "type": "OpenApi",
      "auth": { "type": "None" },
      "spec": { "url": "https://api.contoso.com/repairs/openapi.yaml" }
    }
  ]
}
```

### FULLER apiPlugin.json (explicit functions, OAuth, Adaptive Card, MCP)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/plugin/v2.4/schema.json",
  "schema_version": "v2.4",
  "name_for_human": "Contoso Real Estate",
  "namespace": "realestate",
  "description_for_human": "Find real estate listings for sale.",
  "description_for_model": "Use whenever the user asks about properties for sale by city, bedrooms, or amenities.",
  "functions": [
    {
      "name": "getListings",
      "description": "Get properties matching criteria",
      "parameters": {
        "type": "object",
        "properties": {
          "city": { "type": "string", "description": "City to search" },
          "bedrooms": { "type": "number", "description": "Bedroom count" }
        },
        "required": [ "city" ]
      },
      "returns": { "type": "string", "description": "A list of properties" },
      "capabilities": {
        "confirmation": { "type": "AdaptiveCard", "title": "Search", "body": "Search now?", "isNonConsequential": true },
        "response_semantics": {
          "data_path": "$.properties",
          "properties": { "title": "$.address", "subtitle": "$.price", "url": "$.listingUrl" },
          "static_template": { "file": "./adaptivecards/property-card.json" }
        },
        "security_info": { "data_handling": [ "GetPublicData" ] }
      }
    }
  ],
  "runtimes": [
    {
      "type": "OpenApi",
      "auth": { "type": "OAuthPluginVault", "reference_id": "0123456-abcdef" },
      "run_for_functions": [ "getListings" ],
      "spec": { "url": "https://api.contoso.com/openapi.yaml" }
    }
  ]
}
```

---

## 3. Packaging: the M365 app package (`.zip`) + app manifest (`manifest.json`)

Reference: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-are-apps

"Agents are apps." A declarative agent ships as a **Microsoft 365 / Teams app package** — a `.zip` containing:

- **`manifest.json`** — the Teams/M365 app manifest (schema **≥ 1.13**; examples use `1.18`/`1.19`). Required fields: `manifestVersion`, `version` (semver), `id` (GUID), `developer` (name/websiteUrl/privacyUrl/termsOfUseUrl), `name` (short/full), `description` (short/full), `icons` (color/outline), `accentColor`.
- **`color.png`** — 192×192, symbol within central 120×120, solid or transparent square background.
- **`outline.png`** — 32×32, white-on-transparent (unused by Copilot but required to pass validation).
- **`declarativeAgent.json`** (§1) and any **`apiPlugin.json`** (§2) + OpenAPI/Adaptive-Card files + localization files.

The app manifest references the DA via the **`copilotAgents`** node:

```json
{
  "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.19/MicrosoftTeams.schema.json",
  "manifestVersion": "1.19",
  "version": "1.0.0",
  "id": "00000000-0000-0000-0000-000000000000",
  "developer": {
    "name": "Northwind Traders",
    "websiteUrl": "https://www.example.com",
    "privacyUrl": "https://www.example.com/privacy",
    "termsOfUseUrl": "https://www.example.com/termsofuse"
  },
  "name": { "short": "Northwind Support", "full": "Northwind Support Agent" },
  "description": { "short": "Support agent", "full": "Answers product & policy questions." },
  "icons": { "color": "color.png", "outline": "outline.png" },
  "accentColor": "#3690E9",
  "copilotAgents": {
    "declarativeAgents": [
      { "id": "agent1", "file": "declarativeAgent.json" }
    ]
  }
}
```

Chain of references: **app manifest → `copilotAgents.declarativeAgents[].file` → DA manifest → `actions[].file` → API plugin manifest → `runtimes[].spec.url` → OpenAPI**.

Notes:
- **Only one declarative agent per app manifest** currently.
- When built in Copilot Studio, the app manifest + `id` are generated automatically. With the **Microsoft 365 Agents Toolkit** (`aka.ms/M365AgentsToolkit`) or hand-authoring, the builder assigns the `id`.
- Distribution: sideload/upload the `.zip` to the tenant (org catalog) or submit to Partner Center for AppSource.

**Builder emits for this surface:** the complete `.zip` (or the set of files ready to zip): `manifest.json`, `declarativeAgent.json`, `apiPlugin.json` (if any), OpenAPI spec, Adaptive Card JSON(s), `color.png`, `outline.png`. This is the cleanest paste/import path of all surfaces.

---

## 4. Copilot Studio — what exports/imports vs. what is hand-config

Copilot Studio agents live in **Dataverse** as `botcomponent` records; every part (topics, tools, triggers, settings) is stored as **YAML**. There are three movement mechanisms:

### 4.1 Solution export/import (agent-level)
Reference: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export

- Add the agent (and dependencies via **Add required objects**) to an **unmanaged** solution → **Export solution** → produces `SolutionName_1_0_0_1_(un)managed.zip`.
- Import into another environment → then **reconfigure by hand**.

**Included:** agent instructions (main prompt), topics/components explicitly added to the solution, environment variables/flows/custom connectors when added as required objects.

**NOT included / does NOT transfer (must be redone by hand):**
- **Connections and connection references** (bind after import; custom connectors must be imported *first*, then the connection reference with the agent solution).
- **Knowledge sources** stored as separate resources/Dataverse tables may not travel.
- **End-user authentication** — must be reconfigured after import (explicit step in docs).
- Bot properties: **Conversation ID, CDS Bot ID, Environment ID**, topic/node-level comments.
- **Agent icon** and **channel details** come across empty; publish is required before sharing; icon can take up to 24 h to propagate.
- Generative-AI orchestration/settings and channel config generally need re-verification.

**Hard limitations:**
- **Managed solutions can't be exported** (must keep an unmanaged source solution).
- Can't export a solution whose agent has a topic name containing a period (`.`).
- Don't edit/remove agent components directly in the solution — breaks export/import.

### 4.2 `pac copilot` CLI — file workspace + solution packaging
Reference: https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/copilot

Keeps an agent as **files on disk** (`.mcs.yml` botcomponent YAML) synced to Dataverse. Key commands the builder can script/instruct:
- `pac copilot init --name … --publisher-prefix …` — scaffold a workspace (add `--environment` to also pack+import+connect in one step). `--authoring-mode cli-copilot` for CLI-authored agents; `--instructions` seeds the system prompt.
- `pac copilot clone --bot <id|schemaName> --environment <guid>` — download an existing agent + sync metadata.
- `pac copilot pull` / `push` — three-way-merge sync (push uploads knowledge files, cloud flows, connection references; stops on conflict).
- `pac copilot pack --publisher-prefix … --project-dir …` — package workspace into a **solution `.zip`** (local, no auth) → deploy with `pac solution import`.
- `pac copilot extract-template --bot … --templateFileName x.yaml` then `pac copilot create --templateFileName x.yaml --displayName … --schemaName … --solution …` — template-based agent creation.
- `pac copilot publish`, `pac copilot list`, `pac copilot status`, `pac copilot extract-translation`/`merge-translation` (resx/json localization).

This is the closest thing to a "source format" for Copilot Studio, but it still requires an authenticated Dataverse environment and post-import connection/knowledge wiring.

### 4.3 Topic YAML (paste-able) — the one clean paste path in Copilot Studio
Reference: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor

A single topic can be authored as **YAML** and pasted into the topic **code editor** (⋯ More → Open code editor). Component collections and topics can also be imported/exported. Example (a conversational-boosting/generative-answers topic):

```yaml
kind: AdaptiveDialog
beginDialog:
  kind: OnUnknownIntent
  id: main
  priority: -1
  actions:
    - kind: SearchAndSummarizeContent
      id: search-content
      userInput: =System.Activity.Text
      variable: Topic.Answer
      moderationLevel: Medium
      additionalInstructions: Include emojis to make responses more fun.
      publicDataSource:
        sites:
          - "www.chessusa.com/"
          - "www.chess.com/"
          - "www.lichess.org/"
      sharePointSearchDataSource: {}
    - kind: ConditionGroup
      id: has-answer-conditions
      conditions:
        - id: has-answer
          condition: =!IsBlank(Topic.Answer)
          actions:
            - kind: EndDialog
              id: end-topic
              clearTopicQueue: true
```

Key node kinds: `AdaptiveDialog` (topic root), `OnUnknownIntent`/`OnRecognizedIntent` (triggers), `SearchAndSummarizeContent` (generative answers, with `publicDataSource.sites[]` and `sharePointSearchDataSource`), `ConditionGroup`, `SendActivity`/`Message`, `Question`, `EndDialog`. VS Code extension uses `.mcs.yml` with IntelliSense/validation.

**Builder emits for Copilot Studio:** (a) an unmanaged **solution `.zip`** or a **`pac copilot` YAML workspace** as the transportable definition, PLUS (b) paste-able **topic YAML** snippets, PLUS (c) **explicit click-by-click config** for everything that doesn't import (connections, knowledge auth, generative settings, channels, icon) — see §5.

---

## 5. Knowledge & action config — exact fields the maker needs

Because runtime bindings rarely import cleanly (especially in Copilot Studio), the builder should emit these as precise instructions.

### 5.1 Declarative agent (manifest — fully declarable, no portal step)
- **Web:** `WebSearch.sites[].url` (≤ 4; ≤ 2 path segments; no query string).
- **SharePoint/OneDrive:** either `items_by_url[].url` OR `items_by_sharepoint_ids[]` (`site_id`,`web_id`,`list_id`,`unique_id`). IDs retrieved per "Retrieving capabilities IDs" doc.
- **Copilot/Graph connectors:** `GraphConnectors.connections[].connection_id` (+ optional KQL `additional_search_terms`, `items_by_external_id/url/path/container_*`).
- **Dataverse:** `host_name`, `skill`, `tables[].table_name`.
- **Email:** `shared_mailbox`, `group_mailboxes[]`, `folders[].folder_id`.
- **Teams/Meetings/People/ScenarioModels:** URLs / meeting IDs+`is_series` / `include_related_content` / model `id`.
- **Actions:** each action = `{ id, file }` → plugin manifest; plugin binds via `runtimes[].spec.url` (OpenAPI) or MCP `spec.url`; auth via `auth.type` + `reference_id` (vault).

### 5.2 Copilot Studio SharePoint knowledge source (portal — hand config)
Reference: https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint
Add knowledge → **SharePoint**, then supply:
- **SharePoint URL** (searches the URL and all subpaths; multiple URLs separated with Shift+Enter; supports variable URLs `https://site/{var}`). For **lists**: Browse items or paste list URL, up to 10 lists.
- **Name** + **Description** (detailed description matters — drives generative orchestration routing).
- **Authentication:** default **"Authenticate with Microsoft"**. For manual auth, an Entra ID app registration is required with scopes **`Sites.Read.All`** and **`Files.Read.All`** added next to `openid`/`profile`. Restricted SharePoint Search blocks it; guests unsupported in SSO apps.
- Optional **Advanced settings** filters (Title/Author/Modified by/Modified on with operators).

### 5.3 Copilot Studio limits & other sources
- **Max 500 knowledge objects** per agent; **only ~5 sources usable at a time**; SharePoint lists ≤ 10, lists > 35,000 rows degrade quality/latency.
- **Public website:** URL (Bing-indexed), name, description, depth limits apply.
- **Dataverse files/tables:** require **Dataverse search enabled** in the environment (admin action). Files are stored in Dataverse and auto-indexed into vector embeddings.
- **Uploaded files:** device/OneDrive/SharePoint upload, stored + indexed in Dataverse.

### 5.4 Copilot Studio actions/connectors (portal — hand config)
- **Custom connectors:** import connector solution **first**, then the agent solution + connection reference; supply secrets/connection in the target environment (never travel in export).
- **Connection references + environment-variable current values:** set per target environment after import.
- **End-user authentication:** reconfigure post-import (Entra ID / Entra ID V2 with secret/cert/federated cred; Generic OAuth not supported for SharePoint generative answers).

---

## Sources

- Declarative agent schema v1.7: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-manifest-1.7
- Plugin (API plugin) manifest schema v2.4: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-manifest-2.4
- M365 app model / packaging ("agents are apps"): https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agents-are-apps
- M365 app manifest reference: https://learn.microsoft.com/en-us/microsoft-365/extensibility/schema
- Copilot Studio export/import via solutions: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export
- Copilot Studio topic code editor (YAML): https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor
- `pac copilot` CLI reference: https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/copilot
- Add SharePoint as a knowledge source: https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint
- Knowledge sources summary: https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
