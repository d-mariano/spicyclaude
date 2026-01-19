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

Parse the task's skills:
```markdown
### Task 2.1: Implement validation
**Skills**: spice/python, test-driven-development
```

Extract: `spice/python`, `test-driven-development`

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
    - .claude/skills/spice/{language}.md (from task's Skills field)
    - test-driven-development skill (ALWAYS)
    
    Load ONLY these skills. Execute TDD protocol.
    Update progress. Mark task [x] complete.
    Commit if parent task complete.
    
    Return: tests passing, files modified, any issues.
```

### 4. Report Results

After subagent completes:
- Show what was accomplished
- Show test results
- Suggest next task or report completion

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
- Parallel execution possible (future)

---

## Examples

```bash
# Execute next pending task
/spice:execute /context/001-auth/plan-001.md

# Execute specific task
/spice:execute /context/001-auth/plan-001.md 2.1

# Execute after a failure (fresh context, retry)
/spice:execute /context/001-auth/plan-001.md 2.1
```
