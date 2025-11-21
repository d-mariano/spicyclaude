---
allowed-tools: Bash, BashOutput, Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: [plan]
description: Implement a given plan.
---
## Goal

Think hard. Write elegant code that completes $1.

Respect Core Philosophy, Development Lifecycle, Implementation, and Validation, in CLAUDE.md.

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
      - References the task number and PRD context
      - **Formats the message as a single-line command using `-m` flags**, e.g.:

        ```
        git commit -m "feat: add payment validation logic" -m "- Validates card type and expiry" -m "- Adds unit tests for edge cases" -m "Related to T123 in PRD"
        ```
  3. Once all the subtasks are marked completed and changes have been committed, mark the **parent task** as completed.

### AI Instructions

When working with task lists, the AI must:

1. Regularly update the task list file after finishing any significant work.
2. Follow the completion protocol:
   - Mark each finished **sub‑task** `[x]`.
   - Mark the **parent task** `[x]` once **all** its subtasks are `[x]`.
3. Add newly discovered tasks.
4. Keep "Relevant Files" accurate and up to date.
5. Before starting work, check which sub‑task is next.

## Output
- Store your progress in `/context/[nnn]-{feature|branch|question}/progress_[nnn].md`, unless instructed otherwise

### Examples:
- `/context/001-implement-cool-service/progress_001.md`
- `/context/001-implement-cool-service/progress_002.md`
- `/context/002-cool-service-addons/progress_002.md`
- `/context/some/specified/path/progress_001.md`