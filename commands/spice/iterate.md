---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [context-folder] [batch-size?]
description: SPICE iterate — spawn fresh subagent for each batch of work until all complete
---

# SPICE Iterate

**Context folder**: $1
**Batch size**: $2 (optional — `parent` (default), `subtask`/`1`, or number like `3` for N subtasks)

This command implements a **delegator pattern**: reads the plan, then spawns implementer subagents.

---

## Batch Options

| Option | Behavior | Use When |
|--------|----------|----------|
| `parent` (default) | One subagent per parent task (1.0 with all subtasks) | Most cases — balanced |
| `3`, `5`, etc. | One subagent per N consecutive subtasks | Large parent tasks |
| `subtask` or `1` | One subagent per subtask | Debugging, max isolation |

```bash
# Default: one subagent per parent task
/spice:iterate /context/001-auth/

# Batch 3 subtasks together
/spice:iterate /context/001-auth/ 3

# Single subtask (slowest, most isolated)
/spice:iterate /context/001-auth/ subtask
```

---

## Process

### 1. Find the Plan

Read the most recent plan: `$1/plan-*.md`

If multiple plans exist, use the latest (highest number).

### 2. Iteration Loop (Parent Mode — Default)

**Spawn a NEW subagent for EACH parent task (1.0, 2.0, etc.):**

```
WHILE parent tasks with unchecked subtasks exist:

    1. Read plan, find next parent task with pending subtasks
       (e.g., "- [ ] **1.0 UserService**" with unchecked children)
    
    2. If no pending tasks → STOP, report completion
    
    3. Extract the task's **Skills:** field
    
    4. **SPAWN `spice-implementer` AGENT** via Task tool:
    
       Task tool:
         agent: spice-implementer
         prompt: |
           Plan: $1/plan-001.md
           Task: 1.0 (complete ALL subtasks: 1.1, 1.2, 1.3)
           Context folder: $1
           
           **Skills to load:**
           - {language skill from task}
           - test-driven-development
           
           Execute TDD for ALL subtasks in this parent task:
           - 1.1 RED: Write failing tests
           - 1.2 GREEN: Implement
           - 1.3 REFACTOR: Clean up
           
           Mark each subtask [x] as you complete it.
           Mark parent task [x] when all subtasks done.
           Commit when parent task complete.
           
           Return: tests passing, files modified, any issues.
    
    5. Wait for subagent completion
    
    6. Report progress:
       "✅ Task 1.0 Complete: UserService (3 subtasks)"
    
    7. CONTINUE to next parent task
```

### 3. Iteration Loop (Numeric Batch Mode)

If `$2` is a number (e.g., `3`), batch N subtasks together:

```
WHILE subtasks with [ ] exist:

    1. Find next N pending subtasks (e.g., 1.1, 1.2, 1.3 for batch=3)
       - Can span across parent tasks if needed
    
    2. Collect all skills needed for this batch
    
    3. Spawn implementer for the batch:
    
       Task tool:
         agent: spice-implementer
         prompt: |
           Plan: $1/plan-001.md
           Subtasks to complete: 1.1, 1.2, 1.3
           Context folder: $1
           
           **Skills to load:**
           - {union of all skills needed}
           - test-driven-development
           
           Execute each subtask in order.
           Mark each [x] as complete.
           Commit after batch.
    
    4. Wait, report, continue with next batch
```

### 4. Iteration Loop (Single Subtask Mode)

If `$2` is `subtask` or `1`:

```
WHILE subtasks with [ ] exist:

    1. Find next single pending subtask
    2. Spawn implementer for JUST that subtask
    3. Wait, report, continue
```

---

## Progress Reporting

After each batch:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Task 1.0 Complete: UserService
   Skills: spice/languages/python, test-driven-development
   Subtasks: 3/3 complete
   Tests: 8 passing
   Files: src/user/service.py, tests/user/test_service.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: 2/5 parent tasks complete
Next: Task 2.0 — UserRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Handling Failures

If a subagent reports failure:

1. **STOP iteration** — don't proceed to next batch
2. Report the failure with details
3. Suggest retry options:
   ```bash
   # Retry the whole parent task
   /spice:execute $1/plan-001.md 1.0
   
   # Or retry with single subtask for debugging
   /spice:iterate $1 1
   ```

---

## Batch Size Comparison

| Batch | Subagent Calls (12 subtasks, 4 parents) | Speed |
|-------|----------------------------------------|-------|
| `parent` (default) | 4 calls | ⚡ Fast |
| `3` | 4 calls | ⚡ Fast |
| `2` | 6 calls | Medium |
| `subtask`/`1` | 12 calls | Slow |

**Recommended starting points:**
- `parent` — Default, keeps RED/GREEN/REFACTOR together
- `3` — Good if parent tasks have 5+ subtasks each

---

## Examples

```bash
# Default: one subagent per parent task (recommended)
/spice:iterate /context/001-auth/

# Batch 3 subtasks at a time
/spice:iterate /context/001-auth/ 3

# Batch 5 subtasks at a time (for large plans)
/spice:iterate /context/001-auth/ 5

# Single subtask (maximum isolation, debugging)
/spice:iterate /context/001-auth/ subtask
/spice:iterate /context/001-auth/ 1

# After fixing a failure, continue
/spice:iterate /context/001-auth/
```
