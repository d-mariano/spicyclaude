---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [topic-or-prd] [context-folder?]
description: SPICE research — spawn isolated subagent to explore codebase and gather context (web search ENABLED)
---

# SPICE Research (Online)

**Topic**: $1
**Context folder**: $2 (default: auto-detect or `/context/current/`)

This command spawns an **isolated subagent** with web search enabled.

---

## Process

### 1. Determine Context Folder

- If $2 is provided, use it
- If $1 is a path to a PRD, use its parent folder
- Otherwise, find or create appropriate folder in `/context/`

### 2. Spawn Researcher Subagent

**Use the Task tool** to spawn the `spice-researcher` agent:

```
Task tool:
  agent: spice-researcher
  prompt: |
    Mode: Online (web search enabled)
    Topic: $1
    Context folder: {context_folder}
    
    Execute the researcher protocol.
    
    1. Understand the request (read PRD if path given)
    2. Detect languages and skills in codebase
    3. Explore codebase for patterns
    4. Conduct web searches for external docs (cite sources)
    5. Identify third-party capabilities
    
    Write output to: {context_folder}/research-001.md
    
    CRITICAL: Include a **Skills Detected** section:
    ```
    ## Skills Detected
    
    ### Languages Involved
    - **spice/languages/python** — {where/why}
    
    ### Skills for Implementation
    - `spice/languages/python`
    - `test-driven-development`
    ```
```

### 3. Review Output

After subagent completes:
- Summarize key findings
- Highlight skills detected
- Suggest next step: `/spice:plan`

---

## When to Use Online vs Offline

| Use **Online** (`/spice:research`) | Use **Offline** (`/spice:research-offline`) |
|-----------------------------------|---------------------------------------------|
| Need framework documentation | Air-gapped environment |
| Using unfamiliar libraries | Already know the tech stack |
| API specs or protocols | Pure codebase refactoring |
| Best practices research | Sensitive/restricted network |

---

## Next Step

After research approval:
```bash
/spice:plan {context_folder}/prd-001.md {context_folder}/research-001.md
```

---

## Examples

```bash
# Research a topic
/spice:research "user authentication" /context/001-auth/

# Research from PRD
/spice:research /context/001-payments/prd-001.md

# Research a Jira ticket
/spice:research JIRA-1234 /context/002-feature/

# Default folder
/spice:research "payment processing"
```
