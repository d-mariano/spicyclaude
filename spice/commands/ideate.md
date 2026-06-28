---
allowed-tools: Task, Read, Write, Glob, AskUserQuestion
argument-hint: "[idea-or-topic]"
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

3. **Handle question forwarding**:
   - If response contains `AWAITING_INPUT: true`:
     - Extract questions from "Questions Before Proceeding" section
     - Use `AskUserQuestion` tool to get answers from user
     - Re-invoke agent with original prompt + "Previous questions answered:" section
     - Repeat until agent completes without `AWAITING_INPUT`
   
4. After completion, suggest: `/spice:research {folder}/prd-001.md`

## Question Forwarding Loop

```
while response contains "AWAITING_INPUT: true":
    questions = extract_questions(response)
    answers = AskUserQuestion(questions)
    response = Task(agent: spice-ideator, prompt: original + answers)
```

## Examples

```bash
/spice:ideate "notification system for user events"
/spice:ideate "Users should be able to export their data as CSV"
```
