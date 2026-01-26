---
allowed-tools: Task, Read, Glob, AskUserQuestion
argument-hint: [prd-path]
description: SPICE research — explore codebase and gather context (web search enabled)
---

# SPICE Research

**PRD**: $1

## Process

1. Derive context folder from PRD path
2. Spawn `spice-researcher` agent:

```
Task tool:
  agent: spice-researcher
  prompt: |
    Mode: Online
    PRD: $1
    Output: {folder}/research-001.md
```

3. After completion, suggest: `/spice:design {folder}/prd-001.md {folder}/research-001.md`

## Online vs Offline

| Online (`/spice:research`) | Offline (`/spice:research-offline`) |
|---------------------------|-------------------------------------|
| Web search enabled | Codebase only |
| Framework docs, APIs | Air-gapped environments |

## Examples

```bash
/spice:research /context/001-auth/prd-001.md
/spice:research /context/002-payments/prd-001.md
```
