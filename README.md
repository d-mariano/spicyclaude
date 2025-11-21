# 🤖 Claude Code Workflows & Commands

A comprehensive collection of slash commands, agents, and workflows for Claude Code that implements a structured, iterative approach to AI-assisted software development. ✨

## Overview

This repository provides a complete workflow system for building features with Claude Code, from initial ideation through implementation and validation. The workflow emphasizes structured planning, incremental development, and continuous validation to maximize code quality while maintaining developer control.

## 🔄 Core Workflow

The recommended development cycle follows four distinct phases:

1. **💡 Ideation & Requirements** - Generate a PRD or Story document
   - Use Gemini Deep Research for exploration 🔬
   - Import from Jira or other tools 📋
   - Use `/prdgen [idea]` for interactive PRD generation ❓
   - Creates clear, actionable requirements for junior developers 👥

2. **🔍 Research** - Use `/research <prd.md>` to become a subject matter expert
   - Reads through related code and documentation 📚
   - Conducts web searches on frameworks and libraries 🌐
   - Identifies third-party types and alternative approaches 🔎
   - Outputs to `/context/[nnn]-{feature}/research-[nnn].md`

3. **🗺️ Planning** - Use `/plan <prd.md> <research.md>` to create detailed implementation plan
   - Identifies files that need changes 📝
   - Lists new classes, functions, and test names 🏗️
   - Includes specific tasks in checkbox format ✅
   - Outputs to `/context/[nnn]-{feature}/plan-[nnn].md`

4. **⚡ Execution** - Use `/execute <plan.md>` to implement with continuous validation
   - Follows Test Driven Development practices 🧪
   - Marks tasks complete incrementally with commits 🔄
   - Runs full test suite before each commit ✅
   - Tracks progress in `/context/[nnn]-{feature}/progress.md`

This structured approach ensures clarity at each stage and prevents scope creep while maintaining flexibility to adapt as you learn. All work happens in a **single context window** for maximum coherence.

## 🧪 Experimental Workflows

These workflows explore alternative approaches to managing complexity and context windows:

### PRD Refinement Workflow
Use `/prdgen [idea]` to iteratively refine an existing PRD:
- Interactively asks clarifying questions to improve requirements
- Helps evolve and detail existing product specifications
- Outputs refined PRD to `/context/[nnn]-{feature}/prd-[nnn].md`

### Integrated Research & Refinement (WIP)
Use `/prdresearch [idea]` to combine PRD generation with automatic research:
- Cycles between refining requirements and conducting research
- Automatically invokes `@researcher` agent throughout the process
- Research happens before questions, after answers, and after PRD changes
- **⚠️ Known Issue**: Sometimes requires an extra researcher call
- Useful when you want a fully integrated ideation → research → PRD flow

### Context-Partitioned Execution (Experimental)
Execute plans across **separate context windows** to avoid context bloat:

- **`@iterator` agent** - Iterative task execution with continuous review
  - Chooses next important task from plan
  - Assigns task to `@executer` agent in new context
  - Uses `@pragmatic-code-review` to validate implementation
  - Repeats until plan complete
  - **Benefit**: Each task gets fresh context, avoiding degradation

- **`@executer` agent** - Fire-and-forget plan execution
  - Executes entire plan in separate context window
  - Returns when complete
  - **Benefit**: Main context stays clean for oversight

**Why Context Partitioning?** As context windows grow large, Claude's performance can degrade. Executing work in separate contexts maintains peak performance while allowing the main context to orchestrate and review.

## 📟 Available Slash Commands

### 🚀 Development Workflow Commands

- **`/prdgen [idea]`** - Interactively generate a Product Requirements Document from an initial idea
  - Asks clarifying questions to gather requirements
  - Focuses on understanding "what" and "why" (not "how")
  - Outputs to `/context/[nnn]-{feature}/prd-[nnn].md`
  - Target audience: junior developers
  - **Recommended for**: Refining existing PRDs or starting simple PRDs

- **`/prdresearch [idea]`** - PRD generation with integrated research (Experimental)
  - Combines `/prdgen` and `/research` in iterative cycles
  - Automatically invokes `@researcher` agent throughout process
  - Researches before questions, after answers, and after PRD changes
  - Outputs PRD and research files to `/context/[nnn]-{feature}/`
  - **⚠️ Note**: May require extra researcher calls (WIP)

- **`/research [topic]`** - Conduct comprehensive research on a topic or PRD
  - Reads through related code and documentation
  - Conducts web searches on frameworks and libraries
  - Identifies third-party types and alternative approaches
  - Outputs to `/context/[nnn]-{feature}/research-[nnn].md`
  - **Recommended for**: Main workflow research phase

- **`/plan [prd] [research]`** - Create detailed implementation plan
  - Identifies files that need changes
  - Lists new classes, functions, and test names
  - Includes specific tasks in checkbox format
  - Reinforces CLAUDE.md principles
  - Outputs to `/context/[nnn]-{feature}/plan-[nnn].md`

- **`/execute [plan]`** - Implement the plan with TDD and validation
  - Follows Test Driven Development practices
  - Marks tasks complete incrementally with commits
  - Runs full test suite before each commit
  - Tracks progress in `/context/{feature}/progress.md`

- **`/taskgen [prd]`** - Generate task list from a PRD
- **`/taskexec [tasks]`** - Execute a specific task list
- **`/explore [topic]`** - Alternative research command for gaining context, does not output to a file

### 🔍 Code Quality Commands

- **`/pragmatic-code-review`** - Conduct pragmatic code review on current branch
  - Focuses on practical concerns over theoretical perfection 🎯
  - Reviews pending changes systematically

- **`/design-review`** - Comprehensive UI/UX design review
  - Uses Playwright for automated browser testing 🎭
  - Validates accessibility and responsiveness ♿
  - Ensures world-class design standards ✨

- **`/simplify`** - Refactor and simplify existing code 🧹

### 🛠️ Utility Commands

- **`/crawl`** - Generate/update CLAUDE.md documentation files
  - Recursively documents codebase structure and patterns 🕷️
  - Updates after feature changes

- **`/pr`** - Create pull request with proper formatting 📬
- **`/next`** - Determine next steps in development workflow 🧭
- **`/quick`** - Quick task execution for simple changes ⚡

### 🎨 Custom Workflow Commands

- **`/my-developer-plan`** - Custom planning workflow
- **`/my-developer-review`** - Custom review workflow

## 🤝 Available Agents

Specialized agents provide focused capabilities for complex tasks:

### Core Development Agents
- **`@planner`** 🗺️ - Creates detailed implementation plans from PRDs and research
- **`@researcher`** 🔬 - Conducts comprehensive research and maintains research files
- **`@executer`** ⚡ - Implements code following strict TDD principles (used in main workflow)
- **`@iterator`** 🔄 - Iterative task execution with continuous review (experimental, for context partitioning)

### Review & Quality Agents
- **`@plan-reviewer`** 📋 - Reviews implementation plans with detailed feedback
- **`@pragmatic-code-review`** 🔍 - Pragmatic code quality assessment
- **`@design-review`** 🎨 - Automated UI/UX validation with browser testing

### Infrastructure & Documentation Agents
- **`@claude-crawler`** 🕷️ - Generates and maintains CLAUDE.md files
- **`@aws-cdk-agent`** ☁️ - AWS CDK infrastructure development

**Note**: Agents marked as "experimental" are part of the context-partitioning workflows. They execute in separate context windows to manage complexity.

## 📁 Context Management

The workflow uses a structured `/context/` directory to organize artifacts:

```
/context/
  [nnn]-{feature-name}/
    prd-[nnn].md          # Product requirements
    research-[nnn].md     # Research findings
    plan-[nnn].md         # Implementation plan
    progress.md           # Execution progress
```

This structure keeps all related materials together and enables easy reference across workflow stages.

## 💎 Development Principles

This workflow adheres to principles defined in `CLAUDE.md`:

- 🗑️ Delete more than you add - complexity compounds into disasters
- 🏗️ Follow SOLID and KISS principles
- 🚀 Assume MVP mindset for rapid iteration
- 🧠 Trust your research - don't read files repeatedly
- 💥 Fail fast and loud, not silently
- 🧪 Use Test Driven Development by default
- ✅ Validate every code block: lint, compile, test
- 🎯 Maximize code coverage quality, not just quantity

## 🧠 Context Window Management

A key theme in the roadmap is **managing context window size** to maintain peak Claude performance.

### The Challenge
As context windows grow with conversation history, file reads, and accumulated changes, Claude's performance can degrade. This manifests as:
- Slower response times
- Decreased code quality
- Higher likelihood of errors or missed requirements
- Difficulty maintaining coherence across large codebases

### The Solution: Context Partitioning
The experimental workflows explore executing work across **separate context windows**:

1. **Main context** - Orchestration, planning, and high-level oversight
2. **Agent contexts** - Focused execution of specific tasks or plans

**Benefits:**
- Each task/plan gets fresh, focused context
- Main context stays lean for strategic decisions
- Better performance on complex, multi-phase projects
- Easier to review and validate work in isolation

### Choosing Your Approach

**Use single context (main workflow)** when:
- Working on small to medium features
- You want maximum coherence across all phases
- The entire workflow fits comfortably in context
- You prefer direct control and visibility

**Use context partitioning (experimental)** when:
- Working on large, complex features
- Context window is approaching limits (200K+ tokens)
- You want to maintain peak performance across long sessions
- You're comfortable with agent-based orchestration

The goal is to provide flexibility: start with the simple single-context workflow, and graduate to context partitioning as your needs grow.

## 🌟 Inspirations & Resources

This workflow synthesizes ideas from several AI-assisted development approaches:

### 📦 Repository Resources

- **[ai-dev-tasks](https://github.com/snarktank/ai-dev-tasks)** by Ryan Carson - Structured markdown templates for breaking features into reviewable chunks
- **[claude-code-workflows](https://github.com/actiondavestep/claude-code-workflows)** by Patrick Ellis - Automated review workflows for code, security, and design

### 🎥 Video Resources

- **[Advanced Context Engineering for Agents](https://www.youtube.com/watch?v=VIDEO_ID)** - Dex Horthy (HumanLayer) at YC Root Access (Aug 25, 2025)
- **[Claude Code: Tips and Tricks](https://www.youtube.com/watch?v=hOqgFNlbrYE)** - Featuring Galen Ward's workflow ([Slides](https://docs.google.com/presentation/d/1TbgpuCJ8ZuulW4i1I0FE0xnArjivViEl/edit?slide=id.p1#slide=id.p1))

### 🔗 Other Resources

- **[The Ralph Wiggum Technique](https://ghuntley.com/ralph/)** by Geoffrey Huntley - Continuous automation loop for AI coding agents

## 🎯 Getting Started

Follow the **Core Workflow** for the best experience:

1. **⚙️ Set up your environment** - Ensure Claude Code is installed and configured

2. **📖 Review CLAUDE.md** - Understand the development principles

3. **💡 Create your PRD** - Generate a Product Requirements Document
   - Use Gemini Deep Research for complex features 🔬
   - Use `/prdgen [idea]` for interactive PRD generation ❓
   - Import from Jira or other tools 📋
   - Outputs to `/context/[nnn]-{feature}/prd-[nnn].md`

4. **🔍 Research** - Use `/research <prd.md>` to become a subject matter expert
   - Explores codebase and documentation 📚
   - Researches frameworks and libraries 🌐
   - Outputs to `/context/[nnn]-{feature}/research-[nnn].md`

5. **🗺️ Plan** - Use `/plan <prd.md> <research.md>` for detailed implementation plan
   - Identifies files, classes, functions needed 🏗️
   - Creates task checklist ✅
   - Outputs to `/context/[nnn]-{feature}/plan-[nnn].md`

6. **⚡ Execute** - Use `/execute <plan.md>` to implement with TDD
   - Incremental commits per task 🔄
   - Full test suite before each commit 🧪
   - Tracks progress in `/context/[nnn]-{feature}/progress.md`

7. **✅ Review** - Use review commands before merging
   - `/pragmatic-code-review` for code quality 🔍
   - `/design-review` for UI/UX validation 🎨

## 🏗️ Command Architecture

Commands are defined using markdown files with YAML frontmatter:

```yaml
---
allowed-tools: Bash, Glob, Grep, Read, Edit, Write
argument-hint: [topic]
description: Brief description of command purpose
---
```

The command body contains the prompt template with `$1`, `$2`, etc. for arguments.

## ⭐ Best Practices

- **🔄 Follow the Core Workflow** - PRD → `/research` → `/plan` → `/execute`
- **🧠 Trust your research** - Don't re-read files unnecessarily; reference research docs
- **✅ Validate incrementally** - Commit after each task completion, not in batches
- **🤝 Use agents strategically** - Let specialized agents handle complex subtasks
- **📁 Organize context** - Use `/context/[nnn]-{feature}/` structure consistently
- **💎 Reference principles** - Follow CLAUDE.md guidelines in all work
- **🧪 Test continuously** - Run full test suite before every commit
- **📏 Monitor context size** - Consider experimental workflows if context exceeds 200K tokens
- **🎯 Start simple** - Use main workflow first; graduate to context partitioning as needed

## 🧪 Testing

Test commands by:
1. Running with appropriate arguments
2. Verifying tool restrictions are respected
3. Checking output locations
4. Validating argument substitution

## 📚 Resources

- 📖 [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- ⚡ [Slash Commands Guide](https://docs.claude.com/en/docs/claude-code/slash-commands)
- 📟 Command definitions in `/commands/` directory
- 🤝 Agent definitions in `/agents/` directory
- 💎 Global principles in `CLAUDE.md`

## 📄 License

See `LICENSE` file for details.

## 🤝 Contributing

Contributions welcome! This is a living collection of workflows that evolves with experience and community input. 🌱
