---
name: spice
description: "**S**ubagent-**P**owered **I**terative **C**oding **E**ngine — A multi-phase SDLC workflow using context-efficient patterns. Subagents for research/planning, main context for implementation with /clear discipline. Activates on: feature requests, multi-step implementations, complex refactoring, mentions of 'spice', 'workflow', 'plan and implement', or 'research and build'."
---

# SPICE — Subagent-Powered Iterative Coding Engine

**SPICE** orchestrates the complete software development lifecycle with **optimal context management**:
- **Phases 1-4** (Ideate, Research, Design, Plan): Subagents → clean markdown output
- **Phase 5** (Implement): Main context → skills work, `/clear` discipline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SPICE PIPELINE                                  │
│                                                                              │
│   EXPLORATION (Subagents)                    IMPLEMENTATION (Main Context)  │
│   ─────────────────────                      ────────────────────────────── │
│                                                                              │
│   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    ┌──────────────────┐   │
│   │ IDEATE │─►│RESEARCH│─►│ DESIGN │─►│  PLAN  │──► │   IMPLEMENT      │   │
│   └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘    │  (main context)  │   │
│       │           │           │           │  /clear │                  │   │
│       ▼           ▼           ▼           ▼         │  Task 1.0        │   │
│    prd.md    research.md   tdd.md     plan.md       │  → context ~40%  │   │
│                                                     │  /clear          │   │
│                                                     │                  │   │
│                                                     │  Task 2.0        │   │
│                                                     │  → context ~40%  │   │
│                                                     │  /clear          │   │
│                                                     │  ...             │   │
│                                                     └────────┬─────────┘   │
│                                                              │             │
│                                                              ▼             │
│                                                         progress.md        │
│                                                         + code changes     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## SDLC Phases

| Phase | Command | Runs In | Deliverable | Purpose |
|-------|---------|---------|-------------|---------|
| **Ideation** | `/spice:ideate` | Subagent | `prd-{nnn}.md` | Flesh out ideas into PRD |
| **Research** | `/spice:research` | Subagent | `research-{nnn}.md` | Explore codebase, gather context |
| **Design** | `/spice:design` | Subagent | `tdd-{nnn}.md` | Technical architecture & contracts |
| **Planning** | `/spice:plan` | Subagent | `plan-{nnn}.md` | Create TDD task breakdown |
| **Implement** | `/spice:implement` | **Main** | `progress-{nnn}.md` | Implement one parent task |
| **Iterate** | `/spice:iterate` | **Main** | `progress-{nnn}.md` | Implement all tasks with /clear |
| **Status** | `/spice:status` | Main | (display) | Show progress, suggest next action |
| **Workflow** | `/spice:workflow` | Mixed | All deliverables | End-to-end pipeline |

### Phase Variants

| Variant | Command | Difference |
|---------|---------|------------|
| Research (online) | `/spice:research` | Web search enabled |
| Research (offline) | `/spice:research-offline` | No web search, codebase only |
| Planning (with TDD) | `/spice:plan [prd] [tdd]` | Uses technical design |
| Planning (without TDD) | `/spice:plan [prd] [research]` | Skips design phase |

---

## Context Management

### Why This Design?

| Phase | Runs In | Why |
|-------|---------|-----|
| Ideate, Research, Design, Plan | Subagent | Exploration noise discarded after clean markdown output |
| **Implement** | **Main context** | Skills load properly, progressive disclosure works, TDD cycles benefit from accumulated understanding |

### The `/clear` Pattern

Implementation runs in main context but uses `/clear` to manage context growth:

```
/spice:iterate /context/001-auth/

  ↓ Task 1.0 complete (context ~38%)
  ↓ Task 2.0 complete (context ~47%)
  
  ⏸️ PAUSE — Context at 47%
  
  All state saved to:
  - plan-001.md (tasks 1.0, 2.0 marked [x])
  - progress-001.md (completion log)
  
  Run /clear, then:
  /spice:iterate /context/001-auth/
  
  ↓ Task 3.0 complete (context ~35%)
  ↓ ...
```

### State Preservation

All state lives in markdown — safe to `/clear` anytime:

| File | Contains |
|------|----------|
| `plan-001.md` | Task checkboxes `[x]` / `[ ]` |
| `progress-001.md` | Completion log, files modified, test counts |
| `prd-001.md` | Requirements (unchanged) |
| `research-001.md` | Patterns/context (unchanged) |
| `tdd-001.md` | Design decisions (unchanged) |

---

## Context Structure

All phases communicate via markdown in `/context/`:

```
/context/
└── {nnn}-{feature}/
    ├── prd-001.md          # Product requirements (from ideation)
    ├── research-001.md     # Technical findings (skills detected)
    ├── tdd-001.md          # Technical design (architecture, contracts)
    ├── plan-001.md         # TDD task breakdown (skills per task)
    └── progress-001.md     # Implementation status
```

---

## Skill System

### Phase Skills (Instructions)

Detailed instructions for each phase:
- [phases/ideate.md](phases/ideate.md) — PRD generation protocol
- [phases/research.md](phases/research.md) — Research protocol
- [phases/design.md](phases/design.md) — Technical design protocol
- [phases/plan.md](phases/plan.md) — Planning protocol
- [phases/execute.md](phases/execute.md) — Implementation protocol

### Language Skills (Conventions)

Language-specific conventions loaded during implementation:
- [languages/python.md](languages/python.md) — Python patterns, types, testing
- [languages/typescript.md](languages/typescript.md) — TypeScript patterns, types, testing
- [languages/go.md](languages/go.md) — Go patterns, idioms, testing

### External Skills

SPICE integrates with skills in your `.claude/skills/` directory:
- **`test-driven-development`** — TDD cycle, test structure, anti-patterns (required)

### Dynamic Loading

Skills are loaded **per-task** during implementation:

```markdown
- [ ] **2.0 UserService**
  - **Skills**: python-development, test-driven-development
```

During implementation, the main context loads:
1. `.claude/skills/python-development.md`
2. `.claude/skills/test-driven-development/SKILL.md`

Because implementation runs in **main context**, skills load properly with progressive disclosure.
