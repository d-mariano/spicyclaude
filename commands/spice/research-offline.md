---
allowed-tools: Task, Read, Glob, AskUserQuestion
argument-hint: [prd-path]
description: SPICE research — explore codebase only (NO web search)
---

# SPICE Research (Offline)

**PRD**: $1

## Process

1. Derive context folder from PRD path
2. Spawn `spice-researcher-offline` agent:

```
Task tool:
  agent: spice-researcher-offline
  prompt: |
    Mode: Offline
    PRD: $1
    Output: {folder}/research-001.md
```

3. After completion, suggest: `/spice:design {folder}/prd-001.md {folder}/research-001.md`

## When to Use

- Air-gapped environments
- Already know the tech stack
- Pure codebase refactoring
- Sensitive/restricted network

## Examples

```bash
/spice:research-offline /context/001-auth/prd-001.md
```
