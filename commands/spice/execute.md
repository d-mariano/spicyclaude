---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [plan-path] [task(s)]
description: SPICE execute — spawn isolated subagent to implement task(s) with TDD
---

# SPICE Execute

**Plan**: $1
**Task(s)**: $2 (single: `2.1`, batch: `2.1,2.2,2.3`, parent: `2.0`, or omit for next pending)

This command spawns an **isolated subagent** for the task(s). Each invocation gets a fresh 200K context.

---

## Process

### 1. Read Plan and Identify Tasks

Read the plan at $1 to find:
- If $2 is a subtask (e.g., `2.1`): that specific task
- If $2 is a parent (e.g., `2.0`): all subtasks (2.1, 2.2, 2.3)
- If $2 is a list (e.g., `2.1,2.2,2.3`): those specific tasks
- If $2 is omitted: next pending task

### 2. Extract Skills

Collect **Skills:** from all tasks in batch (union):
```markdown
### Task 2.1
**Skills**: spice/python, test-driven-development

### Task 2.2  
**Skills**: spice/python, test-driven-development
```

Skills to load: `spice/python`, `test-driven-development`

### 3. Spawn Implementer Subagent

**Use the Task tool** to spawn the `spice-implementer` agent:

```
Task tool:
  agent: spice-implementer
  prompt: |
    Plan: $1
    Tasks to implement: {task list}
    Context folder: {derived from plan path}
    
    **Skills to load:**
    - .claude/skills/spice/{language}.md
    - test-driven-development skill
    
    Execute TDD for each task in order.
    Mark each task [x] as completed.
    Commit after batch complete.
    
    Return: tasks completed, tests passing, files modified.
```

### 4. Report Results

After subagent completes:
- Show tasks accomplished
- Show test results
- Suggest next task/batch or report completion

---

## Examples

```bash
# Next pending task (single)
/spice:execute /context/001-auth/plan-001.md

# Specific subtask
/spice:execute /context/001-auth/plan-001.md 2.1

# All subtasks under parent 2.0
/spice:execute /context/001-auth/plan-001.md 2.0

# Explicit batch
/spice:execute /context/001-auth/plan-001.md 2.1,2.2,2.3

# Three tasks starting from 2.1
/spice:execute /context/001-auth/plan-001.md 2.1,2.2,2.3
```

---

## When to Use Execute vs Iterate

| Command | Use Case |
|---------|----------|
| `/spice:execute` | Manual control, debugging, specific tasks |
| `/spice:iterate` | Automated execution of remaining plan |

Use `/spice:execute` when you want to:
- Run a specific task or batch
- Debug a failing task with fresh context
- Control exactly what gets executed
