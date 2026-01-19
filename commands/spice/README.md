# SPICE Skill

**S**ubagent **P**owered **I**terative **C**oding **E**ngine

A Claude Code skill for structured, multi-phase software development using isolated subagents and dynamic skill loading.

## Installation

Copy the contents to your `~/.claude/` directory:

```bash
cp -r .claude/* ~/.claude/
```

## Directory Structure

```
.claude/
├── skills/
│   └── spice/
│       ├── SKILL.md           # Main skill entry point
│       ├── researcher.md      # Detailed researcher instructions
│       ├── planner.md         # Detailed planner instructions
│       ├── implementer.md     # Detailed implementer instructions
│       ├── python.md          # Language conventions
│       ├── typescript.md
│       └── go.md
│
├── agents/
│   └── spice/
│       ├── researcher.md      # Agent definition (tools: Read, Grep, Glob, WebSearch)
│       ├── planner.md         # Agent definition (tools: Read, Grep, Glob, Write)
│       └── implementer.md     # Agent definition (tools: Read, Write, Edit, Bash, etc.)
│
└── commands/
    └── spice/
        ├── workflow.md        # /spice:workflow
        ├── research.md        # /spice:research
        ├── plan.md            # /spice:plan
        ├── execute.md         # /spice:execute
        └── iterate.md         # /spice:iterate
```

### Skills vs Agents

- **Skills** (`.claude/skills/`) — Knowledge and detailed instructions that subagents read
- **Agents** (`.claude/agents/`) — Subagent definitions with tool permissions (spawned via Task tool)

The agent files are lightweight — they define allowed tools and reference the skill for detailed instructions.

## Requirements

SPICE integrates with the **`test-driven-development`** skill for TDD enforcement. Make sure you have it installed:

```
.claude/skills/
├── spice/                     # This skill
└── test-driven-development/   # TDD skill (required)
    ├── SKILL.md
    ├── red-green-refactor.md
    ├── first-principles.md
    ├── anti-patterns.md
    └── ...
```

## Usage

### Full Workflow

```bash
/spice:workflow user-auth "Users can log in with email and password"
```

This runs: Research → Planning → Implementation

### Individual Phases

```bash
# Research only
/spice:research "payment processing" /context/001-payments/

# Planning only
/spice:plan /context/001-payments/prd.md /context/001-payments/research-001.md

# Implementation
/spice:iterate /context/001-payments/
# or
/spice:execute /context/001-payments/plan-001.md 2.1
```

## How It Works

### Key Concept: Isolated Subagents via Task Tool

**SPICE spawns fresh subagents for each phase and each task.** The main context only orchestrates — it doesn't do actual work.

```
Main Context (Orchestrator)
     │
     ├──► Task tool ──► [Research Subagent] ──► research.md
     │
     ├──► Task tool ──► [Planner Subagent]  ──► plan.md
     │
     ├──► Task tool ──► [Implementer: Task 1.1] ──► Done
     │
     ├──► Task tool ──► [Implementer: Task 1.2] ──► Done
     │
     └──► ... (fresh subagent per task)
```

Why this matters:
- **No context pollution** — exploration doesn't bleed into implementation
- **No prompt bloat** — each subagent starts fresh with 200K tokens
- **Focused work** — each subagent loads only the skills it needs
- **Retry-friendly** — failed tasks get clean slate on retry

### Phase 1: Research (Subagent)

The orchestrator spawns a researcher subagent via Task tool:
1. Subagent explores the codebase
2. Researches external documentation
3. **Detects which skills apply** (languages involved)
4. Writes `research-001.md` with a **Skills Detected** section

### Phase 2: Planning (Subagent)

The orchestrator spawns a planner subagent via Task tool:
1. Subagent reads PRD and research
2. Breaks work into TDD tasks
3. **Assigns skills to each task** based on research
4. Writes `plan-001.md` with tasks like:

```markdown
### Task 2.1: Implement validation

**Skills**: spice/python, test-driven-development
**Files**: src/validators/email.py

#### RED: Write failing tests
- `test_rejects_invalid_email`

#### GREEN: Implement
- Create `validate_email()` function
```

### Phase 3: Implementation (Subagent Per Task)

The orchestrator spawns a **fresh implementer subagent for each task**:
1. Subagent reads the task
2. **Loads ONLY the skills specified** (keeps context lean)
3. Follows TDD: RED → GREEN → REFACTOR
4. Updates progress, commits when complete
5. Returns summary to orchestrator

Each task gets isolated 200K context — no accumulated state.

## Dynamic Skill Loading

SPICE loads skills per-task, not globally:

| Task Says | Skills Loaded |
|-----------|---------------|
| `**Skills**: spice/python, test-driven-development` | `python.md` + TDD skill |
| `**Skills**: spice/typescript, test-driven-development` | `typescript.md` + TDD skill |
| No Skills field | Detect from `.py`/`.ts`/`.go` extensions |

This keeps each subagent's context focused and efficient.

## Skill Composition

SPICE provides **language conventions**:
- `spice/python` — Python patterns, types, style
- `spice/typescript` — TypeScript patterns, types, style  
- `spice/go` — Go patterns, idioms, style

TDD enforcement comes from **`test-driven-development`**:
- RED/GREEN/REFACTOR cycle
- Test structure (AAA)
- Anti-patterns to avoid

They compose together per-task.

## Context Structure

All phases communicate via markdown in `/context/`:

```
/context/001-user-auth/
├── prd.md              # Requirements (input)
├── research-001.md     # Research findings
├── plan-001.md         # TDD task breakdown
└── progress-001.md     # Implementation status
```

## Auto-Activation

The SPICE skill activates on:
- Requests for new features
- Multi-step implementations
- Mentions of "spice", "workflow", "plan and implement"

Or invoke explicitly with `/spice:*` commands.

## License

MIT
