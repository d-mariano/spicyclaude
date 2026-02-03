## Implementation Protocol

**Role**: Execute tasks following strict TDD discipline in main context.

**Approach**: Main context execution (no subagents) — skills load properly, progressive disclosure works, context from earlier work helps.

**Tools**: Read, Write, Edit, MultiEdit, Bash, Grep, Glob

---

### Context Management

Implementation runs in main context. Benefits:
- Skills load correctly with progressive disclosure
- Accumulated understanding from earlier work
- No cold-start overhead

Trade-off: Context grows. Manage with `/clear` between parent tasks.

**Context threshold**: ~45%
- After completing a parent task, check context usage
- If >= 45%, pause and suggest `/clear`
- All state is preserved in markdown files — safe to clear

---

### Inputs

From the context folder (`/context/{nnn}-{feature}/`):
1. **plan-*.md** — Task list with `[ ]` / `[x]` checkboxes
2. **progress-*.md** — Completion tracking
3. **research-*.md** or **tdd-*.md** — Patterns and design decisions
4. **prd-*.md** — Original requirements

---

### Task Scope

Implement ONE parent task at a time (all its subtasks):

| Task Format | What to Do |
|-------------|------------|
| `1.0`, `2.0` (parent) | Execute all subtasks 1.1, 1.2, 1.3... in sequence |

Parent task execution keeps the full TDD cycle (RED/GREEN/REFACTOR) in one context.

---

### Process

#### 1. Load Skills (Dynamic)

**Load ONLY the skills specified for this task.**

You will be told which skills:
```
Skills to load, i.e: python-development, terraform-developer, test-driven-development
```

For SPICE language skills, read:
- `spice/languages/typescript` → `~/.claude/skills/spice/languages/typescript.md`
- `spice/languages/go` → `~/.claude/skills/spice/languages/go.md`
- `python-development` → load full `python-development` skill protocol
- `terraform-development` → load full `terraform-development` skill protocol
- `frontend-development` → load full `frontend-development` skill protocol

For `test-driven-development`, load that skill's full protocol.

**Do NOT load skills that aren't specified** — keep context focused.

#### 2. Load Context

- Read the plan document
- Identify the task (parent or subtask)
- If parent task: identify all subtasks to execute
- Read research if needed for patterns

#### 3. Execute TDD Cycle

**For parent tasks (1.0, 2.0):** Execute each subtask in sequence within the same context.
**For single subtasks (1.1):** Execute just that subtask.

```
FOR EACH subtask (or single subtask if specified):
    
    1. Execute RED/GREEN/REFACTOR as appropriate
    2. Mark subtask [x] complete in plan
    3. Continue to next subtask (if parent task)
    
AFTER ALL subtasks in parent complete:
    
    1. Mark parent task [x] complete
    2. Run full test suite
    3. Commit with conventional message
```

Follow strict RED → GREEN → REFACTOR for each subtask. **No exceptions.**

---

### TDD Execution

#### RED Phase — Write Failing Tests

1. Create/open test file from plan
2. Write tests listed in the RED section
3. **Run tests — They MUST fail**
4. Verify failure is correct (not syntax/import errors)

```bash
# Python
pytest src/validators/test_email.py -v
# Expected: FAILED (function doesn't exist)
# NOT: SyntaxError or ImportError

# TypeScript
npm test -- src/validators/email.test.ts
# Expected: FAILED

# Go
go test -v ./src/validators/
# Expected: FAIL
```

**Gate Check**:
- [ ] Tests exist and run
- [ ] Tests fail for the RIGHT reason (missing implementation)
- [ ] No syntax or import errors

**DO NOT PROCEED** until tests fail correctly.

#### GREEN Phase — Minimal Implementation

1. Write minimum code to pass tests
2. No features beyond what's tested
3. No optimization yet
4. **Run tests — They MUST pass**

```bash
# Python
pytest src/validators/test_email.py -v
# Expected: All PASSED

# TypeScript
npm test -- src/validators/email.test.ts
# Expected: All passed

# Go
go test -v ./src/validators/
# Expected: PASS
```

**Gate Check**:
- [ ] All tests pass
- [ ] No unrelated tests broken
- [ ] Code does ONLY what tests require

**DO NOT PROCEED** until all tests pass.

#### REFACTOR Phase — Improve Code

Only if there's clear improvement needed:

1. Look for code smells
2. Make small improvements
3. **Run tests after EACH change**
4. If tests fail, **revert immediately**

Refactoring targets:
- Remove duplication
- Improve naming
- Extract methods (if complex)
- Add type hints (if missing)

**Gate Check**:
- [ ] All tests still pass
- [ ] Code is cleaner than before
- [ ] No functionality changed

---

### Validation Commands

Run validation after implementation:

```bash
# Python
pytest                      # Full test suite
ruff check .               # Linting
mypy src/                  # Type checking

# TypeScript
npm test                   # Full test suite
npm run lint              # ESLint
npm run typecheck         # tsc --noEmit

# Go
go test ./...             # Full test suite
golangci-lint run         # Linting
```

All must pass before marking task complete.

---

### Update Progress

After completing each subtask and the parent task:

#### 1. Mark Subtasks Complete (As You Go)

After each subtask, mark it `[x]`:

```markdown
- [ ] **1.0 UserService**
  - [x] 1.1 RED: Write failing tests  ← Done
  - [x] 1.2 GREEN: Implement          ← Done
  - [ ] 1.3 REFACTOR: Clean up        ← In progress
```

#### 2. Mark Parent Task Complete (When All Subtasks Done)

When all subtasks are `[x]`, mark the parent:

```markdown
- [x] **1.0 UserService**             ← Now complete
  - [x] 1.1 RED: Write failing tests
  - [x] 1.2 GREEN: Implement
  - [x] 1.3 REFACTOR: Clean up
```

#### 3. Update Progress File

Update `{context_folder}/progress-{nnn}.md`:

```markdown
# Progress: {Feature Name}

## Current Status

**Last Updated**: {timestamp}
**Current Task**: 1.0 UserService
**Status**: ✅ Complete

## Completed Tasks

| Task | Subtasks | Tests | Status |
|------|----------|-------|--------|
| 1.0 UserService | 1.1 ✓ 1.2 ✓ 1.3 ✓ | 8 passing | ✅ |

## Test Summary

```
========================= test session starts =========================
collected 3 items
tests/user/test_service.py ...                                    [100%]
========================= 3 passed in 0.15s ===========================
```

## Files Modified

| File | Action | Lines |
|------|--------|-------|
| `src/user/service.py` | Created | 45 |
| `tests/user/test_service.py` | Created | 62 |

## Validation

- [x] Tests pass
- [x] Linter passes
- [x] Type checker passes

## Next Task

**2.1 RED**: Tests for email validation
**Skills**: python-development, test-driven-development

## Notes

{Any issues encountered or decisions made}
```

---

### Commit Protocol

When **all subtasks** of a parent task are complete:

```bash
# 1. Run full test suite
pytest  # or: npm test / go test ./...

# 2. Only if all pass, stage changes
git add .

# 3. Remove any temp files/debug code

# 4. Commit with conventional message
git commit -m "feat: {parent task title}" \
  -m "- {subtask 1 summary}" \
  -m "- {subtask 2 summary}"
```

Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`

---

### Completion Report

After completing a parent task, report:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Task 1.0 Complete: UserService

Subtasks: 1.1 ✓, 1.2 ✓, 1.3 ✓
Tests: 8 passing
Files: 
  - src/user/service.py (created)
  - tests/user/test_service.py (created)
Validation: All checks pass
Commit: feat: implement UserService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: 1/5 parent tasks complete
Next: Task 2.0 — UserRepository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Context: ~{n}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**If context >= 45%**, add:

```
⚠️  Context threshold reached — recommend /clear before next task

All state preserved in:
- plan-001.md (task completion status)
- progress-001.md (detailed log)

After /clear, resume with:
/spice:implement {context-folder}
```

---

### Rules

#### TDD Discipline
- **NEVER skip RED phase** — Always see tests fail first
- **NEVER write code before tests** — Tests define the interface
- **ONE failing test at a time** — Small increments
- **Fix failures immediately** — Don't proceed with failing tests

#### Skill Discipline
- **Load ONLY specified skills** — Keep context lean
- **Follow loaded skills strictly** — They define conventions
- **Language skill + TDD skill** — Always both for implementation

#### Code Quality
- Minimal implementation in GREEN phase
- Refactor only when tests are green
- No speculative features
- Follow conventions from loaded language skill

---

### Handling Failures

#### Tests Won't Fail (RED Phase)

If tests pass when they shouldn't:
1. Check if implementation already exists
2. Verify test assertions are correct
3. Make test more specific

#### Tests Won't Pass (GREEN Phase)

If tests still fail after implementation:
1. Read error message carefully
2. Check test expectations match implementation
3. Verify imports and paths
4. Fix ONE issue at a time
5. Run tests after each fix

#### Stuck?

1. Take smaller steps
2. Hardcode a return value if needed (next test forces generalization)
3. Re-read the task requirements
4. Check loaded skill for patterns
5. Review similar code in codebase

---

### Capturing Lessons Learned

When unexpected failures occur, document them to improve future workflows.

**When to capture a lesson:**
- Unexpected test failure due to missing context
- Design assumption was wrong
- Research gap caused implementation issue
- Plan was missing a dependency
- Skill guidance was insufficient

**Process:**

1. **Identify root cause** — What went wrong and why?
2. **Determine improvement area** — Where should this be fixed?
3. **Document in lessons-learned.md** — Structured format below
4. **Optionally apply fix** — If simple, fix it now

**Create/append to `{context_folder}/lessons-learned.md`:**

```markdown
## Lesson: {YYYY-MM-DD HH:MM}

### What Happened
Task 2.1 (UserService.authenticate) failed unexpectedly.
Test passed but integration failed due to missing database transaction.

### Root Cause
Design (TDD) didn't specify transaction boundaries for auth operations.
Research didn't cover transaction patterns in the existing codebase.

### Impact
Lost 20 minutes debugging. Had to research transaction handling mid-implementation.

### Suggested Improvement

**Area**: Design Phase (phases/design.md)
**Type**: Template Addition
**Suggestion**: Add "Transaction Boundaries" section to TDD template

```markdown
## Transaction Boundaries

| Operation | Transaction Scope | Notes |
|-----------|------------------|-------|
| User creation | Single transaction | Rollback on validation failure |
| Authentication | Read-only | No transaction needed |
```

### Status
- [ ] Pending review
- [ ] Applied to project CLAUDE.md
- [ ] Applied to global CLAUDE.md
- [ ] Applied to SPICE skill
```

**Improvement areas:**

| Area | When to Suggest |
|------|-----------------|
| **Project CLAUDE.md** | Project-specific patterns, conventions |
| **Global CLAUDE.md** | Universal lessons, coding standards |
| **Research skill** | Missing codebase analysis, gaps |
| **Design skill** | Missing template sections, contracts |
| **Plan skill** | Task breakdown issues, dependencies |
| **Execute skill** | TDD guidance, validation steps |
| **Language skill** | Language-specific patterns |

**At end of implementation**, review lessons-learned.md and decide:
- Apply to appropriate area?
- Flag for human review?
- Defer to next iteration?

---

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Do Instead |
|--------------|---------|------------|
| Write all tests at once | Overwhelming, hard to debug | One test at a time |
| Write code before test | Loses TDD benefit | RED → GREEN → REFACTOR |
| Test private methods | Brittle tests | Test public interface |
| Skip validation | Bugs slip through | Run lint/typecheck |
| Optimize in GREEN | Over-engineering | Save for REFACTOR |

---

### Example Task Execution

```
Task: 1.2 GREEN - Implement user creation
Skills: python-development, test-driven-development

Loading skills...
- python-development ✓
- test-driven-development ✓

Reading task 1.2 from plan...

[GREEN Phase]
Tests from 1.1 are failing as expected ✓

Creating src/user/service.py...
```python
class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo
    
    def create_user(self, data: CreateUserRequest) -> User:
        if self._repo.exists_by_email(data.email):
            raise DuplicateEmailError(data.email)
        return self._repo.save(User.from_request(data))
```

Running tests...
pytest tests/user/test_service.py -v
✓ test_creates_user_with_valid_data PASSED
✓ test_rejects_duplicate_email PASSED

All tests pass ✓

Running validation...
✓ ruff check . — no issues
✓ mypy src/ — no errors

Updating progress...
Marking task [x] complete...

Task 1.2 Complete ✓
```
