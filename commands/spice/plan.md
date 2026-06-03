---
allowed-tools: Task, Read, Glob, AskUserQuestion
argument-hint: [prd-path] [tdd-or-research-path]
description: SPICE plan — create TDD task breakdown
---

# SPICE Plan

**PRD**: $1
**Technical Input**: $2 (TDD preferred, or research)

## Process

1. Verify both files exist
2. Derive context folder from PRD path
3. Spawn `spice-planner` agent:

```
Task tool:
  agent: spice-planner
  prompt: |
    PRD: $1
    Technical Input: $2
    Output: {folder}/plan-001.md
```

4. **Handle question forwarding** (if needed):
   - If response contains `AWAITING_INPUT: true`:
     - Extract questions from "Questions Before Proceeding" section
     - Relay via `AskUserQuestion` following the rules below
     - Re-invoke agent with original prompt + "Previous questions answered:" section

   **`AskUserQuestion` relay rules** (the subagent wrote its questions in this shape; preserve it):

   - **Batch related questions** — up to 4 per call. Chain calls only if more remain.
   - **2-4 options per question**, each with a one-line description.
   - **Every option's description includes a counter.** Format: `"<implication> · Counter: <trade-off or objection>"`.
   - **Recommended option goes first** in the options array, labeled "(Recommended)" — only when the subagent flagged a clear lean from inputs.
   - **`header` is hard-capped at 12 characters** (e.g., "Approach", "AC interp", "Call sites").
   - **Question text states why it matters** — which AC item, pre-flight finding, or TDD section rides on the answer.
   - **Always offer a defer path** unless the plan genuinely cannot proceed: `"Defer — file under Stakeholder Decisions Needed Before Merge"`.
   - **Do NOT add an "Other" option** — `AskUserQuestion` surfaces a free-text input automatically; an explicit "Other" wastes one of the 4 slots.
   - **Use `multiSelect: true`** when choices are not mutually exclusive (e.g., "Which footgun categories apply?", "Which AC items need stakeholder clarification?"). Default `false` for picking-one decisions.
   - **Use the `preview` field for concrete-shape choices** (single-select only) — function signatures, directory layouts, sample test-name patterns. Skip for preference questions where label + description suffice.

   If the subagent's questions don't already follow this shape, reshape them when relaying — don't pass raw `AWAITING_INPUT` text straight through.

5. After completion, suggest: `/spice:iterate {folder}/`

## With TDD vs Without

| With TDD | Without (research only) |
|----------|------------------------|
| Tasks from architecture | Tasks from requirements |
| Tests from API contracts | Tests from functional specs |
| More precise breakdown | More exploration needed |

## Examples

```bash
/spice:plan /context/001-auth/prd-001.md /context/001-auth/tdd-001.md
/spice:plan /context/002-ui/prd-001.md /context/002-ui/research-001.md
```
