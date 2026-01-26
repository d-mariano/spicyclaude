---
allowed-tools: Task, Read, Write, Glob, Grep, Edit, MultiEdit, Bash, AskUserQuestion
argument-hint: [feature-name] [description-or-prd]
description: SPICE workflow — full pipeline from idea to implementation
---

# SPICE Workflow

**Feature**: $1
**Input**: $2

## Pipeline

```
Ideate → Research → Design → Plan → [/clear] → Implement
  ↓         ↓         ↓        ↓                   ↓
prd.md  research.md tdd.md  plan.md            progress.md
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
→ research-001.md
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

### Checkpoint
```
Planning complete! Recommend /clear before implementation.
After /clear: /spice:iterate {folder}/
```

### Phase 5: Implementation
Main context with `/clear` discipline — see `/spice:iterate`.

## Examples

```bash
/spice:workflow user-auth "email/password authentication"
/spice:workflow payment-flow /docs/payment-prd.md
```
