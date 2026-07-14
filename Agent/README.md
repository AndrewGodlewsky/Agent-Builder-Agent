# Agent Builder — ready to assemble

This folder is a **self-contained package**: everything you need to create the **Agent Builder** in Microsoft Copilot Studio is here, in paste-ready form. Work top to bottom.

The Agent Builder is a Copilot Studio agent that interviews a person and hands them ready-to-paste artifacts to create their own Microsoft 365 declarative agent or Copilot Studio agent.

## Files in this folder

```
Agent/
├─ README.md                     ← you are here (the build guide)
├─ 00-agent-settings.md          Name, description, settings, starters, knowledge list
├─ 01-instructions.md            The instruction body to paste into the agent
└─ knowledge/                    The 4 files to upload as the agent's knowledge
   ├─ 01-agentspec-skeleton.md   The AgentSpec structure + question→field mapping
   ├─ 02-archetype-library.md    6 starter archetypes
   ├─ 03-artifact-formats.md     Exact output formats per surface
   └─ 04-platforms-and-quality.md Platform delta rule + agent-quality best practices
```

## Prerequisites

- Access to **Microsoft Copilot Studio** (a Copilot Studio license and an environment you can create agents in).
- Permission to add knowledge sources (file upload, or a SharePoint library you can point to).

## Build it — step by step

1. **Create the agent.** In Copilot Studio, choose **Create → New agent** (skip/close the conversational setup, go to **Configure/Edit**). Set the **Name** and **Description** from [`00-agent-settings.md`](00-agent-settings.md).

2. **Set orchestration.** Open **Settings → Generative AI**. Set **Orchestration = Generative**, **Allow ungrounded responses = ON**, **Content moderation = High**. *(These matter: the builder runs a multi-step interview and drafts text, which needs generative orchestration.)*

3. **Paste the instructions.** Open the **Instructions** field on the Overview page and paste the entire body from [`01-instructions.md`](01-instructions.md) (everything below its divider line).

4. **Add the knowledge.** Go to **Knowledge → Add knowledge → Upload files** and upload all four files from [`knowledge/`](knowledge/). *(Alternatively, drop them in a SharePoint document library and add that library as the knowledge source.)*

5. **Add conversation starters.** On the Overview page, add the three suggested prompts listed in [`00-agent-settings.md`](00-agent-settings.md).

6. **Edit the Fallback topic.** Under **Topics → System → Fallback**, change the message so off-topic asks restate what the builder does (suggested wording in the settings file).

7. **Test.** Open the **Test** pane and try:
   - each conversation starter,
   - a vague goal ("make me an AI helper"),
   - an out-of-scope ask ("write me a poem"),
   - one simple case ("answer HR questions from our policy docs" → should end in a `declarativeAgent.json`),
   - one advanced case ("onboard new employees by running our provisioning flow" → should end in Copilot Studio portal steps).

   Confirm it asks one question at a time, derives the surface, and emits the right artifact. Iterate on the instructions until it behaves (~80–90% of test runs good).

8. **Publish.** Use **Publish**, then add the channel(s) you want (Teams, web, etc.).

## What "done" looks like

A published *Agent Builder* that a colleague can open and, in a short guided chat, walk away with either:
- a **`declarativeAgent.json`** (plus an `apiPlugin.json` if their agent has actions) and a publish checklist, or
- a set of **click-by-click Copilot Studio steps**,

for the agent they described — without needing to know the difference between the two platforms.

## Notes

- **Why no tools/flows?** The builder writes its output straight into the chat as code blocks / numbered steps, so it needs no connectors. (A future enhancement could add a flow to hand back a downloadable file.)
- **Keeping knowledge current.** These platforms change; when Microsoft updates the manifest schema or platform limits, refresh `knowledge/03-artifact-formats.md` and `knowledge/04-platforms-and-quality.md` and re-upload.
- **Where this came from.** The full research, templates, and decision history behind this package live in `../.scratch/builder-agent/` and the repo `../README.md`.
