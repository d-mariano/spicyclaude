---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [feature-name] [description-or-prd-or-ticket]
description: SPICE full workflow — ideate → research → plan → implement using isolated subagents
---

# SPICE Workflow

**Feature**: $1
**Input**: $2

Complete SDLC pipeline using **isolated subagents** for each phase.

---

## Pipeline Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                        SPICE WORKFLOW                               │
│                                                                     │
│  $1 (feature) + $2 (input)                                         │
│         │                                                           │
│         ▼                                                           │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐          │
│  │   IDEATE    │ ──► │  RESEARCH   │ ──► │    PLAN     │          │
│  │  (if idea)  │     │             │     │             │          │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘          │
│         │                   │                   │                  │
│         ▼                   ▼                   ▼                  │
│      prd.md            research.md           plan.md               │
│                                                 │                  │
│                                                 ▼                  │
│                                    ┌─────────────────────┐        │
│                                    │     ITERATE         │        │
│                                    │  (task by task)     │        │
│                                    └──────────┬──────────┘        │
│                                               │                   │
│                                               ▼                   │
│                                          progress.md              │
│                                          + code changes           │
└────────────────────────────────────────────────────────────────────┘
```

---

## Process

### Phase 0: Setup

1. Create context folder: `/context/{nnn}-$1/`
   - Find next available number
   - Sanitize feature name for folder

2. Determine starting point:
   - If $2 is a PRD path → Skip ideation
   - If $2 is a ticket ID → Start with research
   - If $2 is a description → Start with ideation

### Phase 1: Ideation (Optional)

**Skip if**: $2 is already a PRD path

**Spawn via Task tool** — `spice-ideator` agent:

```
Task tool:
  agent: spice-ideator
  prompt: |
    Context folder: /context/{nnn}-$1/
    Idea: $2
    
    Execute ideator protocol.
    Write output to: /context/{nnn}-$1/prd-001.md
```

**Wait for completion**, then review PRD with user.

**Checkpoint**: Confirm PRD before proceeding.

---

### Phase 2: Research

**Spawn via Task tool** — `spice-researcher` agent:

```
Task tool:
  agent: spice-researcher
  prompt: |
    Mode: Online
    Context folder: /context/{nnn}-$1/
    PRD: /context/{nnn}-$1/prd-001.md (if exists)
    Topic: $2
    
    Execute researcher protocol.
    Write output to: /context/{nnn}-$1/research-001.md
    Include Skills Detected section.
```

**Wait for completion**, then review research with user.

**Checkpoint**: Confirm research before proceeding.

---

### Phase 3: Planning

**Spawn via Task tool** — `spice-planner` agent:

```
Task tool:
  agent: spice-planner
  prompt: |
    PRD: /context/{nnn}-$1/prd-001.md
    Research: /context/{nnn}-$1/research-001.md
    
    Execute planner protocol.
    Write output to: /context/{nnn}-$1/plan-001.md
    
    Every task MUST have Skills: and Files: fields.
```

**Wait for completion**, then review plan with user.

**Checkpoint**: Confirm plan before implementation.

---

### Phase 4: Implementation

Use the iterate pattern — spawn **fresh subagent for each task**:

```
Task tool (for each task):
  agent: spice-implementer
  prompt: |
    Plan: /context/{nnn}-$1/plan-001.md
    Task: {task number}
    Skills to load: {from task's Skills field}
    
    Execute TDD protocol.
    Update progress.
    Mark task [x] complete.
```

**Report progress** after each task completes.

---

## Checkpoints

The workflow pauses at key points:

| After Phase | Checkpoint |
|-------------|------------|
| Ideation | "Does this PRD capture your requirements?" |
| Research | "Does this research cover the necessary context?" |
| Planning | "Does this plan look correct? Ready to implement?" |

User can:
- Approve and continue
- Request modifications
- Stop the workflow

---

## Context Folder Structure

After workflow completion:

```
/context/{nnn}-$1/
├── prd-001.md          # Product requirements
├── research-001.md     # Technical findings
├── plan-001.md         # TDD task breakdown
└── progress-001.md     # Implementation status
```

---

## Usage Patterns

### From Idea (Full Pipeline)

```bash
/spice:workflow user-auth "Users can log in with email and password"
```

Runs: Ideation → Research → Planning → Implementation

### From Existing PRD

```bash
/spice:workflow payment-flow /docs/payment-prd.md
```

Runs: Research → Planning → Implementation

### From Ticket

```bash
/spice:workflow feature-x JIRA-1234
```

Runs: Research (fetches ticket) → Planning → Implementation

---

## Partial Runs

If workflow is interrupted, resume from any phase:

```bash
# Resume from research
/spice:research /context/001-feature/ "topic"

# Resume from planning
/spice:plan /context/001-feature/prd-001.md /context/001-feature/research-001.md

# Resume from implementation
/spice:iterate /context/001-feature/
```

---

## Examples

```bash
# Full workflow from idea
/spice:workflow user-auth "Users can log in with email and password"

# From detailed description
/spice:workflow notifications "Real-time notification system with email digests and in-app alerts"

# From existing PRD
/spice:workflow payment-processing /context/payments/prd.md

# From Jira ticket
/spice:workflow api-rate-limiting JIRA-5678
```
