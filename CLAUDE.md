# CLAUDE.md

Project configuration for Claude Code with SPICE integration.

## Core Philosophy

- Delete more than you add — complexity compounds into disasters
- Follow SOLID principles (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
- Follow KISS (Keep It Simple, Stupid)
- Assume an MVP of a rapidly iterating startup, not an enterprise
- Be pragmatic — don't follow patterns for their own sake
- Fail fast and loud, not silently
- Do not add granular comments to self-explanatory code

## Development Lifecycle

### Default: Use SPICE

For new features and complex changes, use the SPICE workflow:

```bash
/spice:workflow [feature-name] [description]
```

This ensures:
- Research before implementation
- TDD task breakdown
- Context isolation between phases
- Proper validation at each step

### Quick Changes

For simple changes that don't need SPICE:
- Plan → Validate → Execute → Validate → Repeat
- Use Test Driven Development
- Validate both RED and GREEN phases

## Validation

### Every Code Change

After writing any code:
1. Lint: `ruff check .` / `eslint .` / `golangci-lint run`
2. Type check: `mypy src/` / `tsc --noEmit` / `go vet`
3. Test: `pytest` / `npm test` / `go test ./...`

### TDD Requirements

- RED Phase: Write tests first, validate they fail as expected
- GREEN Phase: Implement minimum code, validate tests pass
- REFACTOR Phase: Improve while keeping tests green

### Test Quality

- Test public interfaces and core business logic
- Avoid testing implementation details
- Use fixtures for large expected outputs
- Delete redundant test code
- Use correct types for mocks

## Implementation

### Code Quality

- Delete more code than you add (unused imports, dead code)
- No backwards compatibility unless explicitly requested
- Use SOLID but don't over-engineer abstractions
- One class per file
- Avoid unnecessary try/catch
- Add docblocks to functions and classes
- Check for existing third-party types before creating new ones

### Simplification

When refactoring, treat the new version as if it has no knowledge of the previous one.

## SPICE Context Structure

All SPICE artifacts go in `/context/`:

```
/context/
└── {nnn}-{feature}/
    ├── prd-001.md          # Product requirements
    ├── research-001.md     # Technical findings
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
