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
| **Research** | `/spice:research` | Subagent | `research-{nnn}.md` | Analyze inputs, explore codebase, identify gaps |
| **Web Research** | `/spice:web-research` | Subagent | Updates `research-{nnn}.md` | Fill research gaps with targeted web searches |
| **Design** | `/spice:design` | Subagent | `tdd-{nnn}.md` | Technical architecture & contracts |
| **Planning** | `/spice:plan` | Subagent | `plan-{nnn}.md` | Create TDD task breakdown with coverage analysis |
| **Plan Review** | `/spice:review-plan` | Subagent | `plan-review-{nnn}.md` | Critical external review (optional) |
| **Implement** | `/spice:implement` | **Main** | `progress-{nnn}.md` | Implement one parent task |
| **Iterate** | `/spice:iterate` | **Main** | `progress-{nnn}.md` | Implement all tasks with /clear |
| **Review** | `/spice:review` | **Main** | `review-{nnn}.md` | Comprehensive implementation review |
| **Status** | `/spice:status` | Main | (display) | Show progress, suggest next action |
| **Workflow** | `/spice:workflow` | Mixed | All deliverables | End-to-end pipeline |

### Plan Coverage Analysis (Built-in)

The planner automatically generates a **Coverage Analysis** section:
- Maps requirements to tasks
- Maps components to tasks
- Identifies gaps before implementation
- Asks for confirmation if gaps detected

### Plan Review (Optional)

For extra confidence, use `/spice:review-plan` — a separate agent that **critically challenges** the plan:
- Fresh perspective (not the author)
- Explicitly looks for problems
- Checks traceability, dependencies, risks
- Verdicts: 🔴 Major Issues / 🟡 Minor Issues / 🟢 Ready

### Implementation Review

After implementation, use `/spice:review` to verify:
- All tests pass
- Linting clean
- Requirements implemented
- Components delivered
- Verdicts: ✅ Complete / ⚠️ Caveats / ❌ Incomplete

### Flexible Research Inputs

`/spice:research` accepts any combination of:
- **File path** — PRD, external research (Gemini, Claude deep-dive), ideas
- **Folder path** — Reads all `.md` files, continues existing research
- **Multiple files** — Combines all inputs

```bash
/spice:research /context/001-auth/prd-001.md           # PRD only
/spice:research /docs/prd.md /docs/gemini-research.md  # PRD + external
/spice:research /context/001-auth/                      # Continue existing
```

### Research → Web Research Flow

```
/spice:research [inputs]
    ↓
research-001.md (with "Research Gaps" section)
    ↓
/spice:web-research [folder]  ← Optional, fills gaps
    ↓
research-001.md (updated with "Web Research Findings")
    ↓
/spice:design
```

### Question Forwarding

Subagents can request user input via **question forwarding**:

1. Subagent outputs `## Questions Before Proceeding` section
2. Subagent ends with `AWAITING_INPUT: true` marker
3. Caller extracts questions and uses `AskUserQuestion` tool
4. Caller re-invokes subagent with answers

This enables interactive clarification without losing subagent isolation.

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
    ├── research-001.md     # Technical findings + gaps + web research
    ├── tdd-001.md          # Technical design (architecture, contracts)
    ├── plan-001.md         # TDD task breakdown (with coverage analysis)
    ├── plan-review-001.md  # Critical plan review (optional)
    ├── progress-001.md     # Implementation status
    ├── review-001.md       # Implementation review (when complete)
    └── lessons-learned.md  # Captured improvements (optional)
```

---

## Skill System

### Phase Skills (Instructions)

Detailed instructions for each phase:
- [phases/ideate.md](phases/ideate.md) — PRD generation protocol
- [phases/research.md](phases/research.md) — Codebase analysis + gap identification
- [phases/web-research.md](phases/web-research.md) — Targeted web searches for gaps
- [phases/design.md](phases/design.md) — Technical design protocol
- [phases/plan.md](phases/plan.md) — Planning protocol + coverage analysis
- [phases/review-plan.md](phases/review-plan.md) — Critical plan review
- [phases/execute.md](phases/execute.md) — Implementation protocol + lessons learned
- [phases/review.md](phases/review.md) — Implementation review protocol

### Language Skills (Conventions)

Language-specific conventions loaded during implementation:

- [languages/typescript.md](languages/typescript.md) — TypeScript patterns, types, testing
- [languages/go.md](languages/go.md) — Go patterns, idioms, testing

### External Skills

SPICE integrates with skills from the `spicy-skills` plugin (declared as a dependency):
- **`test-driven-development`** — TDD cycle, test structure, anti-patterns (required)
- **`python-development`** — Python patterns, types, testing
- **`terraform-development`** - Terraform best practices and validation instructions
- **`frontend-development`** - Frontend best practices and validation instructions

### Dynamic Loading

Skills are loaded **per-task** during implementation:

```markdown
- [ ] **2.0 UserService**
  - **Skills**: python-development, test-driven-development
```

During implementation, the main context loads:
1. The `python-development` skill
2. The `test-driven-development` skill

Because implementation runs in **main context**, skills load properly with progressive disclosure.
