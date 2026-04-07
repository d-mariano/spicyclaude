# CLAUDE.md

Project configuration for Claude Code with SPICE integration.

## Core Philosophy

- Delete more than you add — complexity compounds into disasters
- Follow SOLID and KISS
- Assume an MVP of a rapidly iterating startup, not an enterprise
- Do NOT post-rationalize ignoring linting and typing rules
- NEVER use `# type: ignore` to suppress type errors — fix the types instead:
  - Import the correct type from the third-party library (use aliased imports to avoid name collisions, e.g. `from lib import Foo as LibFoo`)
  - If the type doesn't exist, check if the library exports a TypedDict, Protocol, or base class you should use
  - Only use `# type: ignore` as a last resort when the library's own type stubs are genuinely wrong, and add a comment explaining why
- If you come across typing errors then work backwards to determine if:
  - A greater code issue is at play, typing incompatibilities are a red flag
  - An incorrect type hint was assigned to a variable or function definition

## Development Lifecycle

### Default: Research → Plan → Execute

Most tasks: features, fixes, refactors.

```
/research [topic]  →  /planner [prd] [research]  →  /execute [plan]
```

### Design-Heavy Changes

When architecture decisions matter — new systems, complex integrations, significant refactors. Use `/design` to route to the right workflow (greenfield vs feature integration), or invoke directly:

- `/design-greenfield` — new system from scratch
- `/design-integrate` — adding to an existing codebase

### Large Features: Use SPICE

Multi-phase SDLC with subagent orchestration and `/clear` discipline. Use when the task needs ideation, research, design, planning, and iterative implementation:

```bash
/spice:workflow [feature-name] [description]
```

## Implementation

- No backwards compatibility unless explicitly requested
- One class per file
- Add docblocks to functions and classes
- Check for existing third-party types before creating new ones

## Context Structure

All workflow artifacts go in `/context/`:

```
/context/
└── {nnn}-{feature}/
    ├── prd-001.md          # Product requirements
    ├── research-001.md     # Technical findings
    ├── tdd-001.md          # Technical design (architecture, contracts)
    ├── plan-001.md         # TDD task breakdown
    └── progress-001.md     # Implementation status
```

## Commit Protocol

Use conventional commits:

```bash
git commit -m "feat: {description}" \
  -m "- {change 1}" \
  -m "- {change 2}"
```

Types: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
