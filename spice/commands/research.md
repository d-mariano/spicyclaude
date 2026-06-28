---
allowed-tools: Task, Read, Glob, AskUserQuestion
argument-hint: "[input...] (file, folder, or multiple files)"
description: SPICE research — analyze inputs, explore codebase, identify gaps
---

# SPICE Research

**Input**: $ARGS

## Flexible Inputs

Accepts any combination of:
- **File path** — PRD, external research (Gemini, Claude), ideas
- **Folder path** — Reads all `.md` files, continues existing research
- **Multiple files** — Combines all inputs

```bash
# Single file
/spice:research /context/001-auth/prd-001.md

# Folder (reads all .md files)
/spice:research /context/001-auth/

# Multiple files (PRD + external research)
/spice:research /docs/prd.md /docs/gemini-research.md

# External research only (for greenfield)
/spice:research /docs/claude-deep-dive.md
```

## Process

1. Parse inputs — identify files/folders provided
2. Create or identify context folder
3. Spawn `spice-researcher` agent:

```
Task tool:
  agent: spice-researcher
  prompt: |
    Inputs: $ARGS
    Output: {folder}/research-001.md
    
    1. Read and categorize all inputs (PRD, external research, ideas)
    2. Explore codebase for patterns, files, packages
    3. Detect skills/languages
    4. Identify research gaps
    5. Generate web research plan if gaps exist
```

4. **Handle question forwarding** (if needed):
   - If response contains `AWAITING_INPUT: true`:
     - Extract questions from "Questions Before Proceeding" section
     - Use `AskUserQuestion` tool to get answers
     - Re-invoke agent with original prompt + answers

5. Review output and suggest next step based on gaps:
   - **If gaps exist**: Suggest `/spice:web-research {folder}/`
   - **If no gaps**: Suggest `/spice:design {folder}/prd-001.md {folder}/research-001.md`

## Input Auto-Detection

The researcher auto-detects input types:

| Content | Detected As | Handling |
|---------|-------------|----------|
| "PRD", "Requirements", "FR-01" | PRD | Extract requirements |
| "Research", "Findings", citations | External Research | Summarize findings |
| Short, informal text | Idea/Prompt | Research feasibility |
| Existing context folder | Continuation | Update research |

## Output

Creates/updates `{folder}/research-001.md` with:
- Inputs analyzed
- External research summary (if provided)
- Codebase analysis
- Skills detected
- Research gaps (if any)
- Recommended web research plan (if gaps)
- Next steps

## Examples

```bash
# Standard: PRD exists, research codebase
/spice:research /context/001-auth/prd-001.md

# With external research: Gemini deep-dive + PRD
/spice:research /docs/prd.md /docs/gemini-auth-research.md

# Continue existing context
/spice:research /context/001-auth/

# Greenfield with deep-dive only
/spice:research /docs/claude-deep-dive.md
```
