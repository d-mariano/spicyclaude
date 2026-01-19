---
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: [feature-name] [description-or-ticket]
description: SPICE full workflow — research → plan → implement using isolated subagents
---

# SPICE Workflow

**Feature**: $1
**Input**: $2

Each phase runs in an **isolated subagent** via the Task tool. This prevents context pollution between phases.

---

## Phase 0: Setup

1. Create context folder: `/context/{nnn}-$1/`
2. If $2 is a PRD path, copy to context folder
3. If $2 is a description, note for research phase

---

## Phase 1: Research (Isolated Subagent)

**Use the Task tool** to spawn the `spice-researcher` agent:

```
Task tool:
  agent: spice-researcher
  prompt: |
    Context folder: /context/{nnn}-$1/
    Topic/Input: $2
    
    Execute the researcher protocol.
    Write output to: /context/{nnn}-$1/research-001.md
    Include a **Skills Detected** section.
```

**Wait for subagent to complete**, then review research with user.

---

## Phase 2: Planning (Isolated Subagent)

**Use the Task tool** to spawn the `spice-planner` agent:

```
Task tool:
  agent: spice-planner
  prompt: |
    PRD: /context/{nnn}-$1/prd.md (if exists)
    Research: /context/{nnn}-$1/research-001.md
    
    Execute the planner protocol.
    Write output to: /context/{nnn}-$1/plan-001.md
    Every task MUST have **Skills:** and **Files:** fields.
```

**Wait for subagent to complete**, then review plan with user.

---

## Phase 3: Implementation (Isolated Subagent Per Task)

Use `/spice:iterate` which spawns a **fresh implementer subagent for each task**:

```
/spice:iterate /context/{nnn}-$1/
```

Or for manual control, use `/spice:execute` which also spawns isolated subagents:

```
/spice:execute /context/{nnn}-$1/plan-001.md 1.1
/spice:execute /context/{nnn}-$1/plan-001.md 1.2
```

**Each task gets a fresh context window** — no accumulated state from previous tasks.

---

## Why Isolated Subagents?

```
┌─────────────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR (this command)                                         │
│   • Manages flow between phases                                     │
│   • Reviews outputs with user                                       │
│   • Spawns subagents via Task tool                                  │
└─────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ RESEARCHER    │   │ PLANNER       │   │ IMPLEMENTER   │
│ (200K context)│   │ (200K context)│   │ (200K context)│
│               │   │               │   │ Per task!     │
│ Fresh context │   │ Fresh context │   │ Fresh context │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
   research.md           plan.md            progress.md
```

Benefits:
- **No context pollution** from exploration bleeding into implementation
- **No prompt bloat** from accumulated file reads
- **Each task starts fresh** with only what it needs
- **Phases communicate via files**, not shared context

---

## Example Usage

```bash
# Full workflow from idea
/spice:workflow user-auth "Users can log in with email and password"

# From a Jira ticket
/spice:workflow payment-flow JIRA-1234
```
