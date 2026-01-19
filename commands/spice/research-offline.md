---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [topic-or-prd] [context-folder?]
description: SPICE research offline — spawn isolated subagent for codebase-only research (NO web search)
---

# SPICE Research (Offline)

**Topic**: $1
**Context folder**: $2 (default: auto-detect or `/context/current/`)

This command spawns an **isolated subagent** WITHOUT web search.

Use this when:
- Working in an air-gapped environment
- Doing pure codebase refactoring
- Already familiar with the technology
- Network restrictions apply

---

## Process

### 1. Determine Context Folder

- If $2 is provided, use it
- If $1 is a path to a PRD, use its parent folder
- Otherwise, find or create appropriate folder in `/context/`

### 2. Spawn Offline Researcher Subagent

**Use the Task tool** to spawn the `spice-researcher-offline` agent:

```
Task tool:
  agent: spice-researcher-offline
  prompt: |
    Mode: Offline (NO web search)
    Topic: $1
    Context folder: {context_folder}
    
    Execute the researcher protocol in OFFLINE mode.
    
    1. Understand the request (read PRD if path given)
    2. Detect languages and skills in codebase
    3. Explore codebase thoroughly for patterns
    4. Analyze installed packages for capabilities
    5. Document assumptions that would need verification
    
    Write output to: {context_folder}/research-001.md
    
    CRITICAL: Include both sections:
    
    **Skills Detected** section:
    ```
    ## Skills Detected
    
    ### Languages Involved
    - **spice/languages/python** — {where/why}
    
    ### Skills for Implementation
    - `spice/languages/python`
    - `test-driven-development`
    ```
    
    **Offline Mode Notes** section:
    ```
    ## Offline Mode Notes
    
    ### Assumptions Made
    - {assumptions}
    
    ### Recommended Follow-up Research
    - {topics needing external verification}
    ```
```

### 3. Review Output

After subagent completes:
- Summarize key findings
- Highlight assumptions made
- Note any recommended follow-up research
- Suggest next step: `/spice:plan` or `/spice:research` (online) if needed

---

## Switching to Online

If offline research reveals topics needing external docs:

```bash
# Run online research for specific topics
/spice:research "OAuth2 PKCE flow" /context/001-auth/
```

---

## Next Step

After research approval:
```bash
/spice:plan {context_folder}/prd-001.md {context_folder}/research-001.md
```

---

## Examples

```bash
# Offline codebase research
/spice:research-offline "refactor user service" /context/001-refactor/

# From PRD, offline
/spice:research-offline /context/001-auth/prd-001.md

# Default folder, offline
/spice:research-offline "database migration patterns"
```
