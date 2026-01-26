---
allowed-tools: Task, Read, Write, Glob, AskUserQuestion
argument-hint: [prd-path] [research-path]
description: SPICE design — create Technical Design Document
---

# SPICE Design

**PRD**: $1
**Research**: $2

## Process

1. Verify both files exist
2. Derive context folder from PRD path
3. Spawn `spice-designer` agent:

```
Task tool:
  agent: spice-designer
  prompt: |
    PRD: $1
    Research: $2
    Output: {folder}/tdd-001.md
```

4. **Review assumptions** — Designer will present decisions requiring confirmation
5. After confirmation, suggest: `/spice:plan {folder}/prd-001.md {folder}/tdd-001.md`

## When to Use

**Create TDD for**: APIs, database changes, system integration, technical decisions
**Skip TDD for**: Simple bug fixes, UI-only changes, configuration

## Examples

```bash
/spice:design /context/001-auth/prd-001.md /context/001-auth/research-001.md
```
