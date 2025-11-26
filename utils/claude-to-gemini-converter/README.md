# Claude Code to Gemini CLI Converter

A TypeScript CLI tool that converts Claude Code commands to Gemini CLI TOML format, enabling seamless workflow transition between AI coding assistants.

## Features

- 🔄 **Complete Conversion**: Converts Claude Code markdown commands to Gemini CLI TOML format
- 📁 **Batch Processing**: Processes entire command directories at once
- ✅ **Validation**: Built-in TOML syntax validation
- 📊 **Progress Reporting**: Clear conversion status and error reporting
- 🛡️ **Error Handling**: Continues processing even if individual files fail

## Installation

### Global Installation
```bash
npm install -g @spicyclaude/claude-to-gemini-converter
```

### Local Installation
```bash
npm install @spicyclaude/claude-to-gemini-converter
```

## Usage

### Basic Usage
Convert all Claude Code commands in the default `./commands` directory:

```bash
claude-to-gemini convert
```

### Custom Directories
Specify custom input and output directories:

```bash
claude-to-gemini convert --input ./my-commands --output ./gemini-commands
```

### Options
- `-i, --input <dir>`: Input directory containing Claude Code commands (default: `./commands`)
- `-o, --output <dir>`: Output directory for Gemini commands (default: `./.gemini/commands`)
- `-h, --help`: Show help information

## How It Works

The converter performs the following transformations:

### 1. YAML Frontmatter → TOML Structure
**Claude Code format:**
```yaml
---
allowed-tools: Read, Write, Grep
argument-hint: "[topic]"
description: Explore relevant files and resources
---
```

**Gemini CLI format:**
```toml
description = "Explore relevant files and resources"
```

### 2. Argument Placeholder Conversion
- Claude Code: `$1`, `$2`, `$3`, etc.
- Gemini CLI: `{{args}}`

**Example:**
```
Input:  "Research $1 and analyze $2"
Output: "Research {{args}} and analyze {{args}}"
```

### 3. File Structure
- **Input**: `./commands/explore.md`
- **Output**: `./.gemini/commands/explore.toml`

## Example Conversion

**Input: `explore.md`**
```markdown
---
allowed-tools: Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: "[topic]"
description: Explore relevant files and resources to gain enough context for a full understanding of the given PRD or topic.
---

We are going to work on $1.

Dig in, read relevant files, and prepare to discuss the ins and outs of how it works.
```

**Output: `explore.toml`**
```toml
description = "Explore relevant files and resources to gain enough context for a full understanding of the given PRD or topic."
prompt = """
We are going to work on {{args}}.

Dig in, read relevant files, and prepare to discuss the ins and outs of how it works."""
```

## Error Handling

The converter handles various error scenarios gracefully:

- **Missing directories**: Clear error messages for non-existent input directories
- **Invalid YAML**: Detailed parsing error information
- **Malformed files**: Continues processing other files when individual conversions fail
- **TOML validation**: Ensures generated files have valid TOML syntax

## Development

### Setup
```bash
git clone <repository>
cd claude-to-gemini-converter
npm install
```

### Testing
```bash
npm test          # Run all tests
npm test:watch    # Watch mode
```

### Building
```bash
npm run build     # Build TypeScript to JavaScript
```

## Requirements

- Node.js ≥ 18.0.0
- NPM or Yarn

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

**Note**: This converter focuses on functional equivalence. Some Claude Code features like `allowed-tools` restrictions are not supported in Gemini CLI and are omitted from the conversion.