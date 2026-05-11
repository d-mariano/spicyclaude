# CLAUDE.md

## Principles

- Delete more than you add — complexity compounds into disasters
- Follow SOLID and KISS
- Fail fast and loud, not silently
- Code for an MVP at a rapidly iterating startup, not an enterprise
- Don't post-rationalize ignoring linting and typing rules
- No backwards compatibility unless explicitly requested
- One class per file
- Add docblocks to public functions and classes, avoid inline comments

## Commit Protocol

Use conventional commits:

```bash
git commit -m "feat: {description}" \
  -m "- {change 1}" \
  -m "- {change 2}"
```

Types: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
