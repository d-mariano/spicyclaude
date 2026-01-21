---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [idea-or-topic]
description: SPICE ideate — spawn isolated subagent to generate a PRD from an idea
---

# SPICE Ideate

**Idea**: $1

This command spawns an **isolated subagent** to generate a PRD through interactive conversation.

---

## Process

### 1. Setup Context Folder

Determine or create the context folder:
- If a folder like `/context/NNN-*` exists for this feature, use it
- Otherwise, create: `/context/{next-number}-{sanitized-idea-name}/`

Example: `/context/001-user-auth/`

### 2. Spawn Ideator Subagent

**Use the Task tool** to spawn the `spice-ideator` agent:

```
Task tool:
  agent: spice-ideator
  prompt: |
    Context folder: {context_folder}
    Idea: $1
    
    Execute the ideator protocol.
    
    1. Ask clarifying questions using AskUserQuestion
    2. Generate a PRD based on responses
    3. Write to: {context_folder}/prd-001.md
    4. Present PRD and ask for feedback
    5. Iterate if needed
```

### 3. Review Output

After subagent completes:
- Summarize the PRD created
- Suggest next step: `/spice:research`

---

## Next Step

After PRD approval:
```bash
/spice:research "{topic}" {context_folder}/
```

---

## Examples

```bash
# From an idea
/spice:ideate "notification system for user events"

# From a feature description
/spice:ideate "Users should be able to export their data as CSV"

# More detailed
/spice:ideate "Real-time collaboration on documents, like Google Docs"
```
