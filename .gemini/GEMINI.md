## Core Philosophy
- Delete more than you add, complexity compounds into disasters
- Follow SOLID (Single Responsibility (S), Open-Closed (O), Liskov Substitution (L), Interface Segregation (I), and Dependency Inversion (D))
- Follow KISS (Keep It Simple Stupid)
- Assume an MVP of a rapidly iterative startup, not an enterprise
- Be pragmatic, don't follow or do for the sake of following or doing, but only if what you are doing provides immediate benefit
- Trust your research, don't read files more than once unless something doesn't make sense
- Do not think about backups unless explicitly asked
- Fail fast and loud, not silently and secretively

## Development Lifecycle
- Plan, Validate, Execute, Validate, Repeat
- When implementing, unless asked otherwise, use or plan for Test Driven Development
- Validate both RED and GREEN phases of TDD
    - RED Phase: Write tests first that test the requirements and public interfaces, validate that they fail as expected
    - GREEN Phase: Implement the code that makes the tests pass, validate that the tests pass as expected
- Always break up implementation into logical pieces, ideally separated by component or concern

## Validation
- Never placeholder tests that pass for future implementation, test must fail accurately, tests must pass accurately
- Treat your tests as another version of the product requirements and specs
- Use Test Driven Development unless requested otherwise
- Run tests on both RED and GREEN phases of TDD when applicable
- Validate every code block you write after you write it: lint, compile, tests
- Write tests for maximum code coverage AND coverage QUALITY
- Test the public interface and core business logic
- Test entire outputs, avoid subsequent tests for testing bits of the output
- If a test covers multiple cases, do not create new tests for each sub-assertion
- For large expected outputs, utilize a fixtures or expected output files, especially for re-use
- Delete more test code than you add when possible
- Always use the correct types when creating mocks, including when mocking third-party responses
- Prioritize predefined types before creating new ones
- Validate with linters/compilers/type-checkers

## Implementation
- Delete more code than you add when possible (unused imports, unused code, etc)
- Do not add backwards compatibility unless explicitly requested
- Use SOLID principals, but be reasonable and DO NOT over engineer abstractions
- Limit 1 class per file
- Aviod unnecessary try/catches
- Avoid simply wrapping errors
- Add docblocks to functions, methods, and classes that you create
- Update dockblocks of functions, methods, and classes that you edit, when applicable
- Do not create unnecessary types or abstractions, always check if third-party types exist before creating your own
- When simplifying/editing/refactoring, treat the simplified version as if it has no knowledge of the previous one
- Do not add comments to code blocks that explain themselves