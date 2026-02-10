---
allowed-tools: Read, Glob, Grep, Bash, Write
argument-hint: [context-folder]
description: SPICE review — comprehensive implementation review before completion
---

# SPICE Implementation Review

**Folder**: $1

## Purpose

Comprehensive review of completed implementation. Run this when you think implementation is done to verify:

1. ✅ All tests pass
2. ✅ Linting clean
3. ✅ Type checking passes
4. ✅ All requirements implemented
5. ✅ All components delivered
6. ✅ No forgotten items

## Process

**This runs in main context** (not a subagent) because it needs to execute tests and linting.

1. Load the review protocol:
   ```
   Read: ~/.claude/skills/spice/phases/review.md
   ```

2. Load context files:
   - `$1/prd-001.md` — Requirements
   - `$1/tdd-001.md` — Design (if exists)
   - `$1/plan-001.md` — Plan
   - `$1/progress-001.md` — What was done

3. Run automated checks:
   ```bash
   # Tests
   pytest --tb=short
   
   # Lint
   ruff check .
   
   # Types
   mypy src/
   ```

4. Verify requirements coverage

5. Verify component delivery

6. Check test coverage

7. Document open items

8. Write review to `$1/review-001.md`

## When to Use

- After completing all tasks in the plan
- Before declaring a feature "done"
- Before creating a pull request
- When handing off to QA

## Output

Creates `{folder}/review-001.md` with:
- Automated check results
- Requirements verification
- Component verification
- Test coverage
- Open items
- Final verdict

## Verdicts

| Verdict | Meaning |
|---------|---------|
| ✅ Complete | Ready for deployment |
| ⚠️ Complete with caveats | Done but with documented gaps |
| ❌ Incomplete | Needs more work |

## Examples

```bash
# After completing implementation
/spice:review /context/001-auth/

# Review will output verdict and next steps
```

## After Review

Based on verdict:
- ✅ Complete → Merge/deploy
- ⚠️ Caveats → Review caveats, decide if acceptable
- ❌ Incomplete → Continue with `/spice:iterate`
