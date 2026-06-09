# CLAUDE.md

## Principles

- Delete more than you add — complexity compounds into disasters
- Follow SOLID and KISS
- Fail fast and loud, not silently
- Code for an MVP at a rapidly iterating startup, not an enterprise
- No backwards compatibility unless explicitly requested
- One class per file
- Add docblocks to public functions and classes, avoid inline comments
- Don't post-rationalize ignoring linting and typing rules


## Code Intelligence

Prefer LSP (`workspaceSymbol`, `findReferences`, `goToDefinition`, `hover`) over Grep/Read for code navigation — faster, precise, no full-file reads. Use Grep for text/pattern searches (comments, strings, config) and when LSP isn't available.

After writing or editing code, check LSP diagnostics and fix errors before proceeding.

## Documentation

- README is a map, not a manual — link to deeper docs, don't inline entire guides
- Cut history: reversed decisions, removed features, and migration notes belong in `git log`, not docs
- Document what exists now, not what used to exist or what's planned
- Same rule applies to comments — no "we used to do X" or "previously Y was needed"
- Don't restate what readable code already says — document the non-obvious: invariants, gotchas, intentional constraints

### CLAUDE.md files

- Purpose: index, light guide, conventions — not a novel, not a textbook, not a file registry
- Describe only the **top-level structure at the current directory** (depth 0). Subdirectories get their own CLAUDE.md if they need one
- Don't enumerate every file or describe what code does — readable code speaks for itself
- Avoid brittle facts that change with normal edits (test counts, function counts, exhaustive lists). If editing code routinely forces a CLAUDE.md update, the CLAUDE.md is wrong

## Commit Protocol

Use conventional commits (`feat:`, `fix:`, `refactor:`, etc.):

```bash
git commit -m "feat: {description}" \
  -m "- {change 1}" \
  -m "- {change 2}"
```
