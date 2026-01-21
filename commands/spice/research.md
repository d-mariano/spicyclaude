---
allowed-tools: Task, Read, Glob, Grep
argument-hint: [topic-or-ticket] [context-folder]
description: SPICE research phase — spawn isolated subagent to explore codebase and gather context
---

# SPICE Research

**Topic**: $1
**Context folder**: $2 (default: `/context/current/`)

This command spawns an **isolated subagent** to conduct research without polluting the main context.

---

## Process

**Use the Task tool** to spawn the `spice-researcher` agent:

```
Task tool:
  agent: spice-researcher
  prompt: |
    Topic: $1
    Context folder: $2
    
    Execute the researcher protocol.
    Write output to: $2/research-001.md
    
    MUST include a **Skills Detected** section:
    ```
    ## Skills Detected
    
    Languages involved:
    - **spice/python** — Backend uses FastAPI
    - **spice/typescript** — Frontend uses React
    
    Skills to load: spice/python, spice/typescript, test-driven-development
    ```
    
    The planner uses this section to assign skills per task.
```

---

## Output

Research saved to: `$2/research-{nnn}.md`

The subagent runs in isolation — its exploration doesn't pollute your main context.

---

## Next Step

After research completes, run planning:
```
/spice:plan $2/prd.md $2/research-001.md
```

---

## Examples

```bash
/spice:research "user authentication" /context/001-auth/
/spice:research JIRA-1234 /context/002-payment/
/spice:research /docs/feature-prd.md /context/003-feature/
```
