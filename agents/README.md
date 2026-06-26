# Agents Reference

This directory contains specialized agent configurations for Claude Code. Agents are autonomous sub-processes that handle complex, focused tasks using defined tools and models.

## Agent Architecture

Agents are defined using markdown files with YAML frontmatter:

```yaml
---
name: agent-name
description: When and why to use this agent
tools: Bash, Glob, Grep, Read, Edit, Write
model: sonnet
color: green
---
```

The agent body contains detailed instructions for autonomous execution.

## Core Development Agents

These agents support the main workflow phases.

### `@planner`
**File**: `planner.md`
**Model**: Sonnet
**Purpose**: Creates detailed implementation plans from PRDs and research

**Capabilities**:
- Identifies files that need changes
- Lists new classes, functions, and test names
- Creates task checklists in proper format
- Reinforces CLAUDE.md principles throughout

**When to use**:
- Invoked automatically by `/plan` command
- Can be used directly for custom planning tasks
- Good for breaking down complex features

**Output**: `/context/[nnn]-{feature}/plan-[nnn].md`

---

### `@researcher`
**File**: `researcher.md`
**Model**: Sonnet
**Purpose**: Conducts comprehensive research and maintains research files

**Capabilities**:
- Reads through related code and documentation
- Conducts web searches on frameworks and libraries
- Identifies third-party types and alternative approaches
- Maintains cumulative research files across multiple calls

**When to use**:
- Invoked automatically by `/research` command
- Used iteratively by `/prdresearch` command
- Can be used directly for ad-hoc research

**Output**: `/context/[nnn]-{feature}/research-[nnn].md`

---

### `@executer`
**File**: `executer.md`
**Model**: Sonnet
**Purpose**: Implements code following strict TDD principles

**Capabilities**:
- Follows Test Driven Development (RED → GREEN → REFACTOR)
- Validates both RED and GREEN phases
- Marks tasks complete incrementally with commits
- Runs full test suite before each commit

**When to use**:
- Invoked automatically by `/execute` command (main workflow)
- Used by `@iterator` agent for individual tasks (experimental)
- Can be invoked directly for fire-and-forget plan execution

**Output**: `/context/[nnn]-{feature}/progress.md` and code changes

**Context Window Note**: In main workflow, executes in the same context. In experimental workflows, executes in separate context to avoid bloat.

---

### `@iterator` (Experimental)
**File**: `iterator.md`
**Model**: Sonnet
**Purpose**: Iterative task execution with continuous review

**Capabilities**:
- Chooses next important task from plan
- Assigns task to `@executer` agent in new context
- Uses `@pragmatic-code-review` agent to validate implementation
- Repeats until plan complete

**When to use**:
- Large, complex features that would bloat a single context
- When you want each task executed in fresh context
- Experimental context-partitioned execution workflow

**Benefits**:
- Each task gets fresh context, avoiding performance degradation
- Main context stays lean for orchestration
- Better performance on multi-phase projects

**Output**: Orchestrates execution across multiple contexts

---

## Review & Quality Agents

These agents validate code quality and design standards.

### `@plan-reviewer`
**File**: `plan-reviewer.md`
**Model**: Sonnet
**Purpose**: Reviews implementation plans with detailed feedback

**Capabilities**:
- Provides high-level architectural feedback
- Reviews nitty-gritty details of plan
- Suggests improvements and identifies issues
- Acts as "world-class software engineer" reviewer

**When to use**:
- After generating a plan with `/plan` or `@planner`
- Before starting execution to catch issues early
- When you want expert validation of approach

**Output**: Review feedback and suggestions

---

### `@pragmatic-code-review`
**File**: `pragmatic-code-review.md`
**Model**: Sonnet
**Purpose**: Pragmatic code quality assessment

**Capabilities**:
- Focuses on practical concerns over theoretical perfection
- Reviews pending changes systematically
- Identifies real issues, not nitpicks
- Balances quality with pragmatism

**When to use**:
- Invoked automatically by `/pragmatic-code-review` command
- Used by `@iterator` agent to validate each task
- Pre-merge validation

**Output**: Code review feedback

---

### `@design-review`
**File**: `design-review.md`
**Model**: Sonnet
**Purpose**: Automated UI/UX validation with browser testing

**Capabilities**:
- Uses Playwright for automated browser testing
- Tests across multiple viewports (mobile, tablet, desktop)
- Validates WCAG 2.1 AA accessibility standards
- Checks visual consistency and user experience
- Validates against design principles and style guides

**When to use**:
- Invoked automatically by `/design-review` command
- After completing UI/UX features
- Pre-merge validation of visual changes
- When comprehensive accessibility testing needed

**Output**: Design review report with screenshots

---

### Multi-Reviewer Suite (`review-heavy`)
**Files**: `review/mental-alignment.md`, `review/security.md`, `review/code-quality.md`, `review/documentation.md`
**Model**: Sonnet (×4, fanned out in parallel)
**Purpose**: Read-only specialists driven by the [`/review-heavy`](../skills/review-heavy/) skill, which fetches the diff once, runs all four concurrently, and aggregates behind a confidence gate.

- **mental-alignment** — does the diff do what the ticket/PR claims? Catches unimplemented acceptance criteria and scope creep.
- **security** — concretely exploitable flaws only (injection, authz/authn bypass, secrets); strictest confidence discipline.
- **code-quality** — over-engineering and unnecessary complexity, per SOLID + KISS.
- **documentation** — comment rot, over-documentation, stale CLAUDE.md.

Each reviews only the changed code and returns structured findings (or "No concerns identified") — never posts, never approves.

---

## Infrastructure & Documentation Agents

These agents handle meta-tasks and documentation.

### `@claude-crawler`
**File**: `claude-crawler.md`
**Model**: Sonnet
**Purpose**: Generates and maintains CLAUDE.md files throughout codebase

**Capabilities**:
- Recursively explores codebase structure
- Documents patterns, conventions, and architecture
- Updates documentation after feature changes
- Can spawn sub-agents for large codebases

**When to use**:
- Invoked automatically by `/crawl` command
- After completing major features
- When onboarding new team members
- To keep documentation in sync with code

**Output**: CLAUDE.md files throughout repository

---

### `@aws-cdk-agent`
**File**: `aws-cdk-agent.md`
**Model**: Sonnet
**Purpose**: AWS CDK infrastructure development specialist

**Capabilities**:
- Expert in AWS CDK with TypeScript
- Designs lean, cost-effective, scalable infrastructure
- Reviews existing CDK code for best practices
- Ideal for startup environments

**When to use**:
- Planning new AWS infrastructure
- Reviewing existing CDK code
- Designing serverless apps, microservices, networking

**Output**: CDK infrastructure code or review feedback

---

## Agent Invocation

Agents are invoked via the Task tool:

1. Main Claude instance identifies task matching agent specialty
2. Task tool invoked with `subagent_type` parameter
3. Agent receives detailed prompt with context
4. Agent executes autonomously using allowed tools
5. Agent returns single comprehensive report
6. Main instance processes and presents results

## Context Partitioning (Experimental)

**The Challenge**: Large context windows can cause performance degradation:
- Slower response times
- Decreased code quality
- Higher error likelihood
- Difficulty maintaining coherence

**The Solution**: Execute agents in separate context windows:

- **`@iterator` agent** - Orchestrates task-by-task execution
- **`@executer` agent** - Executes each task in fresh context
- **Main context** - Stays lean for oversight and review

**Benefits**:
- Each task gets fresh, focused context
- Main context stays clean
- Better performance on complex projects
- Easier to validate work in isolation

**When to use context partitioning**:
- Context window approaching 200K+ tokens
- Large, complex features
- Long development sessions
- Comfortable with agent-based orchestration

## Agent Communication

- Agents are **stateless** - no ongoing dialogue
- Communication via comprehensive initial prompts
- Results returned in structured reports
- For large codebases, `@claude-crawler` can spawn sub-agents

## Best Practices

- **Use agents for specialized tasks** - Let experts handle their domain
- **Trust agent output** - Agents are optimized for their purpose
- **Provide clear prompts** - Agents need context and expected output format
- **Monitor context size** - Use context partitioning when needed
- **Start simple** - Use main workflow before graduating to agent orchestration
- **Review agent work** - Always validate output before merging

## Testing Agents

Test agents by:
1. Using slash commands that invoke them
2. Directly invoking via Task tool with proper parameters
3. Verifying agent uses only allowed tools
4. Checking output format matches expectations

## Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Agent Best Practices](https://docs.claude.com/en/docs/claude-code/agents)
- Global CLAUDE.md for development principles
- Command definitions in `/commands/` directory
- Main README.md for workflow overviews
