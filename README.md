# 🌶️ Spicy Claude

A comprehensive collection of slash commands, agents, and workflows for Claude Code that implements a structured, iterative approach to AI-assisted software development. ✨

## 🤖 Overview

This repository provides a complete workflow system for building features with Claude Code, from initial ideation through implementation and validation. The workflow emphasizes structured planning, incremental development, and continuous validation to maximize code quality while maintaining developer control.

## 💎 Core Philosophy: CLAUDE.md

All workflows, commands, and agents in this repository are guided by the principles defined in `CLAUDE.md`. This file serves as the **foundation for code quality** and decision-making throughout development.

### Key Principles

**SOLID & KISS Above All**
- Follow SOLID principles (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
- Keep It Simple Stupid (KISS) - pragmatic solutions over clever complexity
- Delete more code than you add - complexity compounds into disasters
- One class per file, avoid unnecessary abstractions

**Test Driven Development (TDD)**
- Plan → Execute → Validate → Repeat
- Validate both RED and GREEN phases
- Tests are another version of product requirements
- Run full test suite before every commit

**Validation at Every Step**
- Lint, compile, and test every code block immediately after writing
- Fail fast and loud, never silently
- Use type-checkers and static analysis tools
- Break implementation into logical pieces by component or concern

**Avoiding Code Slop**
- Delete unused imports, code, and dependencies
- Don't create types/abstractions if third-party ones exist
- No backwards compatibility unless explicitly requested
- Avoid unnecessary try/catch blocks and error wrapping
- Trust your research - don't re-read files repeatedly

**MVP Mindset**
- Assume rapidly iterative startup, not enterprise
- Be pragmatic - only do things that provide immediate benefit
- Don't over-engineer for hypothetical future needs

Every command and agent reinforces these principles. When in doubt, consult `CLAUDE.md`.

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

## 📟 Slash Commands

Slash commands are user-defined operations that expand to full prompts for consistent, specialized task execution.

### Core Workflow Commands
- **`/prdgen [idea]`** - Generate PRD interactively
- **`/prdresearch [idea]`** - PRD generation with integrated research (Experimental)
- **`/research [topic]`** - Comprehensive research on topic or PRD ⭐ **Main workflow**
- **`/plan [prd] [research]`** - Create detailed implementation plan ⭐ **Main workflow**
- **`/execute [plan]`** - Implement with TDD and validation ⭐ **Main workflow**
- **`/taskgen [prd]`** - Generate task list from PRD
- **`/taskexec [tasks]`** - Execute specific task list
- **`/explore [topic]`** - Quick exploration without formal output

### Code Quality Commands
- **`/pragmatic-code-review`** - Pragmatic code review on current branch
- **`/design-review`** - UI/UX design review with automated testing
- **`/simplify`** - Refactor and simplify code

### Utility Commands
- **`/crawl`** - Generate/update CLAUDE.md documentation
- **`/pr`** - Create pull request
- **`/next`** - Determine next steps
- **`/quick`** - Quick task execution

### Custom Commands
- **`/my-developer-plan`** - Custom planning workflow
- **`/my-developer-review`** - Custom review workflow

**📚 For detailed documentation**, see [`commands/README.md`](commands/README.md)

## 🤝 Agents

Specialized agents are autonomous sub-processes that handle complex, focused tasks in separate context windows. The experimental workflows lean on subagents for the sole purpose of context windowm management.

### Core Development Agents
- **`@planner`** 🗺️ - Creates implementation plans from PRDs and research
- **`@researcher`** 🔬 - Conducts research and maintains research files ⭐ **Main workflow**
- **`@executer`** ⚡ - Implements code with strict TDD ⭐ **Main workflow**
- **`@iterator`** 🔄 - Iterative execution with review (Experimental)

### Review & Quality Agents
- **`@plan-reviewer`** 📋 - Reviews implementation plans with detailed feedback
- **`@pragmatic-code-review`** 🔍 - Pragmatic code quality assessment
- **`@design-review`** 🎨 - Automated UI/UX validation with browser testing

### Infrastructure & Documentation
- **`@claude-crawler`** 🕷️ - Generates and maintains CLAUDE.md files
- **`@aws-cdk-agent`** ☁️ - AWS CDK infrastructure development

**📚 For detailed documentation**, see [`agents/README.md`](agents/README.md)

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

## 🧠 Context Window Management

A key theme in the roadmap for evolving these workflows is **managing context window size** to maintain peak Claude performance. We should aim to give enough context to Claude...no more, no less.

### The Challenge
As context window grows with conversation history, file reads, and accumulated changes. Claude's performance, or any LLM, can degrade when the context window becomes too large. This manifests as:
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

### Claude Code Documentation
- 📖 [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- ⚡ [Slash Commands Guide](https://docs.claude.com/en/docs/claude-code/slash-commands)
- 🔧 [Agent Best Practices](https://docs.claude.com/en/docs/claude-code/agents)

## 🌶️ Enhanced Statusline

This repository includes a custom statusline script that provides real-time context monitoring during development.

*See [settings.json](settings.json) for reference to [statusline.sh](statusline.sh).*

**What it displays**:
- ⏰ Current time and user
- 📁 Current directory
- 🌳 Git branch with status (clean/dirty)
- 🤖 Model name (e.g., Sonnet 4.5)
- 🧠 **Context usage**: Current tokens / 200K limit with percentage
  - 🟢 Green (< 16%)
  - 🟡 Yellow (16-50%)
  - 🟠 Orange (50-80%)
  - 🔴 Red (≥ 80%) - **Consider experimental workflows!**
- 💰 Session cost

**Why context monitoring matters**:
- Avoid performance degradation from oversized contexts
- Make informed decisions about workflow strategy
- Know when to try to context-partitioned execution (at ~200K tokens)

The statusline script calculates context from the transcript file, matching how Claude Code tracks usage internally. See [statusline.sh](statusline.sh) for implementation details.

## 📄 License

See `LICENSE` file for details.

## 🤝 Contributing

Contributions welcome! This is a living collection of workflows that evolves with experience and community input. 🌱
