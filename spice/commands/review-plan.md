---
allowed-tools: Task, Read, Glob, AskUserQuestion
argument-hint: "[context-folder]"
description: SPICE review-plan — critically review plan for gaps and issues
---

# SPICE Plan Review

**Folder**: $1

## Purpose

Provides a **critical external review** of the implementation plan. The reviewer is a separate agent that challenges the plan rather than validating it.

Use this when you want extra confidence before starting implementation.

## Process

1. Verify folder contains required files:
   - `plan-001.md` (required)
   - `prd-001.md` (required)
   - `tdd-001.md` (optional but recommended)

2. Spawn `spice-plan-reviewer` agent:

```
Task tool:
  agent: spice-plan-reviewer
  prompt: |
    Review the plan critically. Find problems.
    
    Plan: $1/plan-001.md
    PRD: $1/prd-001.md
    TDD: $1/tdd-001.md (if exists)
    Output: $1/plan-review-001.md
```

3. Present review findings to user

4. Based on verdict:
   - 🔴 Major Issues → Suggest `/spice:plan` revision
   - 🟡 Minor Issues → Note issues, suggest proceeding
   - 🟢 Ready → Approve for `/spice:iterate`

## When to Use

- Before starting implementation on complex features
- When plan seems too simple for the requirements
- When multiple people will implement the plan
- When you want a "second opinion" on the plan

## When to Skip

- Simple features with obvious plans
- When time is critical and plan looks solid
- When you're highly confident in the planner output

## Output

Creates `{folder}/plan-review-001.md` with:
- Requirements traceability
- Component traceability
- Dependency analysis
- Risk assessment
- Test coverage gaps
- Specific recommendations

## Examples

```bash
# Review plan before implementation
/spice:review-plan /context/001-auth/

# After review, based on verdict:
/spice:iterate /context/001-auth/      # If approved
/spice:plan /context/001-auth/prd-001.md /context/001-auth/tdd-001.md  # If revision needed
```
