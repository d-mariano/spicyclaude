---
allowed-tools: Read, Write, Edit, MultiEdit, Bash, Grep, Glob, AskUserQuestion
argument-hint: [context-folder]
description: SPICE iterate — implement tasks until context threshold (main context)
---

# SPICE Iterate

**Context folder**: $1

Implements tasks sequentially until context ~45%, then pauses. Load the full protocol:

`.claude/skills/spice/phases/execute.md`

## Quick Reference

```
WHILE pending tasks AND context < 45%:
  1. Find next pending parent task
  2. Load skills, execute TDD
  3. Mark complete, commit
  4. Check context → continue or pause
```

After pause: `/clear` then `/spice:iterate $1` to resume.

## Examples

```bash
/spice:iterate /context/001-auth/
```

## vs /spice:implement

| Command | Behavior |
|---------|----------|
| `implement` | One task, then stop |
| `iterate` | Loop until context threshold |
