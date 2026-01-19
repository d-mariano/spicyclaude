---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [plan-path] [task-number?]
description: SPICE execute — spawn isolated subagent to implement a single task with TDD
---

# SPICE Execute

**Plan**: $1
**Task**: $2 (optional — defaults to next pending)

This command spawns an **isolated subagent** for the task. Each task gets a fresh 200K context window.

---

## Process

### 1. Read Plan and Find Task

Read the plan at $1 to find:
- The target task (specified $2 or next pending `[ ]`)
- The **Skills:** field for that task
- The files involved

### 2. Extract Skills

Parse the task's skills field:
```markdown
### Task 2.1: Implement validation
**Skills**: spice/languages/python, test-driven-development
```

Extract: `spice/languages/python`, `test-driven-development`

**Fallback** if no Skills field: detect from file extensions in **Files:** field.

### 3. Spawn Implementer Subagent

**Use the Task tool** to spawn the `spice-implementer` agent:

```
Task tool:
  agent: spice-implementer
  prompt: |
    Plan: $1
    Task to implement: {task number, e.g., "2.1"}
    Context folder: {derived from plan path}
    
    **Skills to load for this task:**
    - {skills from task's Skills field}
    - test-driven-development (ALWAYS)
    
    Read these skill files:
    - .claude/skills/spice/languages/{language}.md
    - .claude/skills/test-driven-development/SKILL.md
    
    Execute TDD protocol:
    1. RED: Write tests, verify they FAIL
    2. GREEN: Minimal code, verify tests PASS
    3. REFACTOR: Clean up while green
    
    After completion:
    1. Mark task [x] complete in plan
    2. Update progress file
    3. Commit if parent task complete
    
    Return: tests passing, files modified, any issues.
```

### 4. Report Results

After subagent completes:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Task 2.1 Complete: Implement email validation
   Skills: spice/languages/python, test-driven-development
   Tests: 3 passing
   Files: src/validators/email.py, tests/test_email.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next: Task 2.2 — Add validation error messages
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Why Fresh Subagent Per Task?

```
Task 1.1 ──► [Fresh 200K context] ──► Done
Task 1.2 ──► [Fresh 200K context] ──► Done  
Task 2.1 ──► [Fresh 200K context] ──► Done
```

Benefits:
- No accumulated context from previous tasks
- Each task loads only the skills it needs
- Failed tasks don't pollute subsequent attempts
- Clean retry on failure

---

## Handling Failures

If the subagent reports failure (tests don't pass):

1. Review the error in progress file
2. Retry with fresh context:
   ```bash
   /spice:execute $1 {task-number}
   ```
3. If still failing, break task into smaller pieces

---

## Examples

```bash
# Execute next pending task
/spice:execute /context/001-auth/plan-001.md

# Execute specific task
/spice:execute /context/001-auth/plan-001.md 2.1

# Retry a failed task (fresh context)
/spice:execute /context/001-auth/plan-001.md 2.1
```
