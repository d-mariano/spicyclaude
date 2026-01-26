---
allowed-tools: Read, Glob, Grep, AskUserQuestion
argument-hint: [context-folder]
description: SPICE status — show progress and suggest next action
---

# SPICE Status

**Context folder**: $1

## Process

1. Read artifacts in `$1`: `prd-*.md`, `research-*.md`, `tdd-*.md`, `plan-*.md`, `progress-*.md`
2. Parse plan: count `[x]` vs `[ ]` tasks
3. Estimate context usage
4. Output status and suggest next action

## Output Format

```
📍 Feature: {name}
📄 Artifacts: PRD ✓, Research ✓, TDD ✓, Plan ✓
📋 Tasks: 3/5 complete
   [x] 1.0 UserService
   [x] 2.0 UserRepository
   [ ] 3.0 AuthController ← Next
💾 Context: ~35%
▶️  Next: /spice:implement $1 3.0
```

If context > 45%, recommend `/clear` first.

## Examples

```bash
/spice:status /context/001-auth/
```
