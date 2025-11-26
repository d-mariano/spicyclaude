# Research: Claude Code to Gemini CLI Command Converter

## Claude Code Command Structure Analysis

### Format
Claude Code commands are defined as markdown files with YAML frontmatter:
```yaml
---
allowed-tools: Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: [topic]
description: Explore relevant files and resources to gain enough context for a full understanding of the given PRD or topic.
---
```

### Key Components
1. **allowed-tools**: Specifies which Claude Code tools the command can use
2. **argument-hint**: User-facing parameter hints (e.g., `[topic]`, `[prd] [research]`)
3. **description**: Brief explanation of command purpose
4. **Body**: Prompt template with `$1`, `$2`, etc. for argument substitution

### Current Commands (19 total)
- Development workflow: research, plan, execute, explore
- Code quality: pragmatic-code-review, design-review, simplify
- Utilities: crawl, pr, next, quick
- Custom workflows: my-developer-plan, my-developer-review
- Others: prdgen, prdresearch, taskexec, taskgen

### Data Flow Patterns
- Commands often use `/context/{feature|branch}/` output structure
- Common workflow: research → plan → execute
- Arguments passed as `$1`, `$2` in template

## Gemini CLI Custom Commands Structure

### Format
Gemini commands are defined as TOML files:
```toml
description="Brief explanation of command purpose"
prompt = """Template with {{args}} for argument injection"""
```

### Key Components
1. **description**: Brief explanation (similar to Claude Code)
2. **prompt**: Core instruction template
3. **{{args}}**: Argument placeholder (vs Claude's `$1`, `$2`)
4. **Special injections**: `!{...}` for shell, `@{...}` for files

### File Organization
- Global: `~/.gemini/commands/`
- Project-specific: `<project-root>/.gemini/commands/`
- Subdirectories create namespaces (e.g., `git/commit.toml` → `/git:commit`)

## Key Conversion Challenges

### 1. Format Differences
- **Source**: Markdown with YAML frontmatter
- **Target**: TOML format
- **Arguments**: `$1`, `$2` → `{{args}}`

### 2. Tool Restrictions
- Claude Code has granular tool restrictions via `allowed-tools`
- Gemini CLI doesn't have equivalent tool restriction mechanism
- Need to handle this conceptual difference

### 3. Output Patterns
- Claude Code uses structured `/context/` outputs
- Gemini CLI relies on shell commands for file operations
- Conversion may need to adapt file creation patterns

### 4. Argument Handling
- Claude Code: Multiple positional args (`$1`, `$2`)
- Gemini CLI: Single `{{args}}` string
- May need to restructure multi-argument commands

## Technical Implementation Requirements

### Package Structure
```
utils/
└── claude-to-gemini-converter/
    ├── package.json
    ├── tsconfig.json
    ├── src/
    │   ├── index.ts
    │   ├── converter.ts
    │   ├── types.ts
    │   └── templates/
    └── dist/
```

### Core Functionality Needed
1. **Parser**: Read Claude Code markdown files with YAML frontmatter
2. **Converter**: Transform Claude format to Gemini TOML format
3. **Argument Mapper**: Convert `$1`, `$2` to `{{args}}` patterns
4. **Output Generator**: Create `.gemini/commands/` structure
5. **CLI Interface**: Command-line tool for conversion

### Output Structure
Should generate a `.gemini/` or `gemini/` folder in the repo containing converted commands.

## User Requirements (Clarified)

Based on user feedback:
- **Scope**: Convert ALL 19 existing Claude Code commands (1A)
- **Arguments**: Combine all arguments into single `{{args}}` string (2A)
- **Package Type**: CLI tool installable via npm (3A)
- **Output**: `.gemini/` hidden folder (4A)
- **Tool Restrictions**: Ignore completely - Gemini CLI doesn't support this (5B)
- **Context Patterns**: Add file creation instructions to prompt text (6B)
- **Validation**: Basic TOML syntax validation only (7A)
- **Documentation**: Simple README for the converter (8A)