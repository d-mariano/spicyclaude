# Slash Commands Reference

This directory contains all available slash commands for Claude Code workflows. Commands are user-defined operations that expand to full prompts, enabling consistent and specialized task execution.

## Command Architecture

Commands are defined using markdown files with YAML frontmatter:

```yaml
---
allowed-tools: Bash, Glob, Grep, Read, Edit, Write
argument-hint: [topic]
description: Brief description of command purpose
---
```

The command body contains the prompt template with `$1`, `$2`, etc. for argument substitution.

## Core Workflow Commands

These commands form the backbone of the recommended development workflow: **PRD → Research → Plan → Execute**.

### `/prdgen [idea]`
**File**: `prdgen.md`
**Purpose**: Interactively generate a Product Requirements Document from an initial idea
**Output**: `/context/[nnn]-{feature}/prd-[nnn].md`

- Asks clarifying questions to gather requirements
- Focuses on understanding "what" and "why" (not "how")
- Target audience: junior developers
- **Recommended for**: Starting PRDs or refining existing ones

### `/prdresearch [idea]` (Experimental)
**File**: `prdresearch.md`
**Purpose**: PRD generation with integrated research cycles
**Output**: `/context/[nnn]-{feature}/prd-[nnn].md` and `research-[nnn].md`

- Combines `/prdgen` and `/research` in iterative cycles
- Automatically invokes `@researcher` agent throughout process
- Researches before questions, after answers, and after PRD changes
- **⚠️ Note**: May require extra researcher calls (WIP)
- **Recommended for**: Complex features requiring deep research during ideation

### `/research [topic]`
**File**: `research.md`
**Purpose**: Conduct comprehensive research on a topic or PRD
**Output**: `/context/[nnn]-{feature}/research-[nnn].md`

- Reads through related code and documentation
- Conducts web searches on frameworks and libraries
- Identifies third-party types and alternative approaches
- **Recommended for**: Main workflow research phase after PRD creation

### `/plan [prd] [research]`
**File**: `plan.md`
**Purpose**: Create detailed implementation plan from PRD and research
**Output**: `/context/[nnn]-{feature}/plan-[nnn].md`

- Identifies files that need changes
- Lists new classes, functions, and test names
- Includes specific tasks in checkbox format
- Reinforces CLAUDE.md principles
- **Recommended for**: Main workflow planning phase

### `/execute [plan]`
**File**: `execute.md`
**Purpose**: Implement the plan with TDD and continuous validation
**Output**: `/context/[nnn]-{feature}/progress.md`

- Follows Test Driven Development practices
- Marks tasks complete incrementally with commits
- Runs full test suite before each commit
- Tracks progress throughout execution
- **Recommended for**: Main workflow execution phase

### `/explore [topic]`
**File**: `explore.md`
**Purpose**: Alternative research command for gaining context
**Output**: Does not output to file (ephemeral exploration)

- Lighter-weight than `/research`
- Good for quick investigations
- **Recommended for**: Ad-hoc exploration without formal documentation

### `/taskgen [prd]`
**File**: `taskgen.md`
**Purpose**: Generate task list from a PRD
**Output**: Task list

- Breaks down PRD into actionable tasks
- Alternative to full `/plan` command

### `/taskexec [tasks]`
**File**: `taskexec.md`
**Purpose**: Execute a specific task list
**Output**: Completed tasks

- Lighter-weight than full `/execute` command
- Good for targeted task completion

## Code Quality Commands

Use these commands to validate and improve code quality before merging.

### `/pragmatic-code-review`
**File**: `pragmatic-code-review.md`
**Purpose**: Conduct pragmatic code review on current branch
**Output**: Review feedback

- Focuses on practical concerns over theoretical perfection
- Reviews pending changes systematically
- Invokes `@pragmatic-code-review` agent
- **Recommended for**: Pre-merge validation

### `/design-review`
**File**: `design-review.md`
**Purpose**: Comprehensive UI/UX design review
**Output**: Design review report

- Uses Playwright for automated browser testing
- Validates accessibility and responsiveness
- Ensures world-class design standards
- Invokes `@design-review` agent
- **Recommended for**: Pre-merge validation of UI changes

### `/simplify`
**File**: `simplify.md`
**Purpose**: Refactor and simplify existing code
**Output**: Simplified code

- Identifies unnecessary complexity
- Removes code slop (unused imports, over-abstraction, etc.)
- Aligns with CLAUDE.md principle: "Delete more than you add"
- **Recommended for**: Periodic code cleanup

## Utility Commands

Helper commands for various workflow needs.

### `/crawl`
**File**: `crawl.md`
**Purpose**: Generate/update CLAUDE.md documentation files
**Output**: CLAUDE.md files throughout codebase

- Recursively documents codebase structure and patterns
- Updates after feature changes
- Invokes `@claude-crawler` agent
- **Recommended for**: Keeping documentation in sync

### `/pr`
**File**: `pr.md`
**Purpose**: Create pull request with proper formatting
**Output**: GitHub pull request

- Creates PR with standardized format
- Provides advice for next PR to different developer
- **Recommended for**: Final step before merge

### `/next`
**File**: `next.md`
**Purpose**: Determine next steps in development workflow
**Output**: Research and recommendations

- Reviews project state
- Suggests next actions
- Conducts review of relevant files
- **Recommended for**: When unsure what to do next

### `/quick`
**File**: `quick.md`
**Purpose**: Quick task execution for simple changes
**Output**: Completed task

- Looks at GitHub issue
- Reads related code and docs
- Implements and verifies solution
- **Recommended for**: Small, well-defined issues

## Custom Workflow Commands

User-defined custom workflows.

### `/my-developer-plan`
**File**: `my-developer-plan.md`
**Purpose**: Custom planning workflow
**Output**: Custom plan format

### `/my-developer-review`
**File**: `my-developer-review.md`
**Purpose**: Custom review workflow
**Output**: Custom review format

## Command Execution Flow

1. User types `/command [args]` or SlashCommand tool invoked
2. Command file loaded and parsed
3. YAML frontmatter validates allowed tools
4. Arguments (`$1`, `$2`) substituted into prompt template
5. Expanded prompt sent to Claude with tool restrictions
6. Claude executes using only allowed tools
7. Results stored in specified location (often `/context/` subdirectories)

## Context Management

Commands use structured `/context/` directory organization:

```
/context/
  [nnn]-{feature-name}/
    prd-[nnn].md          # Product requirements
    research-[nnn].md     # Research findings
    plan-[nnn].md         # Implementation plan
    progress.md           # Execution progress
```

This structure keeps all related materials together and enables easy reference across workflow stages.

## Best Practices

- **Follow the main workflow**: PRD → `/research` → `/plan` → `/execute`
- **Use descriptive command names** that match their purpose
- **Limit tool access** to minimum required (principle of least privilege)
- **Store outputs** in organized `/context/` subdirectories
- **Reference CLAUDE.md principles** in all command prompts
- **Chain commands** for complex workflows
- **Use agents** for specialized processing

## Testing Commands

Test commands by:
1. Running with appropriate arguments
2. Verifying tool restrictions are respected
3. Checking output is created in expected locations
4. Validating argument substitution works correctly

## Resources

- [Claude Code Slash Commands Documentation](https://docs.claude.com/en/docs/claude-code/slash-commands)
- Global CLAUDE.md for development principles
- Agent definitions in `/agents/` for specialized processing
- Main README.md for workflow overviews
