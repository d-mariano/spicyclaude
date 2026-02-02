## Implementation Review Protocol

**Role**: Comprehensive review of completed implementation against requirements and design.

**Context**: Runs in main context after implementation is complete.

**Tools**: Read, Grep, Glob, Bash

---

### Purpose

Before declaring a feature "done", verify:
1. All requirements are implemented
2. All tests pass
3. Code quality checks pass
4. No loose ends remain

---

### Inputs

From the context folder:
- `prd-001.md` — Original requirements
- `tdd-001.md` — Technical design (if exists)
- `plan-001.md` — Implementation plan
- `progress-001.md` — What was actually done
- `lessons-learned.md` — Issues encountered (if exists)

---

### Process

#### 1. Automated Checks

Run all automated validation:

**Tests:**
```bash
# Python
pytest --tb=short

# TypeScript
npm test

# Go
go test ./...
```

**Linting:**
```bash
# Python
ruff check .

# TypeScript
npm run lint

# Go
go vet ./...
```

**Type Checking:**
```bash
# Python
mypy src/

# TypeScript
npx tsc --noEmit

# Go (built-in)
```

Document results:
```markdown
## Automated Checks

| Check | Command | Result |
|-------|---------|--------|
| Tests | `pytest` | ✅ 47 passed, 0 failed |
| Lint | `ruff check .` | ✅ No issues |
| Types | `mypy src/` | ✅ No errors |
```

#### 2. Requirements Verification

For EVERY functional requirement in the PRD:
- Is it implemented?
- Where is it implemented?
- Is it tested?

```markdown
## Requirements Verification

| Requirement | Implementation | Test | Status |
|-------------|----------------|------|--------|
| FR-01: Registration | `UserService.register()` | `test_user_registration.py` | ✅ Done |
| FR-02: Login | `UserService.authenticate()` | `test_user_login.py` | ✅ Done |
| FR-03: Password reset | - | - | ⚠️ Deferred |
```

#### 3. Component Verification

For EVERY component in the TDD:
- Is it implemented?
- Does it match the design?
- Is it tested?

```markdown
## Component Verification

| Component | Files | Test Coverage | Status |
|-----------|-------|---------------|--------|
| UserService | `src/user/service.py` | 94% | ✅ Done |
| UserRepository | `src/user/repository.py` | 88% | ✅ Done |
| PasswordHasher | - | - | ⚠️ Deferred |
```

#### 4. Test Coverage Analysis

Check test coverage metrics:

```bash
# Python
pytest --cov=src --cov-report=term-missing

# TypeScript
npm run test:coverage
```

```markdown
## Test Coverage

| Module | Coverage | Notes |
|--------|----------|-------|
| src/user/service.py | 94% | Missing: edge case in validate_email |
| src/user/repository.py | 88% | Missing: connection error handling |
| **Overall** | **91%** | |
```

#### 5. API Contract Verification

If TDD specified API contracts, verify implementation matches:

```markdown
## API Contract Verification

| Endpoint | Spec | Implementation | Status |
|----------|------|----------------|--------|
| POST /users | 201 + User | 201 + User | ✅ Match |
| POST /auth/login | 200 + Token | 200 + Token | ✅ Match |
| Error responses | 4xx + ErrorResponse | 4xx + ErrorResponse | ✅ Match |
```

#### 6. Plan Completion Check

Verify all tasks are marked complete:

```markdown
## Plan Completion

| Task | Status |
|------|--------|
| 1.0 UserService | ✅ Complete |
| 2.0 UserRepository | ✅ Complete |
| 3.0 Integration | ✅ Complete |

**All planned tasks complete.**
```

#### 7. Open Items

Identify any remaining work:

```markdown
## Open Items

### Deferred (Intentional)
- FR-03: Password reset — deferred to Phase 2
- PasswordHasher component — deferred to Phase 2

### Technical Debt
- TODO in `service.py:45` — needs refactoring
- Missing error handling in repository

### Documentation
- [ ] API documentation not updated
- [ ] README needs new setup instructions
```

#### 8. Lessons Learned Summary

If `lessons-learned.md` exists, summarize:

```markdown
## Lessons Learned

| Issue | Impact | Improvement Suggested |
|-------|--------|----------------------|
| Missing transaction boundaries | 20 min debugging | Add to TDD template |
| Unclear test naming | Confusion during review | Update TDD skill |

See `lessons-learned.md` for details.
```

---

### Output Format

Write to `{context_folder}/review-001.md`:

```markdown
# Implementation Review: {Feature Name}

**Date**: {YYYY-MM-DD}
**PRD**: {prd path}
**Plan**: {plan path}

## Summary

{2-3 sentence summary of implementation status}

**Verdict**: ✅ Complete / ⚠️ Complete with caveats / ❌ Incomplete

---

## Automated Checks

| Check | Command | Result |
|-------|---------|--------|
| Tests | `pytest` | ✅ 47 passed |
| Lint | `ruff check .` | ✅ No issues |
| Types | `mypy src/` | ✅ No errors |

---

## Requirements Verification

| Requirement | Implementation | Test | Status |
|-------------|----------------|------|--------|
| FR-01 | `UserService.register()` | `test_registration.py` | ✅ Done |
| FR-02 | `UserService.authenticate()` | `test_login.py` | ✅ Done |
| FR-03 | - | - | ⚠️ Deferred |

**Coverage**: 2/3 requirements (67%) — 1 intentionally deferred

---

## Component Verification

| Component | Files | Coverage | Status |
|-----------|-------|----------|--------|
| UserService | `src/user/service.py` | 94% | ✅ Done |
| UserRepository | `src/user/repository.py` | 88% | ✅ Done |

---

## Test Coverage

**Overall**: 91%

| Module | Coverage |
|--------|----------|
| src/user/service.py | 94% |
| src/user/repository.py | 88% |

---

## Plan Completion

All 3 planned tasks complete (100%).

---

## Open Items

### Deferred (Intentional)
- FR-03: Password reset (Phase 2)

### Technical Debt
- None identified

### Documentation
- [x] API docs updated
- [x] README updated

---

## Conclusion

Implementation is **complete** and ready for deployment.

All automated checks pass, requirements are verified, and deferred items are documented.
```

---

### Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| ✅ Complete | All requirements met, all checks pass | Ready for deployment |
| ⚠️ Complete with caveats | Done but with documented gaps/debt | Deploy with awareness |
| ❌ Incomplete | Missing requirements or failing checks | Continue implementation |

---

### Rules

#### Do:
- Run ALL automated checks
- Verify EVERY requirement
- Document deferred items explicitly
- Note technical debt
- Include test coverage metrics

#### Don't:
- Skip automated checks
- Assume requirements are met
- Hide issues in the review
- Declare complete if tests fail
- Forget to check API contracts

---

### Handoff

After review:
- If ✅: Feature is ready for deployment/merge
- If ⚠️: Proceed with documented caveats
- If ❌: Continue with `/spice:iterate` or fix issues manually
