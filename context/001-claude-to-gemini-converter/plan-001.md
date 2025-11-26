# Implementation Plan: Claude Code to Gemini CLI Command Converter

## Overview

We're building a TypeScript CLI package that converts Claude Code's markdown-based commands to Gemini CLI's TOML format. This enables users familiar with Claude Code workflows to seamlessly transition to Gemini CLI without manually rewriting their 19 existing commands.

The converter will be an npm-installable standalone CLI tool that:
- Parses Claude Code markdown files with YAML frontmatter
- Converts `$1`, `$2` arguments to `{{args}}` format
- Generates valid TOML files in `.gemini/commands/` directory
- Provides conversion status and summary output

This is an MVP focused on functional conversion without over-engineering abstractions or unnecessary error handling complexity.

## Files to Create/Modify

### New Package Structure
- `utils/claude-to-gemini-converter/` - Standalone npm package
- `utils/claude-to-gemini-converter/package.json` - Package configuration with CLI bin
- `utils/claude-to-gemini-converter/tsconfig.json` - TypeScript configuration
- `utils/claude-to-gemini-converter/src/index.ts` - CLI entry point
- `utils/claude-to-gemini-converter/src/converter.ts` - Core conversion logic
- `utils/claude-to-gemini-converter/src/types.ts` - Type definitions
- `utils/claude-to-gemini-converter/README.md` - Usage documentation

### Test Files
- `utils/claude-to-gemini-converter/src/__tests__/converter.test.ts` - Core conversion tests
- `utils/claude-to-gemini-converter/src/__tests__/cli.test.ts` - CLI interface tests

## Key Classes and Functions

### `ClaudeCommandParser` class
Parses Claude Code markdown files with YAML frontmatter to extract command metadata (description, arguments) and prompt content.

### `GeminiCommandGenerator` class
Converts parsed Claude command data into valid TOML format with proper escaping and structure.

### `ArgumentConverter` class
Transforms Claude Code argument patterns (`$1`, `$2`) into Gemini CLI format (`{{args}}`), handling multi-argument consolidation.

### `convertCommand()` function
Main conversion function that orchestrates parsing, transformation, and generation for a single command file.

### `processCommandsDirectory()` function
Processes all `.md` files in `/commands` directory, calls convertCommand for each, and generates summary output.

### `validateToml()` function
Basic TOML syntax validation using `@iarna/toml` parser to ensure generated files are syntactically correct.

## Test Coverage

### Core Conversion Tests (`converter.test.ts`)
- `should parse claude markdown with yaml frontmatter` - extracts metadata correctly
- `should convert single argument placeholder` - transforms `$1` to `{{args}}`
- `should combine multiple arguments` - merges `$1 $2` to single `{{args}}`
- `should generate valid toml structure` - creates proper TOML format
- `should preserve command descriptions` - maintains frontmatter descriptions
- `should handle context patterns` - converts `/context/` instructions to text

### CLI Interface Tests (`cli.test.ts`)
- `should process commands directory` - finds and converts all commands
- `should create gemini directory structure` - generates `.gemini/commands/`
- `should output conversion summary` - displays "Converted X commands successfully"
- `should handle missing commands directory` - graceful error for missing `/commands`
- `should validate generated toml files` - ensures output passes TOML validation

## CLAUDE.md Adherence

- **Delete more than add**: Reusing existing npm packages (`js-yaml`, `@iarna/toml`, `commander.js`) instead of building from scratch
- **SOLID principles**: Single responsibility classes for parsing, converting, and generating
- **KISS**: Simple CLI interface with single `convert` command, no complex configuration
- **Fail fast and loud**: Direct error reporting for missing directories or invalid files
- **No unnecessary abstractions**: Direct file processing without over-engineered interfaces
- **Third-party types**: Using existing YAML/TOML library types instead of creating custom ones

## Dependencies

- `js-yaml`: Parse Claude Code YAML frontmatter
- `@iarna/toml`: Generate and validate TOML files
- `commander.js`: CLI framework for argument parsing
- `@types/js-yaml`: TypeScript definitions
- Node.js built-in `fs/promises`: File system operations

## Tasks

- [ ] 1.0 Setup Package Structure
  - [ ] 1.1 Create package directory and package.json with CLI bin configuration
  - [ ] 1.2 Setup TypeScript configuration and build scripts
  - [ ] 1.3 Install required dependencies (js-yaml, @iarna/toml, commander.js)

- [ ] 2.0 Implement Core Conversion Logic
  - [ ] 2.1 Create ClaudeCommandParser class to parse markdown with YAML frontmatter
  - [ ] 2.2 Create ArgumentConverter class to transform $1, $2 to {{args}} format
  - [ ] 2.3 Create GeminiCommandGenerator class to output valid TOML structure
  - [ ] 2.4 Implement validateToml function for basic syntax validation

- [ ] 3.0 Build CLI Interface
  - [ ] 3.1 Create CLI entry point with commander.js convert command
  - [ ] 3.2 Implement processCommandsDirectory function to batch process commands
  - [ ] 3.3 Add conversion status output and summary reporting

- [ ] 4.0 Test Implementation
  - [ ] 4.1 Write unit tests for core conversion logic with RED/GREEN TDD
  - [ ] 4.2 Write CLI integration tests for end-to-end workflow
  - [ ] 4.3 Test with actual Claude Code commands from /commands directory

- [ ] 5.0 Documentation and Distribution
  - [ ] 5.1 Create README with installation and usage instructions
  - [ ] 5.2 Build TypeScript to JavaScript for distribution
  - [ ] 5.3 Test npm installation and global CLI availability