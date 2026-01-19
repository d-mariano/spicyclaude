---
name: spice
description: "****S**ubagent-**P**owered **I**terative **C**oding **E**ngine — A multi-phase SDLC workflow using isolated subagents to build the best context windows while staying in the smart zone. Activates on: feature requests, multi-step implementations, complex refactoring, mentions of 'spice', 'workflow', 'plan and implement', or 'research and build'."
---

# SPICE — Subagent-Powered Iterative Coding Engine

**SPICE** orchestrates the complete software development lifecycle using **isolated subagents**. Each phase runs in a fresh context via the Task tool, communicating through markdown deliverables.

## Core Philosophy

1. **Build the best context windows** — Stay in the smart zone (~40% utilization)
2. **Subagent isolation** — Prevent context pollution between phases
3. **Knowledge compaction** — Share context via structured markdown deliverables
4. **Iterate and validate** — Each step is tested before proceeding

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR (Main Context)                          │
│             Reads deliverables, spawns subagents, reports progress           │
│                          Does NOT do actual work                             │
└────────┬──────────────┬──────────────┬──────────────┬──────────────┬────────┘
         │              │              │              │              │
   ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
   │ IDEATE    │  │ RESEARCH  │  │ PLAN      │  │ IMPLEMENT │  │ IMPLEMENT │
   │ Subagent  │  │ Subagent  │  │ Subagent  │  │ Task 1.x  │  │ Task 2.x  │
   │           │  │           │  │           │  │           │  │           │
   │ Fresh ctx │  │ Fresh ctx │  │ Fresh ctx │  │ Fresh ctx │  │ Fresh ctx │
   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
      prd.md      research.md      plan.md     progress.md    progress.md
```

---

## SDLC Phases

| Phase | Command | Subagent | Deliverable | Purpose |
|-------|---------|----------|-------------|---------|
| **Ideation** | `/spice:ideate` | `spice-ideator` | `prd-{nnn}.md` | Flesh out ideas into PRD |
| **Research** | `/spice:research` | `spice-researcher` | `research-{nnn}.md` | Explore codebase, gather context |
| **Design** | `/spice:design` | `spice-designer` | `tdd-{nnn}.md` | Technical architecture & contracts |
| **Planning** | `/spice:plan` | `spice-planner` | `plan-{nnn}.md` | Create TDD task breakdown |
| **Execute** | `/spice:execute` | `spice-implementer` | `progress-{nnn}.md` | Implement one task |
| **Iterate** | `/spice:iterate` | Multiple | `progress-{nnn}.md` | Implement all tasks |
| **Workflow** | `/spice:workflow` | All phases | All deliverables | End-to-end pipeline |

### Phase Variants

| Variant | Command | Difference |
|---------|---------|------------|
| Research (online) | `/spice:research` | Web search enabled |
| Research (offline) | `/spice:research-offline` | No web search, codebase only |
| Planning (with TDD) | `/spice:plan [prd] [tdd]` | Uses technical design |
| Planning (without TDD) | `/spice:plan [prd] [research]` | Skips design phase |

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

### Deliverable Versioning

When iterating on a deliverable, increment the number:
- `prd-001.md` → `prd-002.md` (refined PRD)
- `plan-001.md` → `plan-002.md` (revised plan)

---

## Critical: Subagent Isolation

**NEVER do phase work in the main context.** Always spawn subagents:

```
✅ CORRECT:
   Use Task tool: "You are a SPICE researcher..."
   → Subagent explores in isolated 200K context
   → Returns summary, writes deliverable
   → Main context stays lean

❌ WRONG:
   Read codebase files directly in main context
   → Context bloat from exploration
   → Pollution between phases
```

### Why This Matters

| Approach | Context After 3 Phases | Risk |
|----------|------------------------|------|
| Direct work | ~150K tokens (bloated) | Degraded quality |
| Subagent isolation | ~10K tokens (lean) | Optimal performance |

Each subagent gets a **fresh 200K context** — exploration doesn't accumulate.

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

Language-specific conventions loaded dynamically:
- [languages/python.md](languages/python.md) — Python patterns, types, testing
- [languages/typescript.md](languages/typescript.md) — TypeScript patterns, types, testing
- [languages/go.md](languages/go.md) — Go patterns, idioms, testing

### External Skills

SPICE integrates with skills in your `.claude/skills/` directory:
- **`test-driven-development`** — TDD cycle, test structure, anti-patterns (required)

### Dynamic Loading

Skills are loaded **per-task**, not globally:

```markdown
### Task 2.1: Implement validation
**Skills**: spice/languages/python, test-driven-development
```

The implementer loads only:
1. `.claude/skills/spice/languages/python.md`
2. `.claude/skills/test-driven-development/SKILL.md`

This keeps each subagent's context focused.

---

## When to Use SPICE

### ✅ Use SPICE For:
- New features requiring upfront research
- Multi-file implementations
- Complex refactoring with planning
- Features spanning multiple languages
- Work benefiting from context isolation

### ❌ Skip SPICE For:
- Quick single-file changes
- Simple bug fixes (use TDD directly)
- Pure configuration changes
- Documentation-only updates

---

## Quick Start

```bash
# Full workflow from an idea
/spice:workflow user-auth "Users can log in with email and password"

# Or run phases separately
/spice:ideate "notification system for user events"
/spice:research "payment processing" /context/001-payments/
/spice:design /context/001-payments/prd-001.md /context/001-payments/research-001.md
/spice:plan /context/001-payments/prd-001.md /context/001-payments/tdd-001.md
/spice:iterate /context/001-payments/

# Research without web search
/spice:research-offline /context/001-payments/

# Skip design phase (plan directly from research)
/spice:plan /context/001-payments/prd-001.md /context/001-payments/research-001.md
```

---

## Hooks (Optional Validation)

SPICE supports optional hooks for deterministic validation:

```
.claude/hooks/
└── spice-post-task.sh    # Runs after each task completes
```

### Hook Contract

Post-task hooks receive:
- `$1` — Context folder path
- `$2` — Task number completed
- `$3` — Exit code from tests (0 = pass)

Hooks can:
- Run additional linting
- Trigger deployment previews
- Update external systems

See [Hooks Configuration](#hooks-configuration) for setup.

---

## Commit Protocol

When all subtasks of a parent task are complete:

```bash
# 1. Run full test suite
npm test  # or: pytest / go test ./...

# 2. Stage changes (only if tests pass)
git add .

# 3. Remove temp files and debug code

# 4. Commit with conventional message
git commit -m "feat: {parent task title}" \
  -m "- {subtask 1 summary}" \
  -m "- {subtask 2 summary}"
```

---

## Core Principles

### 1. Context Efficiency
Stay in the smart zone (~40% context utilization). If approaching limits, spawn a subagent.

### 2. Knowledge Compaction
Each phase produces a markdown deliverable that captures essential findings. The next phase reads this instead of re-exploring.

### 3. TDD Discipline
Implementation follows strict RED → GREEN → REFACTOR. Tests must fail before implementation, pass after.

### 4. Fail Fast
Explicit errors over silent failures. No unnecessary error handling.

### 5. Simplicity First
Prefer simple solutions over clever ones. Build what's needed now.

---

## Troubleshooting

### Task Fails Repeatedly
1. Check the progress file for error details
2. Spawn a fresh subagent with `/spice:execute` (clean context)
3. Consider breaking the task into smaller pieces

### Research Misses Key Files
1. Review search patterns in research file
2. Re-run with explicit file hints
3. Check that file extensions are recognized

### Plan Tasks Are Too Large
1. Break parent tasks into more subtasks
2. Each subtask should be one RED/GREEN cycle
3. Target 15-30 minutes per subtask
