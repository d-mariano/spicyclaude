---
allowed-tools: Task, Read, Glob, Grep
argument-hint: [prd-path] [research-path]
description: SPICE plan — spawn isolated subagent to create TDD task breakdown
---

# SPICE Planning

**PRD**: $1
**Research**: $2

This command spawns an **isolated subagent** to create the plan.

---

## Process

### 1. Validate Inputs

Verify both files exist:
- PRD document at $1
- Research document at $2

Derive context folder from the PRD path.

### 2. Spawn Planner Subagent

**Use the Task tool** to spawn the `spice-planner` agent:

```
Task tool:
  agent: spice-planner
  prompt: |
    PRD: $1
    Research: $2
    Context folder: {derived from PRD path}
    
    Execute the planner protocol.
    
    1. Read PRD and research documents
    2. Note Skills Detected from research
    3. Break work into TDD tasks
    4. Assign skills to every task
    5. Define RED/GREEN phases
    
    Write output to: {context_folder}/plan-001.md
    
    CRITICAL: Every task MUST have these fields:
    
    ```markdown
    ### Task 2.1: {Title}
    
    **Skills**: {language skill}, test-driven-development
    **Files**: {files involved}
    **Depends on**: {task dependency or "None"}
    
    #### RED: Write failing tests
    - `test_name` — Description
    
    #### GREEN: Implement
    - What to implement
    ```
    
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
# Standard planning
/spice:plan /context/001-auth/prd-001.md /context/001-auth/research-001.md

# Different folder structure
/spice:plan /docs/feature.md /context/001-feature/research-001.md
```
