## Test Case Discovery: Coverage-Driven

After implementing a feature with TDD, **validate completeness with coverage analysis**.

### Post-Implementation Coverage Check

After GREEN phase passes:

```bash
# Python
pytest --cov=<module> --cov-report=term-missing

# TypeScript/JavaScript
npm test -- --coverage

# Go
go test -cover -coverprofile=coverage.out ./...
go tool cover -func=coverage.out
```

### Analyzing Uncovered Lines

For each uncovered line, ask:

1. **What condition reaches this line?** — Identify the input/state that triggers it
2. **Is this a valid code path?** — If unreachable, delete the dead code
3. **What test case is missing?** — Write a test that exercises this path

### Common Gap Patterns

When coverage reveals missed lines in authorization/access control code:

| Uncovered Pattern | Likely Missing Test |
|-------------------|---------------------|
| Secondary `raise` after null check | Cross-boundary access (resource exists but wrong owner) |
| `else` branch in permission check | User with partial permissions |
| Error path after validation | Invalid input that passes type checking |
| Fallback/default case | Edge case input value |

### The Cross-Boundary Test

If you see uncovered lines like:

```python
if resource.org_id != user.org_id:
    raise NotFoundError(...)  # ← UNCOVERED
```

You're missing the test where a **resource exists but belongs to a different owner**. This is the most commonly missed security test.

### Coverage Target

Aim for 100% on business logic and security boundaries. Accept lower coverage only for:
- Framework boilerplate
- Defensive code for truly impossible states
- Third-party integration error paths that can't be easily simulated
