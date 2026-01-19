---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [context-folder]
description: SPICE iterate — spawn fresh subagent for each task until all complete
---

# SPICE Iterate

**Context folder**: $1

This command implements a **delegator pattern**: it reads the plan, then spawns a **fresh implementer subagent for each task**. Each task gets an isolated 200K context window.

---

## Process

### 1. Find the Plan

Read the most recent plan: `$1/plan-*.md`

### 2. Iteration Loop

**CRITICAL**: Use the Task tool to spawn a NEW subagent for EACH task. Do NOT implement tasks in the main context.

```
WHILE tasks with [ ] status exist in plan:

    1. Read plan, find next pending task
    
    2. If no pending tasks → STOP, report completion
    
    3. Extract the task's **Skills:** field
       Example: "**Skills**: spice/python, test-driven-development"
    
    4. **SPAWN `spice-implementer` AGENT** via Task tool:
    
       ```
       Task tool:
         agent: spice-implementer
         prompt: |
           Plan: $1/plan-001.md
           Task: {task number, e.g., 2.1}
           Context folder: $1
           
           **Skills to load** (from task's Skills field):
           - .claude/skills/spice/{language}.md
           - test-driven-development skill
           
           Execute TDD for this ONE task.
           Update progress in: $1/progress-001.md
           Mark task [x] complete in plan.
           
           Return: tests passing count, files modified, any issues.
       ```
    
    5. Wait for subagent to complete
    
    6. Report progress to user:
       "✅ Task 2.1 Complete: {title}"
    
    7. CONTINUE to next task (new subagent)
```

### 3. Completion

When all tasks show `[x]`:
1. Report summary of all changes
2. List files created/modified
3. Show final test count
4. Suggest next steps

---

## Why Fresh Subagent Per Task?

```
Orchestrator (main context)
     │
     ├──► Task tool ──► [Subagent: Task 1.1] ──► Done, returns
     │
     ├──► Task tool ──► [Subagent: Task 1.2] ──► Done, returns
     │
     ├──► Task tool ──► [Subagent: Task 2.1] ──► Done, returns
     │
     └──► ... continues until plan complete
```

Each subagent:
- **Fresh 200K context** — no accumulated bloat
- **Loads only its skills** — spice/python + TDD, not everything
- **Isolated failure** — if it fails, retry with clean slate
- **Focused work** — one task, one goal

---

## Progress Reporting

After each task completes:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Task 2.1 Complete: Implement email validation
   Skills: spice/python, test-driven-development
   Tests: 3 passed
   Files: src/validators/email.py, tests/test_email.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: 4/10 tasks complete
Next: Task 2.2 — Add validation error messages
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Handling Failures

If a subagent reports failure (tests don't pass):

1. **STOP iteration** — don't proceed to next task
2. Report the failure clearly
3. Suggest manual retry:
   ```
   /spice:execute $1/plan-001.md 2.1
   ```
4. Manual retry spawns a fresh subagent (clean slate)

---

## Examples

```bash
# Iterate through all remaining tasks
/spice:iterate /context/001-auth/

# After fixing a failure, continue
/spice:iterate /context/001-auth/
```

---

## Anti-Pattern: DON'T Do This

```
❌ WRONG: Implementing tasks in main context

for each task in plan:
    read task
    write tests      ← DON'T do this here
    write code       ← This pollutes main context
    run tests        ← Context grows with each task
```

```
✅ CORRECT: Spawn subagent for each task

for each task in plan:
    read task metadata (skills, files)
    USE TASK TOOL to spawn implementer
    wait for subagent completion
    report progress
```

The orchestrator (this command) should ONLY:
- Read plan metadata
- Spawn subagents via Task tool
- Report progress
- Handle failures

All actual implementation happens in subagents.
