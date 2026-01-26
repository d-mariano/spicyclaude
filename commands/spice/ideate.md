---
allowed-tools: Task, Read, Write, Glob, AskUserQuestion
argument-hint: [idea-or-topic]
description: SPICE ideate — generate PRD from an idea
---

# SPICE Ideate

**Idea**: $1

## Process

1. Create context folder: `/context/{nnn}-{sanitized-name}/`
2. Spawn `spice-ideator` agent:

```
Task tool:
  agent: spice-ideator
  prompt: |
    Context folder: {folder}
    Idea: $1
    Output: {folder}/prd-001.md
```

3. After completion, suggest: `/spice:research {folder}/prd-001.md`

## Examples

```bash
/spice:ideate "notification system for user events"
/spice:ideate "Users should be able to export their data as CSV"
```
