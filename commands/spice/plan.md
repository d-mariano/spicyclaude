---
allowed-tools: Task, Read, Glob, Grep
argument-hint: [prd-path] [research-path]
description: SPICE planning phase — spawn isolated subagent to create TDD task breakdown
---

# SPICE Planning

**PRD**: $1
**Research**: $2

This command spawns an **isolated subagent** to create the plan without polluting the main context.

---

## Process

**Use the Task tool** to spawn the `spice-planner` agent:

```
Task tool:
  agent: spice-planner
  prompt: |
    PRD: $1
    Research: $2
    
    Execute the planner protocol.
    Write output to: {same folder as PRD}/plan-001.md
    
    Every task MUST have:
    - **Skills**: {language skill}, test-driven-development
    - **Files**: {files involved}
    - RED phase (tests first)
    - GREEN phase (implementation)
    
    Valid skill references:
    - spice/python
    - spice/typescript
    - spice/go
    - test-driven-development (always include)
```

---

## Output

Plan saved to: `{context_folder}/plan-{nnn}.md`

The subagent runs in isolation — planning exploration doesn't pollute your main context.

---

## Next Step

After planning completes, run implementation:
```
/spice:iterate {context_folder}/
```

Or task-by-task:
```
/spice:execute {context_folder}/plan-001.md 1.1
```

---

## Examples

```bash
/spice:plan /context/001-auth/prd.md /context/001-auth/research-001.md
/spice:plan /docs/feature.md /context/002-feature/research-001.md
```
