---
name: test-driven-development
description: >
  Enforces test-driven development via RED-GREEN-REFACTOR when writing code.
  Use when implementing features, fixing bugs, refactoring, or writing any
  functional code. Triggers: 'write tests first', 'TDD', 'test-driven',
  'red-green-refactor', new feature, bug fix, refactor. Does not apply to
  pure config files (JSON, YAML, .env), type-only definitions, or documentation.
---

# Test-Driven Development — Agent Protocol

TDD is a design discipline. Tests drive the implementation, not the other way around.
Every piece of functional code is preceded by a failing test. No exceptions unless
the work is purely configuration, documentation, or type-only definitions.

## Step 0: Discover the Project's Test Setup

Before writing anything, understand the existing test infrastructure.

1. **Find the test framework.** Look for config files: `jest.config.*`, `vitest.config.*`, `pytest.ini`, `pyproject.toml [tool.pytest]`, `go.test`, `Cargo.toml`, `.rspec`, etc.
2. **Find existing tests.** Search for test directories: `__tests__/`, `tests/`, `test/`, `spec/`, or co-located `*.test.*` / `*.spec.*` files. Match the existing convention.
3. **Find the test command.** Check `package.json` scripts, `Makefile`, `Taskfile`, or README for how to run tests. Common commands: `npm test`, `pytest`, `go test ./...`, `cargo test`, `bundle exec rspec`.
4. **If no test setup exists**, ask the user which framework to use or recommend the ecosystem default (Jest/Vitest for JS/TS, pytest for Python, `testing` for Go, cargo test for Rust). Set it up before proceeding.

Run the existing test suite once to confirm a clean baseline. If tests are failing
before you start, stop and tell the user.

## Step 1: RED — Write One Failing Test

Pick the smallest behavior to implement. Write exactly one test for it.

**Test structure follows Arrange-Act-Assert:**
```
Arrange — set up the system under test and its dependencies
Act     — execute exactly one behavior
Assert  — verify the expected outcome
```

If you are acting on multiple things or asserting unrelated outcomes, split into
separate tests.

**Name tests after behavior, not implementation:**
```python
# Good: describes what the system does
test_expired_subscription_denies_access()
test_empty_cart_shows_zero_total()

# Bad: describes how the code works
test_check_expiry_returns_false()
test_get_total_function()
```

Run the test. It must fail. If it passes, either the behavior already exists or the
test is wrong — investigate before continuing.

**Gate check:** The test fails for the right reason (missing functionality, not a
syntax error or import failure). Fix setup issues before counting this as a valid red.

## Step 2: GREEN — Write Minimum Code to Pass

Write only enough production code to make the failing test pass. Nothing more.

- Hardcoding a return value is acceptable if it passes. The next test forces generalization.
- Do not add error handling, optimization, or features not demanded by a failing test.
- Do not refactor yet.

Run all tests. Every test must be green before proceeding.

**Gate check:** All tests pass, including pre-existing ones. If a new test broke an
old one, fix that first.

## Step 3: REFACTOR — Improve While Green

With all tests passing, clean up both production and test code:

- Remove duplication
- Improve naming and clarity
- Extract methods or classes if complexity warrants it
- Simplify conditionals

Run tests after every small change. If any test fails, revert immediately and
take a smaller step.

**Gate check:** All tests still pass. Code is cleaner than before.

## Step 4: REPEAT

Go back to Step 1 with the next behavior. Continue the cycle until the feature is
complete.

## Commit Strategy

Commit at meaningful green points — typically after completing a full RED-GREEN-REFACTOR
cycle or a coherent set of cycles. Each commit should leave the test suite green.

## Bug Fix Protocol

When fixing a bug, the cycle is the same but starts differently:

1. Write a test that reproduces the bug (it should fail, confirming the bug exists)
2. Fix the bug with minimum code (GREEN)
3. Refactor if needed
4. Verify no existing tests broke

## When You're Stuck

If you cannot get to green with a small change, the step was too big. Back up and
write a simpler test. Even testing that a class can be instantiated or a function
returns a hardcoded value is a valid first step. Small steps compound.

## Edge Cases and User Overrides

- **User says "skip tests":** Confirm with the user that they want to skip TDD for
  this task. Comply if they insist, but note that tests were skipped.
- **Massive untested codebase:** Do not try to retroactively test everything. Apply
  TDD to the code you're changing now. Add tests around the seams where your changes
  touch existing code.
- **Prototyping / spike:** If the user is explicitly spiking or prototyping and will
  throw the code away, TDD can be skipped. Confirm intent.

## Reference Material

Read these when writing tests — they contain patterns, anti-patterns, and examples
that prevent common mistakes.

**Testing principles and anti-patterns:** Covers fast, independent, repeatable,
self-validating, and thorough tests, plus the seven most common testing mistakes
with before/after examples. Read when planning test structure or reviewing test quality.
→ [references/testing-principles.md](references/testing-principles.md)

**Test doubles (mocks, stubs, fakes):** Covers when to use each type, what to mock
vs. what to keep real, and the line between useful test doubles and over-mocking.
Read when dealing with external dependencies, databases, APIs, or complex collaborators.
→ [references/test-doubles.md](references/test-doubles.md)
