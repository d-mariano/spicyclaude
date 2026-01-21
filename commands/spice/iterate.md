---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [context-folder] [batch-size?]
description: SPICE iterate — spawn fresh subagent per batch of tasks until all complete
---

# SPICE Iterate

**Context folder**: $1
**Batch size**: $2 (default: `parent` — one high-level task at a time)

This command implements a **delegator pattern**: it reads the plan, then spawns a **fresh implementer subagent for each batch of tasks**.

---

## Batch Modes

| $2 Value | Behavior |
|----------|----------|
| `parent` (default) | One parent task at a time (e.g., all of Task 2.0: 2.1, 2.2, 2.3) |
| `1` | One subtask at a time (slowest, most isolated) |
| `3` | Three subtasks at a time |
| `5` | Five subtasks at a time |
| `all` | All remaining tasks in one subagent (fastest, least isolated) |

**Recommended**: Start with `parent` (default). If tasks are very small, try `3` or `5`.

---

## Process

### 1. Find the Plan

Read the most recent plan: `$1/plan-*.md`

### 2. Iteration Loop

```
WHILE tasks with [ ] status exist:

    1. Read plan, collect next batch of pending tasks:
       - If batch=parent: all subtasks under next incomplete parent (2.1, 2.2, 2.3)
       - If batch=N: next N pending subtasks
       - If batch=all: all remaining tasks
    
    2. If no pending tasks → STOP, report completion
    
    3. Extract **Skills:** from tasks (union of all skills needed)
    
    4. **SPAWN `spice-implementer` AGENT** via Task tool:
    
       ```
       Task tool:
         agent: spice-implementer
         prompt: |
           Plan: $1/plan-001.md
           Tasks to implement: {task list, e.g., "2.1, 2.2, 2.3"}
           Context folder: $1
           
           **Skills to load** (union from all tasks):
           - .claude/skills/spice/{language}.md
           - test-driven-development skill
           
           Execute TDD for EACH task in order:
           - Complete 2.1 (RED → GREEN → REFACTOR)
           - Complete 2.2 (RED → GREEN → REFACTOR)
           - Complete 2.3 (RED → GREEN → REFACTOR)
           
           Update progress after each task.
           Mark each task [x] as completed.
           Commit after batch complete.
           
           Return: tasks completed, tests passing, files modified.
       ```
    
    5. Wait for subagent to complete
    
    6. Report progress: "✅ Batch complete: Tasks 2.1, 2.2, 2.3"
    
    7. CONTINUE to next batch (new subagent)
```

---

## Examples

```bash
# Default: one parent task at a time (recommended)
/spice:iterate /context/001-auth/

# Explicit parent batching
/spice:iterate /context/001-auth/ parent

# Three subtasks at a time
/spice:iterate /context/001-auth/ 3

# Five subtasks at a time (faster, less isolation)
/spice:iterate /context/001-auth/ 5

# All remaining in one shot (fastest, use for small plans)
/spice:iterate /context/001-auth/ all
```

---

## Trade-offs

| Batch Size | Speed | Isolation | Context Usage | Best For |
|------------|-------|-----------|---------------|----------|
| `1` | Slowest | Highest | ~10% per task | Debugging, complex tasks |
| `3` | Medium | High | ~25% per batch | General use |
| `parent` | Medium | High | ~30% per parent | **Recommended default** |
| `5` | Fast | Medium | ~40% per batch | Small, simple tasks |
| `all` | Fastest | Lowest | Full context | Small plans, quick iteration |

**Rule of thumb**: If tasks are failing, reduce batch size. If tasks are trivial, increase it.

---

## Progress Reporting

After each batch:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Batch Complete: Task 2.0 (User Validation)
   Subtasks: 2.1, 2.2, 2.3
   Skills: spice/python, test-driven-development
   Tests: 8 passed
   Files: src/validators/user.py, tests/test_user.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: 6/12 tasks complete
Next batch: Task 3.0 (Password Validation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Handling Failures

If any task in a batch fails:

1. **STOP iteration** — don't proceed to next batch
2. Report which task failed and why
3. Suggest retry with smaller batch:
   ```
   /spice:execute $1/plan-001.md 2.2
   ```
4. After fix, continue:
   ```
   /spice:iterate $1/
   ```
