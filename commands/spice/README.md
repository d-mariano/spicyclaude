# SPICE

**S**ubagent-**P**owered **I**terative **C**oding **E**ngine

A Claude Code skill for multi-phase software development with optimal context management.

## Philosophy

SPICE is built on four core principles:

1. **Build the best context windows** — Stay in the smart zone (~45% utilization)
2. **Subagents for exploration** — Research/planning noise doesn't pollute implementation
3. **Main context for implementation** — Skills load properly, progressive disclosure works
4. **Knowledge compaction** — All state in markdown, safe to `/clear` and resume

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

# After planning completes, clear context and implement
/clear
/spice:iterate /context/001-user-auth/

# When prompted, clear and continue
/clear
/spice:iterate /context/001-user-auth/
```

## Commands

| Command | Purpose |
|---------|---------|
| `/spice:ideate [idea]` | Generate PRD from an idea |
| `/spice:research [prd-path]` | Research with web search |
| `/spice:research-offline [prd-path]` | Research codebase only |
| `/spice:design [prd] [research]` | Create technical design document |
| `/spice:plan [prd] [tdd-or-research]` | Create TDD task breakdown |
| `/spice:status [folder]` | Show progress, suggest next action |
| `/spice:implement [folder] [task?]` | Implement one parent task |
| `/spice:iterate [folder]` | Implement all tasks with /clear prompts |
| `/spice:workflow [name] [input]` | Full pipeline |

## How It Works

### Two-Phase Architecture

```
EXPLORATION (Subagents)                      IMPLEMENTATION (Main Context)
───────────────────────                      ────────────────────────────

┌────────┐  ┌────────┐  ┌────────┐          ┌──────────────────────────┐
│ IDEATE │─►│RESEARCH│─►│ DESIGN │          │     /clear               │
└───┬────┘  └───┬────┘  └───┬────┘          │         ↓                │
    │           │           │               │  Task 1.0 (main ctx)     │
    ▼           ▼           ▼               │         ↓                │
 prd.md    research.md   tdd.md             │     /clear               │
                            │               │         ↓                │
                            ▼               │  Task 2.0 (main ctx)     │
                     ┌──────────┐           │         ↓                │
                     │   PLAN   │ ────────► │     ...                  │
                     └────┬─────┘   /clear  └──────────────────────────┘
                          │
                          ▼
                      plan.md
```

**Why this matters:**
- Subagents handle exploration → clean markdown output
- Main context handles implementation → skills work properly
- `/clear` between tasks keeps context fresh
- All state in markdown → safe to clear anytime

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

Skills are loaded **per-task** during implementation:

```markdown
- [ ] **2.0 UserService**
  - **Skills**: python-developer, test-driven-development
```

Because implementation runs in **main context**, skills load properly with progressive disclosure.

### Minimal Agent Pattern

Agents are thin wrappers that reference skills:

```yaml
---
name: spice-designer
model: opus
description: SPICE designer — creates technical design documents
tools: Read, Grep, Glob, Write, WebSearch, WebFetch
skills:
  - spice
---

Load and follow: `.claude/skills/spice/phases/design.md`
```

### Minimal Command Pattern

Commands are orchestration only — spawn agent or reference skill:

```yaml
---
allowed-tools: Task, Read, Glob
argument-hint: [prd-path] [research-path]
description: SPICE design — create Technical Design Document
---

# SPICE Design

1. Verify inputs exist
2. Spawn `spice-designer` agent with PRD + Research paths
3. After completion, suggest next command
```

All protocol details live in skills, not in commands or agents.

## Directory Structure

```
.claude/
├── skills/spice/
│   ├── SKILL.md              # Main entry point
│   ├── phases/               # Full protocols (source of truth)
│   │   ├── ideate.md         # PRD generation protocol
│   │   ├── research.md       # Research protocol
│   │   ├── design.md         # Technical design protocol
│   │   ├── plan.md           # Planning protocol
│   │   └── execute.md        # Implementation protocol
│   └── languages/            # Language conventions (loaded per-task)
│       ├── python.md
│       ├── typescript.md
│       └── go.md
│
├── agents/spice/             # Minimal configs → reference skills
│   ├── ideator.md
│   ├── researcher.md
│   ├── researcher-offline.md
│   ├── designer.md
│   └── planner.md
│
├── commands/spice/           # User-facing slash commands
│   ├── ideate.md
│   ├── research.md
│   ├── research-offline.md
│   ├── design.md
│   ├── plan.md
│   ├── status.md
│   ├── implement.md
│   ├── iterate.md
│   └── workflow.md
│
└── hooks/
    └── spice-post-task.sh    # Optional validation hook
```

### Component Roles

| Component | Purpose | Size |
|-----------|---------|------|
| **Skills** | Full protocols, templates, examples | 200-500 lines |
| **Agents** | YAML config + skill reference | 6-10 lines |
| **Commands** | User trigger, spawn agent or load skill | 30-65 lines |

Skills are the **single source of truth**. Agents and commands are minimal orchestration.

## Phases

### 1. Ideation (`/spice:ideate`)

Transforms ideas into structured PRDs through interactive conversation.

### 2. Research (`/spice:research` / `/spice:research-offline`)

Explores codebase and gathers context. Outputs clean markdown.

### 3. Design (`/spice:design`)

Creates technical design document (TDD) with architecture, data models, API contracts.

### 4. Planning (`/spice:plan`)

Creates TDD task breakdown with skills per task.

### 5. Implementation (`/spice:implement` / `/spice:iterate`)

Executes tasks with strict TDD **in main context**:
- Skills load properly
- `/clear` between tasks keeps context fresh
- All state in markdown for safe resume

## Typical Session

```bash
# 1. Plan the feature (subagents handle this)
/spice:workflow user-auth "email/password authentication"

# 2. After planning completes, clear context
/clear

# 3. Start implementation
/spice:iterate /context/001-user-auth/

# 4. When prompted (~45% context), clear and continue
/clear
/spice:iterate /context/001-user-auth/

# 5. Repeat until complete
```

## Language Skills

| Skill | Purpose |
|-------|---------|
| `python-developer` | Python patterns, types, pytest |
| `spice/languages/typescript` | TypeScript patterns, types, vitest/jest |
| `spice/languages/go` | Go patterns, idioms, testing |

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

### Context Growing Too Fast
1. Check `/spice:status` for current usage
2. Use `/clear` more frequently
3. Implement smaller parent tasks

### Task Fails Repeatedly
1. Review progress file for errors
2. Run `/clear` and retry: `/spice:implement [folder] [task]`
3. Break task into smaller pieces

### Skills Not Loading
Skills require main context — this is why implementation doesn't use subagents.

### Lost Track of Progress
Run `/spice:status /context/folder/` — shows current state and next action.

## License

MIT
