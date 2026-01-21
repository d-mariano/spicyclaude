---
allowed-tools: Task, Read, Glob, Grep
argument-hint: [prd-path] [tdd-or-research-path]
description: SPICE plan — spawn isolated subagent to create TDD task breakdown from PRD and technical design
---

# SPICE Planning

**PRD**: $1
**Technical Input**: $2 (Technical Design Document preferred, or research if design phase was skipped)

This command spawns an **isolated subagent** to create the plan.

---

## Process

### 1. Validate Inputs

Verify both files exist:
- PRD document at $1
- Technical document at $2 (either `tdd-*.md` or `research-*.md`)

Derive context folder from the PRD path.

### 2. Determine Input Type

Check if $2 is a TDD or research file:
- If filename contains `tdd`: Use as technical design (preferred)
- If filename contains `research`: Use as research context

### 3. Spawn Planner Subagent

**Use the Task tool** to spawn the `spice-planner` agent:

```
Task tool:
  agent: spice-planner
  prompt: |
    PRD: $1
    Technical Input: $2 (type: {tdd|research})
    Context folder: {derived from PRD path}
    
    Execute the planner protocol.
    
    1. Read PRD document
    2. Read technical input ($2)
       - If TDD: Use architecture, contracts, and interfaces for task breakdown
       - If Research: Use patterns and skills for task breakdown
    3. Break work into Test Driven Development tasks
    4. Assign skills to every task
    5. Define RED/GREEN phases
    
    Write output to: {context_folder}/plan-001.md
    
    CRITICAL: Use this checkbox format for ALL tasks:
    
    ```markdown
    - [ ] **1.0 Component Name**
      - **Skills**: spice/languages/python, test-driven-development
      - **Files**: src/file.py, tests/test_file.py
      - **Depends on**: None
      - [ ] 1.1 RED: Write failing tests
        - `test_name` — description
      - [ ] 1.2 GREEN: Implement
        - Implementation details
    ```
    
    DO NOT create separate "Task Checklist" section.
    The Tasks section IS the checklist with checkboxes.
    
    If using TDD, reference:
    - API contracts for test expectations
    - Data models for entity structure
    - Interfaces for implementation signatures
    
    Valid skill references:
    - spice/languages/python
    - spice/languages/typescript
    - spice/languages/go
    - test-driven-development (always include)
```

### 3. Review Output

After subagent completes:
- Summarize the task breakdown
- Show task count and dependencies
- Suggest next step: `/spice:iterate` or `/spice:execute`

---

## With TDD vs Without

| With TDD (`/spice:design` first) | Without TDD (research only) |
|----------------------------------|----------------------------|
| Tasks derived from architecture | Tasks derived from requirements |
| Test cases from API contracts | Test cases from functional reqs |
| Interfaces already defined | Interfaces designed during planning |
| More precise task breakdown | More exploration during implementation |

**Recommendation**: Use the design phase for anything involving APIs, data models, or system integration.

---

## Task Structure Review

Before proceeding to implementation, verify:
- [ ] Every task has `**Skills:**` field
- [ ] Every task has `**Files:**` field
- [ ] RED phase lists specific test names
- [ ] GREEN phase lists specific implementations
- [ ] Tasks are ordered by dependencies

---

## Next Step

After plan approval:
```bash
# Execute all tasks
/spice:iterate {context_folder}/

# Or task-by-task
/spice:execute {context_folder}/plan-001.md 1.1
```

---

## Examples

```bash
# Planning with TDD (recommended for APIs/services)
/spice:plan /context/001-auth/prd-001.md /context/001-auth/tdd-001.md

# Planning with research only (simpler features)
/spice:plan /context/002-ui/prd-001.md /context/002-ui/research-001.md
```
