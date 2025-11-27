## Core Philosophy
- Delete more than you add, complexity compounds into disasters
- Follow SOLID (Single Responsibility (S), Open-Closed (O), Liskov Substitution (L), Interface Segregation (I), and Dependency Inversion (D))
- Follow KISS (Keep It Simple Stupid)
- Assume an MVP of a rapidly iterative startup, not an enterprise
- Be pragmatic, don't follow or do for the sake of following or doing, but only if what you are doing provides immediate benefit
- Trust your research, don't read files more than once unless something doesn't make sense
- Do not think about backups unless explicitly asked
- Fail fast and loud, not silently and secretively
- When simplifying/editing/refactoring, treat the simplified version as if it has no knowledge of the previous one

## Development Lifecycle
- Plan, Execute, Validate, Repeat
- When implementing, unless asked otherwise, use or plan for Test Driven Development
- Validate both Red and Green phases of TDD
- Always break up implementation into logical pieces, ideally separated by component or concern

## Implementation
- Delete more code than you add when possible (unused imports, unused code, etc)
- Do not add backwards compatibility unless explicitly requested
- Use SOLID principals, but be reasonable and DO NOT over engineer abstractions
- Limit 1 class per file
- Aviod unnecessary try/catches
- Fail fast and loud
- Avoid simply wrapping errors
- Add docblocks to functions, methods, and classes that you create
- Update dockblocks of functions, methods, and classes that you edit, when applicable
- Do not create unnecessary types or abstractions, always check if third-party types exist before creating your own

## Validation
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

## Visual Development

### Design Principles
- Comprehensive design checklist in `/context/design-principles.md`
- Brand style guide in `/context/style-guide.md`
- When making visual (front-end, UI/UX) changes, always refer to these files for guidance

### Quick Visual Check
IMMEDIATELY after implementing any front-end change:
1. **Identify what changed** - Review the modified components/pages
2. **Navigate to affected pages** - Use `mcp__playwright__browser_navigate` to visit each changed view
3. **Verify design compliance** - Compare against `/context/design-principles.md` and `/context/style-guide.md`
4. **Validate feature implementation** - Ensure the change fulfills the user's specific request
5. **Check acceptance criteria** - Review any provided context files or requirements
6. **Capture evidence** - Take full page screenshot at desktop viewport (1440px) of each changed view
7. **Check for errors** - Run `mcp__playwright__browser_console_messages`

This verification ensures changes meet design standards and user requirements.

### Comprehensive Design Review
Invoke the `@design-review` agent for thorough design validation when:
- Completing significant UI/UX features
- Before finalizing PRs with visual changes
- Needing comprehensive accessibility and responsiveness testing
