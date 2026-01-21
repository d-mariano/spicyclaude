---
name: spice
description: Subagent-Powered Iterative Coding Engine. Use for structured feature development with research → planning → implementation phases. Activates on requests for new features, multi-step implementations, complex refactoring, or when user mentions "spice", "workflow", "plan and implement", or "research and build".
---

# SPICE — Subagent-Powered Iterative Coding Engine

**SPICE** orchestrates multi-phase software development using **isolated subagents**. Each phase and each task runs in a fresh context via the Task tool, communicating via markdown deliverables.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Main Context)                          │
│         Reads plans, spawns subagents, reports progress                 │
│                    Does NOT do actual work                              │
└───────────────┬─────────────────┬─────────────────┬─────────────────────┘
                │                 │                 │
          ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐
          │   Task    │     │   Task    │     │   Task    │
          │   Tool    │     │   Tool    │     │   Tool    │  (per task)
          └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
                │                 │                 │
          ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐
          │ RESEARCH  │     │ PLANNER   │     │IMPLEMENTER│
          │ Subagent  │     │ Subagent  │     │ Subagent  │
          │ (200K)    │     │ (200K)    │     │ (200K)    │
          └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
                │                 │                 │
                ▼                 ▼                 ▼
          research.md        plan.md          progress.md
```

## Critical: Use Task Tool for Subagents

**NEVER do phase work in the main context.** Always spawn subagents:

```
✅ CORRECT:
   Use Task tool with prompt: "You are a SPICE researcher..."
   → Subagent does work in isolated context
   → Returns summary to orchestrator

❌ WRONG:
   Read codebase files directly in main context
   → Context bloat
   → Pollution between phases
```

## When to Use SPICE

### Use SPICE For:
- New feature implementation (multi-file, multi-step)
- Work requiring upfront research or exploration
- Complex refactoring with planning phase
- Features spanning multiple languages or domains
- Anything benefiting from context isolation between phases

### Skip SPICE For:
- Quick single-file changes
- Simple bug fixes (use TDD directly)
- Pure configuration changes
- Documentation-only updates

## Commands

| Command | Purpose |
|---------|---------|
| `/spice:workflow [name] [desc]` | Full lifecycle: research → plan → implement |
| `/spice:research [topic] [folder]` | Research phase only |
| `/spice:plan [prd] [research]` | Planning phase only |
| `/spice:execute [plan] [task?]` | Implement single task |
| `/spice:iterate [folder]` | Execute all remaining tasks |

## Context Structure

All phases communicate via markdown files in `/context/`:

```
/context/
└── {nnn}-{feature}/
    ├── prd.md              # Product requirements (input or generated)
    ├── research-001.md     # Technical findings
    ├── plan-001.md         # TDD task breakdown
    └── progress-001.md     # Implementation status
```

---

## Phase 1: Research (Subagent)

**Spawn via Task tool.** See [researcher.md](researcher.md) for subagent instructions.

```
Task tool prompt:

"You are a SPICE researcher subagent.
Read instructions: .claude/skills/spice/researcher.md
Context folder: /context/{nnn}-{feature}/
Topic: {topic}

1. Explore codebase for patterns
2. Research external docs if needed
3. Detect which skills apply
4. Write to: /context/{nnn}-{feature}/research-001.md

Include a Skills Detected section."
```

**Output**: `research-{nnn}.md` with **Skills Detected** section

---

## Phase 2: Planning (Subagent)

**Spawn via Task tool.** See [planner.md](planner.md) for subagent instructions.

```
Task tool prompt:

"You are a SPICE planner subagent.
Read instructions: .claude/skills/spice/planner.md
PRD: /context/{nnn}-{feature}/prd.md
Research: /context/{nnn}-{feature}/research-001.md

1. Break work into TDD tasks
2. Assign **Skills:** field to EVERY task
3. Define RED/GREEN phases
4. Write to: /context/{nnn}-{feature}/plan-001.md"
```

**Output**: `plan-{nnn}.md` with tasks like:

```markdown
### Task 2.1: Implement email validation

**Skills**: spice/python, test-driven-development
**Files**: src/validators/email.py, tests/test_email.py

#### RED: Write failing tests
- `test_rejects_invalid_email_format`

#### GREEN: Implement validation
- Create `validate_email()` function
```

---

## Phase 3: Implementation (Subagent Per Task)

**Spawn a NEW subagent via Task tool for EACH task.** See [implementer.md](implementer.md).

```
For EACH task in plan:

    Task tool prompt:
    
    "You are a SPICE implementer subagent for ONE task.
    Read instructions: .claude/skills/spice/implementer.md
    
    Task: 2.1
    Skills to load: spice/python, test-driven-development
    
    1. Load ONLY the skills listed above
    2. RED: Write tests, verify they fail
    3. GREEN: Minimal code, verify tests pass
    4. Update progress, mark task [x]
    
    Return: test count, files modified"
```

**Each task gets fresh 200K context** — no accumulated state from previous tasks.

---

## Dynamic Skill System

### Available Language Skills

| Skill | File | Use When |
|-------|------|----------|
| `spice/python` | [python.md](python.md) | Python files (`.py`) |
| `spice/typescript` | [typescript.md](typescript.md) | TypeScript/JS files (`.ts`, `.tsx`, `.js`) |
| `spice/go` | [go.md](go.md) | Go files (`.go`) |

### External Skills

SPICE integrates with other skills in your `.claude/skills/` directory:

- **`test-driven-development`** — Always loaded for implementation tasks. Provides TDD cycle, test structure, anti-patterns.

### How Loading Works

1. **Researcher** detects languages from codebase and documents in research
2. **Planner** assigns `**Skills**:` field to each task
3. **Implementer** loads only the skills listed for the current task

This keeps subagent context focused and efficient.

### Fallback Detection

If a task lacks a `**Skills**:` field, detect from file extensions:
- `.py` → `spice/python`
- `.ts`, `.tsx`, `.js`, `.jsx` → `spice/typescript`
- `.go` → `spice/go`
- Always include `test-driven-development`

---

## Core Principles

### 1. Subagent Isolation (Most Important)

**Every phase and every task runs in a fresh subagent.** The orchestrator:
- Reads plan metadata
- Spawns subagents via Task tool
- Reports progress
- **Does NOT do actual implementation work**

Why this matters:
- Each subagent gets fresh 200K context
- No pollution from exploration in research phase
- Failed tasks can be retried with clean slate
- Focused context = better results

### 2. Skill Composition
SPICE provides **language conventions**. TDD enforcement comes from the `test-driven-development` skill. They compose per-task.

### 3. Fail Fast
- Explicit errors over silent failures
- No unnecessary error handling
- Let exceptions propagate unless meaningfully handled

### 4. Simplicity First
- Prefer simple solutions over clever ones
- Avoid premature abstraction
- Build what's needed now

---

## Commit Protocol

When all subtasks of a parent task are complete:

```bash
# 1. Run full test suite
npm test  # or pytest / go test ./...

# 2. Stage changes
git add .

# 3. Commit with conventional message
git commit -m "feat: {parent task title}" \
  -m "- {subtask 1 summary}" \
  -m "- {subtask 2 summary}"
```

Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`

---

## Quick Start

```bash
# Full workflow from idea
/spice:workflow user-auth "Users can log in with email/password"

# Or run phases separately
/spice:research "payment processing" /context/001-payments/
/spice:plan /context/001-payments/prd.md /context/001-payments/research-001.md
/spice:iterate /context/001-payments/
```
