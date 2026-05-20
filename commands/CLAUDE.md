# Claude Code Slash Commands

## Overview
This directory contains custom slash command definitions for Claude Code. Slash commands are user-defined operations that expand to full prompts, enabling consistent workflows and specialized task execution.

## Architecture

### Command Configuration Format
Commands are defined using markdown files with YAML frontmatter:
- `allowed-tools`: List of tools the command can use (supports wildcards like `Bash(git add:*)`)
- `argument-hint`: Optional parameter hints shown to users (e.g., `[topic]`, `[prd] [research]`)
- `description`: Brief explanation of the command's purpose

### Command Body
The markdown body contains the prompt template with parameter placeholders:
- `$1`, `$2`, etc. reference command arguments
- Commands can include instructions, constraints, and output formatting
- Can specify file paths for output (e.g., `/context/{feature|branch}/plan.md`)

## Available Commands

### Development Workflow
- **research** (`research.md`): Explore codebase and conduct web searches to understand a topic or PRD without writing code
- **plan** (`plan.md`): Create detailed implementation plan based on PRD and research
- **execute** (`execute.md`): Write elegant code implementing the plan, respecting CLAUDE.md principles
- **explore** (`explore.md`): Alternative research command for gaining context

### Code Quality
- **pragmatic-code-review** (`pragmatic-code-review.md`): Conduct pragmatic code review on current branch
- **design-review** (`design-review.md`): Comprehensive UI/UX design review with automated testing
- **simplify** (`simplify.md`): Refactor and simplify code

### Utilities
- **crawl** (`crawl.md`): Generate/update CLAUDE.md documentation files
- **pr** (`pr.md`): Create pull request workflow
- **next** (`next.md`): Determine next steps
- **quick** (`quick.md`): Quick task execution

### Custom Development Workflows
- **my-developer-plan** (`my-developer-plan.md`): Custom planning workflow
- **my-developer-review** (`my-developer-review.md`): Custom review workflow

## Data Flow

### Command Execution
1. User types `/command [args]` or SlashCommand tool invoked
2. Command file loaded and parsed
3. YAML frontmatter validates allowed tools
4. Arguments (`$1`, `$2`) substituted into prompt template
5. Expanded prompt sent to Claude with tool restrictions
6. Claude executes using only allowed tools
7. Results stored in specified location (often `/context/` subdirectories)

### Common Patterns
- **Research → Plan → Execute**: Standard development workflow
  - `/research [topic]` → `/context/{feature}/research.md`
  - `/plan [prd] [research]` → `/context/{feature}/plan.md`
  - `/execute [plan]` → `/context/{feature}/progress.md`
- **Review → Fix → Validate**: Quality workflow
  - `/pragmatic-code-review` or `/design-review`
  - Fix issues identified
  - Re-run review to validate

## Context Management
Commands often use `/context/{feature|branch}/` directory structure:
- `research.md`: Findings from exploration
- `plan.md`: Implementation plan
- `progress.md`: Execution progress
- `tdd-[nnn].md`: Technical design document (from `design-doc` skill or `spice-designer` agent)
- `contracts-[nnn].md`: Companion field-level wire shapes (from `design-doc` skill)
- Organize by feature name or branch name

## Testing
Test commands by:
1. Running them with appropriate arguments
2. Verifying tool restrictions are respected
3. Checking output is created in expected locations
4. Validating argument substitution works correctly

## Resources
- [Claude Code Slash Commands Documentation](https://docs.claude.com/en/docs/claude-code/slash-commands)
- Global CLAUDE.md (`/Users/dave/.claude/CLAUDE.md`) for development principles
- Agent definitions in `../agents/` for specialized processing

## Best Practices
- Use descriptive command names that match their purpose
- Limit tool access to minimum required (follows principle of least privilege)
- Include clear argument hints when parameters are needed
- Store outputs in organized `/context/` subdirectories
- Reference CLAUDE.md principles in command prompts
- Chain commands for complex workflows (research → plan → execute)
- Use agents for specialized processing (e.g., design-review, crawler)
