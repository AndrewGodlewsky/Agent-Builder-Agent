# Agent Builder — Settings

The exact values to enter when creating the agent in Copilot Studio. (Copy fields as-is.)

## Basic details

| Field | Value |
|---|---|
| **Name** | `Agent Builder` |
| **Description** | `Talks you through designing an M365 or Copilot Studio agent and hands you ready-to-paste artifacts.` |
| **Instructions** | Paste from [`01-instructions.md`](01-instructions.md) |

## Orchestration & behavior settings

| Setting | Value | Where |
|---|---|---|
| **Orchestration** | **Generative** | Settings → Generative AI |
| **Allow ungrounded responses** | **ON** | Settings → Generative AI (the builder reasons and drafts text, not just retrieves) |
| **Content moderation** | **High** (default) | Settings → Generative AI |

## Conversation starters

Add these three (Overview page → Suggested prompts / conversation starters):

| Title | Prompt text |
|---|---|
| Build an agent | `Help me build an agent.` |
| From my docs | `I want an agent that answers questions from my documents.` |
| Not sure | `I'm not sure what kind of agent I need — can you help?` |

## Knowledge sources

Upload the four files from the [`knowledge/`](knowledge/) folder (Knowledge → Add → Upload file), or place them in a SharePoint library and point the agent at it:

| Upload this file | The agent uses it for |
|---|---|
| `knowledge/01-agentspec-skeleton.md` | The **AgentSpec** structure + the question-to-field mapping |
| `knowledge/02-archetype-library.md` | The **6 archetypes** to propose and tailor |
| `knowledge/03-artifact-formats.md` | The exact **output formats** (declarativeAgent.json v1.7, apiPlugin.json v2.4, Copilot Studio portal steps) |
| `knowledge/04-platforms-and-quality.md` | The **surface delta rule** + agent-quality best practices |

## Fallback

Edit the **Fallback** system topic so off-topic requests restate what the builder does (e.g. "I help you design Microsoft 365 and Copilot Studio agents — what would you like to build?").

## Tools / actions

**None required.** The Agent Builder produces its output (a `declarativeAgent.json` code block, or click-by-click portal steps) directly in the conversation — it needs no connectors or flows to do its job.
