---
allowed-tools: Task, Read, Glob, AskUserQuestion
argument-hint: [prd-path] [tdd-or-research-path]
description: SPICE plan — create TDD task breakdown
---

# SPICE Plan

**PRD**: $1
**Technical Input**: $2 (TDD preferred, or research)

## Process

1. Verify both files exist
2. Derive context folder from PRD path
3. Spawn `spice-planner` agent:

```
Task tool:
  agent: spice-planner
  prompt: |
    PRD: $1
    Technical Input: $2
    Output: {folder}/plan-001.md
```

4. **Handle question forwarding** (if needed):
   - If response contains `AWAITING_INPUT: true`:
     - Extract questions from "Questions Before Proceeding" section
     - Use `AskUserQuestion` tool to get answers from user
     - Re-invoke agent with original prompt + "Previous questions answered:" section

5. After completion, suggest: `/spice:iterate {folder}/`

## With TDD vs Without

| With TDD | Without (research only) |
|----------|------------------------|
| Tasks from architecture | Tasks from requirements |
| Tests from API contracts | Tests from functional specs |
| More precise breakdown | More exploration needed |

## Examples

```bash
/spice:plan /context/001-auth/prd-001.md /context/001-auth/tdd-001.md
/spice:plan /context/002-ui/prd-001.md /context/002-ui/research-001.md
```
