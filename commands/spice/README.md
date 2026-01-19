# SPICE

**S**ubagent **P**owered for **I**terative **C**oding **E**cosystem

A Claude Code skill for multi-phase software development using isolated subagents and dynamic skill loading.

## Philosophy

SPICE is built on four core principles:

1. **Build the best context windows** — Stay in the smart zone (~40% utilization)
2. **Subagent isolation** — Prevent context pollution between phases
3. **Knowledge compaction** — Share context via structured markdown deliverables
4. **Iterate and validate** — Each step is tested before proceeding

## Installation

Copy the `.claude/` directory to your project or home directory:

```bash
# Project-specific
cp -r .claude/ /path/to/your/project/

# Global installation
cp -r .claude/ ~/.claude/
```

### Requirements

SPICE requires the **`test-driven-development`** skill:

```
.claude/skills/
├── spice/                      # This skill
└── test-driven-development/    # TDD skill (required)
    ├── SKILL.md
    ├── red-green-refactor.md
    ├── first-principles.md
    └── ...
```

## Quick Start

```bash
# Full workflow from an idea
/spice:workflow user-auth "Users can log in with email and password"

# Or run phases individually
/spice:ideate "notification system for user events"
/spice:research "payment processing" /context/001-payments/
/spice:plan /context/001-payments/prd-001.md /context/001-payments/research-001.md
/spice:iterate /context/001-payments/
```

## Commands

| Command | Purpose |
|---------|---------|
| `/spice:ideate [idea]` | Generate PRD from an idea |
| `/spice:research [topic] [folder?]` | Research with web search |
| `/spice:research-offline [topic] [folder?]` | Research codebase only |
| `/spice:design [prd] [research]` | Create technical design document |
| `/spice:plan [prd] [tdd-or-research]` | Create TDD task breakdown |
| `/spice:execute [plan] [task?]` | Implement single task |
| `/spice:iterate [folder]` | Implement all remaining tasks |
| `/spice:workflow [name] [input]` | Full pipeline |

## How It Works

### Isolated Subagents

SPICE spawns **fresh subagents** for each phase and each task:

```
Main Context (Orchestrator)
     │
     ├──► Task tool ──► [Ideator Subagent]     ──► prd.md
     │
     ├──► Task tool ──► [Researcher Subagent]  ──► research.md
     │
     ├──► Task tool ──► [Planner Subagent]     ──► plan.md
     │
     ├──► Task tool ──► [Implementer: Task 1]  ──► progress.md
     │
     └──► Task tool ──► [Implementer: Task 2]  ──► progress.md
```

**Why this matters:**
- Each subagent gets fresh 200K context
- No pollution from exploration phases
- Failed tasks can retry with clean slate
- Focused context = better results

### Context Sharing

All phases communicate via markdown in `/context/`:

```
/context/
└── 001-user-auth/
    ├── prd-001.md          # Product requirements
    ├── research-001.md     # Technical findings (skills detected)
    ├── tdd-001.md          # Technical design (architecture, contracts)
    ├── plan-001.md         # TDD task breakdown (skills per task)
    └── progress-001.md     # Implementation status
```

### Dynamic Skill Loading

Skills are loaded **per-task**, not globally:

```markdown
### Task 2.1: Implement validation
**Skills**: spice/languages/python, test-driven-development
```

The implementer loads only:
- `.claude/skills/spice/languages/python.md`
- `.claude/skills/test-driven-development/SKILL.md`

## Directory Structure

```
.claude/
├── skills/spice/
│   ├── SKILL.md              # Main entry point
│   ├── phases/
│   │   ├── ideate.md         # PRD generation protocol
│   │   ├── research.md       # Research protocol
│   │   ├── design.md         # Technical design protocol
│   │   ├── plan.md           # Planning protocol
│   │   └── execute.md        # Implementation protocol
│   └── languages/
│       ├── python.md         # Python conventions
│       ├── typescript.md     # TypeScript conventions
│       └── go.md             # Go conventions
│
├── agents/spice/
│   ├── ideator.md            # PRD generation agent
│   ├── researcher.md         # Research agent (online)
│   ├── researcher-offline.md # Research agent (no web)
│   ├── designer.md           # Technical design agent
│   ├── planner.md            # Planning agent
│   └── implementer.md        # Implementation agent
│
├── commands/spice/
│   ├── ideate.md             # /spice:ideate
│   ├── research.md           # /spice:research
│   ├── research-offline.md   # /spice:research-offline
│   ├── design.md             # /spice:design
│   ├── plan.md               # /spice:plan
│   ├── execute.md            # /spice:execute
│   ├── iterate.md            # /spice:iterate
│   └── workflow.md           # /spice:workflow
│
└── hooks/
    └── spice-post-task.sh    # Optional validation hook
```

## Phases

### 1. Ideation (`/spice:ideate`)

Transforms ideas into structured PRDs through interactive conversation.

- Asks clarifying questions
- Generates comprehensive PRD
- Iterates based on feedback

### 2. Research (`/spice:research` / `/spice:research-offline`)

Explores codebase and gathers context.

- Detects languages and skills needed
- Finds existing patterns
- Researches external documentation (online mode)
- Identifies third-party capabilities

### 3. Design (`/spice:design`)

Creates technical design document (TDD) from PRD and research.

- Defines system architecture
- Designs data models and schemas
- Specifies API contracts
- Documents technical decisions
- Defines interfaces and protocols

### 4. Planning (`/spice:plan`)

Creates TDD task breakdown.

- Breaks work into testable increments
- Assigns skills to each task
- Defines RED/GREEN phases
- Orders by dependencies
- Uses TDD contracts for test expectations

### 5. Implementation (`/spice:execute` / `/spice:iterate`)

Executes tasks with strict TDD.

- Fresh subagent per task
- RED → GREEN → REFACTOR cycle
- Updates progress after each task
- Commits when parent tasks complete

## Language Skills

| Skill | Purpose |
|-------|---------|
| `spice/languages/python` | Python patterns, types, pytest |
| `spice/languages/typescript` | TypeScript patterns, types, vitest/jest |
| `spice/languages/go` | Go patterns, idioms, testing |

## Hooks (Optional)

SPICE supports post-task hooks for deterministic validation:

```bash
# Make hook executable
chmod +x .claude/hooks/spice-post-task.sh
```

The hook receives:
- `$1` — Context folder path
- `$2` — Task number completed
- `$3` — Test exit code

## When to Use SPICE

### ✅ Use SPICE For:
- New features requiring upfront research
- Multi-file implementations
- Complex refactoring with planning
- Features spanning multiple languages

### ❌ Skip SPICE For:
- Quick single-file changes
- Simple bug fixes
- Pure configuration changes
- Documentation-only updates

## Troubleshooting

### Task Fails Repeatedly
1. Review progress file for errors
2. Retry with fresh context: `/spice:execute [plan] [task]`
3. Break task into smaller pieces

### Research Misses Key Files
1. Run with explicit topic
2. Try offline mode for codebase focus
3. Check file extensions are recognized

### Plan Tasks Too Large
1. Each subtask should be one RED/GREEN cycle
2. Target 15-30 minutes per subtask
3. Break parent tasks into more subtasks

## License

MIT
