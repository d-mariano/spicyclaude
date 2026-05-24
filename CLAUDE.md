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

Prefer LSP over Grep/Read for code navigation — it's faster, precise, and avoids reading entire files:
- `workspaceSymbol` to find where something is defined
- `findReferences` to see all usages across the codebase
- `goToDefinition` / `goToImplementation` to jump to source
- `hover` for type info without reading the file

Use Grep only when LSP isn't available or for text/pattern searches (comments, strings, config).

After writing or editing code, check LSP diagnostics and fix errors before proceeding.

## Commit Protocol

Use conventional commits:

```bash
git commit -m "feat: {description}" \
  -m "- {change 1}" \
  -m "- {change 2}"
```

Types: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
