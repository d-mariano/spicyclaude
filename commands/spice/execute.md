---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [plan-path] [task(s)?]
description: SPICE execute — spawn isolated subagent to implement task(s) with TDD
---

# SPICE Execute

**Plan**: $1
**Task(s)**: $2 (optional — parent task, subtask, or comma-separated batch)

This command spawns an **isolated subagent** for the task(s).

---

## Task Specification

| Format | Behavior |
|--------|----------|
| `1.0` | Parent task — execute ALL subtasks (1.1, 1.2, 1.3) |
| `1.1` | Single subtask |
| `1.1,1.2,1.3` | Batch of specific subtasks |
| (omitted) | Next pending parent task |

---

## Process

### 1. Read Plan and Find Task(s)

Read the plan at $1 to find:
- The target task(s) (specified $2 or next pending parent task)
- The **Skills:** field for the task(s)
- All subtasks if it's a parent task

### 2. Determine Scope

| Input | Scope |
|-------|-------|
| `1.0`, `2.0` | Parent task — all its subtasks |
| `1.1`, `2.3` | Single subtask |
| `1.1,1.2,1.3` | Batch — those specific subtasks |

### 3. Spawn Implementer Subagent

**Use the Task tool** to spawn the `spice-implementer` agent:

```
Task tool:
  agent: spice-implementer
  prompt: |
    Plan: $1
    Task(s) to implement: {task spec}
    Context folder: {derived from plan path}
    
    **Skills to load:**
    - {skills from task's Skills field}
    - test-driven-development (ALWAYS)
    
    **Scope:**
    - Parent task (X.0): Complete ALL subtasks (X.1, X.2, X.3...)
    - Single subtask (X.Y): Complete just this subtask
    - Batch (X.1,X.2,X.3): Complete these specific subtasks in order
    
    Execute TDD protocol for each subtask:
    1. RED: Write tests, verify they FAIL
    2. GREEN: Minimal code, verify tests PASS
    3. REFACTOR: Clean up while green
    
    After each subtask:
    - Mark subtask [x] complete in plan
    
    After all assigned subtasks:
    - If parent task is fully complete, mark it [x]
    - Run full test suite
    - Commit with conventional message
    
    Return: tests passing, files modified, any issues.
```

### 4. Report Results

After subagent completes:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Task 1.0 Complete: UserService
   Skills: spice/languages/python, test-driven-development
   Subtasks: 1.1 ✓, 1.2 ✓, 1.3 ✓
   Tests: 8 passing
   Files: src/user/service.py, tests/user/test_service.py
   Commit: feat: implement UserService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next: Task 2.0 — UserRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Examples

```bash
# Execute next pending parent task (default)
/spice:execute /context/001-auth/plan-001.md

# Execute specific parent task (all its subtasks)
/spice:execute /context/001-auth/plan-001.md 2.0

# Execute specific subtask only (for debugging)
/spice:execute /context/001-auth/plan-001.md 2.1

# Execute batch of specific subtasks
/spice:execute /context/001-auth/plan-001.md 1.1,1.2,1.3

# Retry a failed parent task (fresh context)
/spice:execute /context/001-auth/plan-001.md 1.0
```
