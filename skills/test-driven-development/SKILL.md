---
name: test-driven-development
description: ALWAYS use this skill when writing code. TDD is mandatory for all new code, features, bug fixes, and refactoring. Only exceptions are pure configuration files (JSON, YAML, env files) and documentation. Triggers on ANY code-related request. Enforces RED-GREEN-REFACTOR cycle without exception.
---

# Test-Driven Development (TDD) — Mandatory Protocol

**TDD is not optional.** Every line of functional code must be driven by a test. This is non-negotiable.

## When to Use TDD

### ALWAYS Use TDD For:
- New features or functionality
- Bug fixes (write a failing test that reproduces the bug first)
- Refactoring existing code
- API endpoints
- Business logic
- Data transformations
- Utility functions
- Class methods
- Database operations
- Integration points

### The ONLY Exceptions:
- Pure configuration files (JSON, YAML, .env, tsconfig, etc.)
- Documentation and comments
- Type definitions with no runtime behavior
- Import/export statements only

**Do not rationalize skipping TDD.** "It's too simple" is not an excuse. "I'll add tests later" is not acceptable. "This is just a quick fix" still requires a test first.


## Quick Reference: Good vs Bad Tests

| Aspect | ✅ Good Test | ❌ Bad Test |
|--------|-------------|-------------|
| **Speed** | Runs in milliseconds | Uses sleep(), real network |
| **Independence** | Creates own state | Depends on other tests |
| **Determinism** | Same result every run | Random failures |
| **Validation** | Clear assertions | console.log inspection |
| **Scope** | One behavior | Entire workflow |
| **Coupling** | Tests public interface | Tests private implementation |
| **Mocking** | Only external boundaries | Everything mocked |
| **Naming** | Describes behavior | Describes implementation |
| **Cleanup** | Leaves no trace | Pollutes environment |


## TDD Workflow Summary

1. **THINK**: What behavior do I need? What's the simplest test case?
2. **RED**: Write ONE failing test that describes the behavior
3. **GREEN**: Write MINIMAL code to pass the test
4. **REFACTOR**: Clean up while tests stay green
5. **REPEAT**: Next behavior, next test

**When stuck:** Take smaller steps. Even a hardcoded return value that passes is progress. The next test will force generalization.

**Remember:** TDD is a design discipline, not just verification. The test drives the design. If you're writing implementation first, you're not doing TDD.

## Mandatory Resources for Planning and Writing Tests

**The TDD Cycle: RED → GREEN → REFACTOR**: See [red-green-refactor.md](red-green-refactor.md)

**Test Naming Conventions**: See [naming.md](naming.md)


## Mandatory Resources for Writing Tests

**The FIRST Principles of Good Tests**: See [first-principles.md](first-principles.md)

**Anti-Patterns: The Seven Deadly Sins of Testing**: See [anti-patterns.md](anti-patterns.md)

**Test Structure: Arrange-Act-Assert (AAA)**: See [aaa.md](aaa.md)

**Test Doubles and Mocks: When to Use What**: See [mocking.md](mocking.md)