---
allowed-tools: Task, Read, Glob, AskUserQuestion
argument-hint: [folder] [optional-topic]
description: SPICE web-research — fill research gaps with targeted web searches
---

# SPICE Web Research

**Folder**: $1
**Topic** (optional): $2

## Purpose

Fills knowledge gaps identified by `/spice:research`. Reads the research file, extracts gaps, performs targeted web searches, and updates the research document.

## Process

1. Verify folder contains `research-001.md`
2. Spawn `spice-web-researcher` agent:

```
Task tool:
  agent: spice-web-researcher
  prompt: |
    Folder: $1
    Topic: $2 (if provided, focus on this; otherwise use gaps from research file)
    
    1. Read research-001.md
    2. Extract Research Gaps and Recommended Web Research sections
    3. Execute web searches for each gap (or specific topic)
    4. Document findings with sources
    5. Update research-001.md with "Web Research Findings" section
    6. Update Research Gaps table (mark filled)
    7. Update Recommendations with new knowledge
```

3. **Handle question forwarding** (if needed):
   - If response contains `AWAITING_INPUT: true`:
     - Extract questions from "Questions Before Proceeding" section
     - Use `AskUserQuestion` tool to get answers
     - Re-invoke agent with original prompt + answers

4. Review updated research and suggest next step:
   - **If gaps remain**: Suggest running again or proceeding
   - **If all filled**: Suggest `/spice:design`

## Usage

```bash
# Research all gaps in the file
/spice:web-research /context/001-auth/

# Research specific topic (overrides gaps list)
/spice:web-research /context/001-auth/ "JWT refresh token best practices"

# Research multiple topics
/spice:web-research /context/001-auth/ "rate limiting Redis"
/spice:web-research /context/001-auth/ "email verification flow"
```

## What It Does

1. **Reads** existing `research-001.md`
2. **Extracts** gaps from "Research Gaps" and "Recommended Web Research" sections
3. **Searches** the web for each topic
4. **Documents** findings with sources and code examples
5. **Updates** the research file (doesn't create new file)
6. **Marks** gaps as filled in the table

## Output

Updates `{folder}/research-001.md` with:

```markdown
## Web Research Findings

*Added by /spice:web-research on {date}*

### {Topic 1}
**Search**: "{query}"
**Key Findings**: ...
**Best Practice**: ...
**Sources**: ...

### {Topic 2}
...

---

## Research Gaps (Updated)

| Topic | Status |
|-------|--------|
| JWT rotation | ✅ Filled |
| Rate limiting | ✅ Filled |
| Email verification | ⏳ Remaining |
```

## Examples

```bash
# After /spice:research identified gaps
/spice:web-research /context/001-auth/

# Check if more gaps remain
/spice:status /context/001-auth/

# When ready
/spice:design /context/001-auth/prd-001.md /context/001-auth/research-001.md
```
