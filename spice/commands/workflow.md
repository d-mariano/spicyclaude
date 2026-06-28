---
allowed-tools: Task, Read, Write, Glob, Grep, Edit, MultiEdit, Bash, AskUserQuestion
argument-hint: "[feature-name] [description-or-prd]"
description: SPICE workflow — full pipeline from idea to implementation
---

# SPICE Workflow

**Feature**: $1
**Input**: $2

## Pipeline

```
Ideate → Research → [Web Research] → Design → Plan → [/clear] → Implement
  ↓         ↓              ↓            ↓        ↓                   ↓
prd.md  research.md   (updates)      tdd.md  plan.md            progress.md
            ↓
       (identifies gaps)
```

Phases 1-4 use subagents. Implementation uses main context with `/clear` discipline.

## Process

### Setup
Create folder: `/context/{nnn}-$1/`

### Phase 1: Ideate (if $2 is not a PRD path)
```
agent: spice-ideator
→ prd-001.md
```

### Phase 2: Research
```
agent: spice-researcher
→ research-001.md (with gaps identified)
```

### Phase 2.5: Web Research (if gaps exist)
```
If research-001.md has gaps:
  - Show gaps to user
  - Ask: Fill with web research? Import your own? Skip?
  - If fill: agent: spice-web-researcher
  - Updates research-001.md
```

### Phase 3: Design
```
agent: spice-designer
→ tdd-001.md
```

### Phase 4: Plan
```
agent: spice-planner
→ plan-001.md
```

### Question Forwarding (all phases)

Each subagent may output questions. When this happens:

```
while response contains "AWAITING_INPUT: true":
    questions = extract from "Questions Before Proceeding" section
    answers = AskUserQuestion(questions)
    response = re-invoke agent with original prompt + answers
```

This enables interactive clarification without leaving the workflow.

### Checkpoint
```
Planning complete! 

Optional: /spice:review-plan {folder}/ for critical external review
Recommend /clear before implementation.
After /clear: /spice:iterate {folder}/
```

### Phase 4.5: Plan Review (Optional)
```
For extra confidence before implementation:
/spice:review-plan {folder}/

Verdicts:
  🔴 Major Issues → Revise plan
  🟡 Minor Issues → Proceed with awareness
  🟢 Ready → Proceed to implementation
```

### Phase 5: Implementation
Main context with `/clear` discipline — see `/spice:iterate`.

### Phase 6: Implementation Review
```
After implementation complete:
/spice:review {folder}/

Verdicts:
  ✅ Complete → Ready for merge/deploy
  ⚠️ Caveats → Done but with documented gaps
  ❌ Incomplete → Continue implementation
```

## Examples

```bash
/spice:workflow user-auth "email/password authentication"
/spice:workflow payment-flow /docs/payment-prd.md
```
