---
allowed-tools: Read, Write, Edit, MultiEdit, Bash, Grep, Glob, AskUserQuestion
argument-hint: [context-folder] [task?]
description: SPICE implement — execute one parent task with TDD (main context)
---

# SPICE Implement

**Context folder**: $1
**Task**: $2 (optional — defaults to next pending)

Implements ONE parent task in main context. Load the full protocol:

`.claude/skills/spice/phases/execute.md`

## Quick Reference

1. Read `plan-*.md`, find target task
2. Load skills from task's `**Skills:**` field
3. Execute TDD cycle for each subtask (RED → GREEN → REFACTOR)
4. Mark tasks `[x]` as complete
5. Commit when parent task done
6. If context > 45%, suggest `/clear`

## Examples

```bash
/spice:implement /context/001-auth/
/spice:implement /context/001-auth/ 2.0
```
