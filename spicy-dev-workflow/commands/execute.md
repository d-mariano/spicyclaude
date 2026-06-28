---
allowed-tools: Bash, BashOutput, Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch, Skill
argument-hint: "[plan]"
description: Implement a given plan.
---
## Goal
You are a world class software engineer.

Ultrathink. Write elegant code that completes $1.

Respect Core Philosophy, Development Lifecycle, Implementation, and Validation, in CLAUDE.md.

Refer to official docs and research in `/context/[nnn]-{feature|branch|question}/research-*` as needed.

## Skill loading protocol

**Before any other work, invoke `Skill(test-driven-development)`.** This is unconditional — the TDD skill self-gates on its documented exclusions (pure config, type-only, rename), so loading it once for the run costs nothing on tasks where it doesn't apply.

**Per parent task, before starting its subtasks:**
1. Read the parent task's `**Skills:**` metadata field from the plan.
2. For each skill listed *other than* `test-driven-development` (which is already loaded), invoke `Skill(<name>)`. Typically this is one of `python-development`, `terraform-development`.
3. **If the `**Skills:**` field is missing from a parent task, stop and report the plan as malformed.** Do not guess or detect project type — the planner is responsible for annotating this field, and a silent skip would hide a planner bug. Per the project's "fail fast and loud" principle, surface it.

## Steps
1. Load TDD per the Skill loading protocol above (once per run).
2. Before starting work on any parent task, check which sub‑task is next AND load that parent's `**Skills:**` per the protocol.
3. Regularly update the task list file after finishing any significant work.
4. Follow the completion protocol:
   - Mark each finished **sub‑task** `[x]`.
   - Mark the **parent task** `[x]` once **all** its subtasks are `[x]`.
5. Add newly discovered tasks.
6. Keep "Relevant Files" accurate and up to date.

## Task List Management

Guidelines for managing task lists in markdown files to track progress on completing a plan or task list.

### Task Implementation
1. When you finish a **sub‑task**, immediately mark it as completed by changing `[ ]` to `[x]`.
  2. If **all** subtasks underneath a parent task are now `[x]`, follow this sequence:
    - **First**: Run the full test suite (`pytest`, `npm test`, `bin/rails test`, etc.)
    - **Only if all tests pass**: Stage changes (`git add .`)
    - **Clean up**: Remove any temporary files and temporary code before committing
    - **Commit**: Use a descriptive commit message that:
      - Uses conventional commit format (`feat:`, `fix:`, `refactor:`, etc.)
      - Summarizes what was accomplished in the parent task
      - Lists key changes and additions
      - **Formats the message as a single-line command using `-m` flags**, e.g.:
        ```
        git commit -m "feat: add payment validation logic" -m "- Validates card type and expiry" -m "- Adds unit tests for edge cases"
        ```
  3. Once all the subtasks are marked completed and changes have been committed, mark the **parent task** as completed.


## Output
- Store your progress in `/context/[nnn]-{feature|branch|question}/progress-[nnn].md`, unless instructed otherwise

### Examples:
- `/context/001-implement-cool-service/progress-001.md`
- `/context/001-implement-cool-service/progress-002.md`
- `/context/002-cool-service-addons/progress-002.md`
- `/context/some/specified/path/progress-001.md`