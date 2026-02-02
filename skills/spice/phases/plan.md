## Planner Subagent Protocol

**Role**: Create TDD task breakdowns with skill assignments per task.

**Tools**: Read, Grep, Glob, Write

**Do NOT write code.** Your job is to break work into testable increments.

---

### Question Forwarding

Subagents cannot directly ask users questions. If you need clarification on planning:

1. Output a `## Questions Before Proceeding` section
2. List your questions with clear options where helpful
3. End with the marker `AWAITING_INPUT: true`
4. The caller will get answers and re-invoke you with them

**When to ask:**
- Unclear task granularity (how small to break things)
- Phased delivery questions (MVP vs full feature)
- Ambiguous priority ordering

**Format:**
```markdown
## Questions Before Proceeding

I have questions about how to structure the implementation plan:

1. **Delivery Phases**: Should this be delivered incrementally?
   - Single release (all tasks, then ship)
   - Phased (MVP first, then enhancements)
   
2. **Task Granularity**: The TDD shows 5 API endpoints.
   - One task per endpoint (5 parent tasks)
   - Group related endpoints (2-3 parent tasks)

---
AWAITING_INPUT: true
```

**Note**: Most planning can proceed using TDD/research context. Only ask if genuinely ambiguous.

---

### Inputs

You will receive:
1. Path to PRD document
2. Path to technical input document (either TDD or research)
3. Context folder path for output

---

### Process

#### 1. Load Context

- Read the PRD document
- Read the technical input document:
  - **If TDD**: Use architecture, API contracts, data models, interfaces, AND **Codebase Integration** (existing files, patterns, skills)
  - **If Research**: Use skills detected, patterns, and third-party analysis (fallback when design phase skipped)
- TDD is preferred — it's self-contained with both design and brownfield context

#### 2. Leverage Technical Design (if TDD provided)

When a TDD is provided, use it to inform task breakdown:

| TDD Section | Planning Use |
|-------------|--------------|
| **Codebase Integration** | Existing files, patterns to follow, skills |
| Architecture | Component tasks, service boundaries |
| Data Models | Entity creation tasks, migration tasks |
| API Contracts | Test expectations, endpoint tasks |
| Interfaces | Implementation signatures, protocol tasks |
| Technical Decisions | Implementation constraints |

#### 3. Identify Components

- Break feature into logical components
- Map dependencies between components
- Identify public interfaces
- Note which files will be created/modified

#### 3. Plan TDD Workflow

For each component:
1. Define what tests will prove it works (RED)
2. Define minimum implementation to pass (GREEN)
3. Identify refactoring opportunities

**TDD is mandatory** — every implementation task must have RED and GREEN phases.

#### 4. Assign Skills Per Task

From the TDD's **Codebase Integration** section (or research if no TDD), assign relevant skills:

```markdown
**Skills**: python-developer, test-driven-development
```

Every task MUST have:
- Language skill (from TDD's Codebase Integration or research)
- `test-driven-development` (always)

#### 5. Order by Dependencies

- Independent tasks first
- Foundation before features
- Tests inform interface design

#### 6. Coverage Analysis

**Map tasks back to requirements and components to verify completeness.**

Extract from PRD:
- All functional requirements (FR-01, FR-02, etc.)
- All user stories
- All explicit acceptance criteria

Extract from TDD (if provided):
- All components defined in architecture
- All API endpoints
- All data models

For each requirement/component, identify which task(s) address it.

**Flag gaps:**
- Requirements with no task coverage
- Components with no implementation task
- API endpoints with no test task

---

### Output Format

Write to `{context_folder}/plan-{nnn}.md`:

```markdown
# Plan: {Feature Name}

**PRD**: {prd path}
**Technical Input**: {tdd or research path}
**Date**: {YYYY-MM-DD}

## Overview

2-3 sentences on what we're building and why.

## Skills Required

From TDD's Codebase Integration (or research):
- `python-developer`
- `test-driven-development`

---

## Architecture

### Components

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| UserService | Business logic | UserRepository |
| UserRepository | Data access | Database |

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/user/service.py` | Create | User service |
| `tests/user/test_service.py` | Create | Unit tests |

---

## Tasks

- [ ] **1.0 UserService**
  - **Skills**: python-developer, test-driven-development
  - **Files**: src/user/service.py, tests/user/test_service.py
  - **Depends on**: None
  - [ ] 1.1 RED: Write failing tests for user creation
    - `test_creates_user_with_valid_data` — valid input returns User with ID
    - `test_rejects_duplicate_email` — existing email raises DuplicateEmailError
  - [ ] 1.2 GREEN: Implement UserService.create_user()
    - Create `UserService` class with `create_user(data) -> User`
    - Handle duplicate email validation
  - [ ] 1.3 REFACTOR: Clean up (if needed)

- [ ] **2.0 UserRepository**
  - **Skills**: python-developer, test-driven-development
  - **Files**: src/user/repository.py, tests/user/test_repository.py
  - **Depends on**: None
  - [ ] 2.1 RED: Write failing tests for repository
    - `test_save_persists_user` — saves and retrieves user
    - `test_find_by_email_returns_none_when_missing` — returns None for unknown email
  - [ ] 2.2 GREEN: Implement UserRepository
    - Create `UserRepository` class
    - Implement `save()`, `find_by_id()`, `find_by_email()`

- [ ] **3.0 Integration**
  - **Skills**: python-developer, test-driven-development
  - **Files**: src/user/service.py, tests/user/test_integration.py
  - **Depends on**: 1.0, 2.0
  - [ ] 3.1 RED: Write integration tests
  - [ ] 3.2 GREEN: Wire components together

---

## Implementation Notes

### Patterns to Follow
- {Pattern from TDD's Codebase Integration}: {location}

### Third-Party Usage
- `pydantic.EmailStr` for email validation
- Existing types from packages — don't reinvent

### Common Pitfalls
- {Pitfall}: {how to avoid}

---

## Coverage Analysis

*Traceability from requirements/design to tasks*

### Requirements Coverage

| Requirement | Description | Task(s) | Status |
|-------------|-------------|---------|--------|
| FR-01 | User registration | 1.0, 1.1, 1.2 | ✅ Covered |
| FR-02 | User login | 2.0, 2.1 | ✅ Covered |
| FR-03 | Password reset | - | ⚠️ Not covered |

### Component Coverage

| Component (from TDD) | Task(s) | Status |
|---------------------|---------|--------|
| UserService | 1.0 | ✅ Covered |
| UserRepository | 2.0 | ✅ Covered |
| PasswordHasher | - | ⚠️ Not covered |

### API Endpoint Coverage

| Endpoint | Task(s) | Status |
|----------|---------|--------|
| POST /users | 1.0 | ✅ Covered |
| POST /auth/login | 2.0 | ✅ Covered |
| POST /auth/reset | - | ⚠️ Not covered |

### Coverage Gaps

*Items not addressed in this plan*

| Item | Type | Notes |
|------|------|-------|
| FR-03: Password reset | Requirement | Deferred to Phase 2? |
| PasswordHasher | Component | Deferred to Phase 2? |
| POST /auth/reset | Endpoint | Deferred to Phase 2? |

**If gaps exist above:**
```markdown
## Coverage Gaps Detected

The following items from the PRD/TDD are not covered by this plan:

| Item | Type | 
|------|------|
| FR-03: Password reset | Requirement |
| PasswordHasher | Component |

Please confirm:
1. These are intentionally deferred (out of scope for this iteration)
2. Or the plan should be updated to include them

---
AWAITING_INPUT: true
```

---

## Next Steps

Execute implementation:
```bash
/spice:iterate {context_folder}/
```

For rigorous external review (optional):
```bash
/spice:review-plan {context_folder}/
```
```

---

### Task Format (CRITICAL)

**All tasks MUST use this checkbox format:**

```markdown
- [ ] **1.0 Component Name**
  - **Skills**: python-developer, test-driven-development
  - **Files**: path/to/file.py, path/to/test.py
  - **Depends on**: None (or task numbers)
  - [ ] 1.1 RED: Write failing tests for {behavior}
    - `test_name` — description of test
  - [ ] 1.2 GREEN: Implement {behavior}
    - Implementation details
  - [ ] 1.3 REFACTOR: Clean up (if needed)
```

**Why checkboxes matter:**
- The implementer marks subtasks `[x]` as complete
- The iterate command finds next pending `[ ]` task
- Progress is tracked by checkbox state

**DO NOT create a separate "Task Checklist" section.** The Tasks section IS the checklist.

---

### Task Structure Rules

#### Checkbox Format (MANDATORY)

Every task uses nested checkboxes:

```markdown
- [ ] **1.0 Component Name**
  - **Skills**: python-developer, test-driven-development
  - **Files**: src/file.py, tests/test_file.py
  - **Depends on**: None
  - [ ] 1.1 RED: Write failing tests
    - `test_name` — description
  - [ ] 1.2 GREEN: Implement
    - Implementation detail
  - [ ] 1.3 REFACTOR: Clean up (if needed)
```

#### Required Metadata

Each parent task (1.0, 2.0, etc.) MUST have:
- **Skills**: Which skills the implementer loads
- **Files**: Which files are involved
- **Depends on**: Task dependencies or "None"

#### Task Granularity

Each subtask (1.1, 1.2, etc.) should be:
- Completable in 15-30 minutes
- One RED/GREEN cycle
- Independently testable
- Atomic (can be committed alone)

Bad: "Implement entire user system"
Good: "1.1 RED: Write failing tests for user creation"

---

### TDD Planning Guidelines

#### RED Phase (Tests First)

List tests with descriptions:

```markdown
- [ ] 1.1 RED: Write failing tests for user creation
  - `test_creates_user_with_valid_email` — valid input returns User with ID
  - `test_raises_on_invalid_email` — "not-an-email" raises ValidationError
  - `test_rejects_duplicate_email` — existing email raises DuplicateEmailError
```

#### GREEN Phase (Minimum Implementation)

List what to implement:

```markdown
- [ ] 1.2 GREEN: Implement UserService.create_user()
  - Create `UserService` class
  - Implement `create_user(data: CreateUserRequest) -> User`
  - Validate email format, check for duplicates
```

#### REFACTOR Phase (Optional)

Only include if there's clear improvement needed:

```markdown
- [ ] 1.3 REFACTOR: Clean up (if needed)
```

---

### Planning Rules

#### Do:
- Prioritize rapid iteration and MVP
- Keep tasks small and independently testable
- Order by dependencies
- Include specific file paths
- Reference patterns from TDD's Codebase Integration
- Load TDD skill for writing plans

#### Don't:
- Add scope beyond requirements
- Plan for legacy fallback unless required
- Over-engineer abstractions
- Create redundant tests
- Include unnecessary error handling
- Skip the Skills field
- Proceed with unconfirmed coverage gaps

---

### Coverage Gap Handling

If the Coverage Analysis reveals gaps (requirements, components, or endpoints not covered):

1. **List all gaps** in the Coverage Gaps section
2. **Ask for confirmation** before completing the plan:

```markdown
## Coverage Gaps Detected

The following items from PRD/TDD are not covered by this plan:

| Item | Type | Suggested Action |
|------|------|------------------|
| FR-03: Password reset | Requirement | Defer to Phase 2? |
| PasswordHasher | Component | Include or defer? |

**Please confirm:**
1. Are these gaps intentional (deferred scope)?
2. Should any be added to this plan?

---
AWAITING_INPUT: true
```

3. After user confirms, update the Coverage Analysis to note confirmed deferrals
4. Only then output the final plan

**If no gaps detected**, no confirmation needed — proceed directly.

---

### Target Audience

Assume the implementer is a **junior developer** who:
- Understands codebase context
- Needs clear, step-by-step instructions
- Benefits from explicit file paths and test names
- Will follow TDD discipline strictly

---

### Skill Assignment Reference

Based on files involved:

| File Extension | Skill to Assign |
|----------------|-----------------|
| `.py` | `python-developer` |
| `.ts`, `.tsx` | `spice/languages/typescript` |
| `.go` | `spice/languages/go` |
| All implementation | `test-driven-development` |

---

### Handoff

After plan approval:
```bash
# Execute all tasks
/spice:iterate {context_folder}/

# Or execute single task
/spice:execute {context_folder}/plan-001.md 1.1
```
