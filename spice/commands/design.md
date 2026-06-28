---
allowed-tools: Task, Read, Glob, AskUserQuestion
argument-hint: "[prd-path] [research-path]"
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

4. **Handle question forwarding**:
   - If response contains `AWAITING_INPUT: true`:
     - Extract questions from "Questions Before Proceeding" section
     - Use `AskUserQuestion` tool to get answers from user
     - Re-invoke agent with original prompt + "Previous questions answered:" section
     - Repeat until agent completes without `AWAITING_INPUT`

5. **Review any remaining assumptions** — Designer may still have minor assumptions in TDD
6. After confirmation, suggest: `/spice:plan {folder}/prd-001.md {folder}/tdd-001.md`

## Question Forwarding Loop

```
while response contains "AWAITING_INPUT: true":
    questions = extract_questions(response)
    answers = AskUserQuestion(questions)
    response = Task(agent: spice-designer, prompt: original + answers)
```

## When to Use

**Create TDD for**: APIs, database changes, system integration, technical decisions
**Skip TDD for**: Simple bug fixes, UI-only changes, configuration

## Examples

```bash
/spice:design /context/001-auth/prd-001.md /context/001-auth/research-001.md
```
