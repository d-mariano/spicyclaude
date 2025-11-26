import { ClaudeCommandParser, ArgumentConverter, GeminiCommandGenerator, convertCommand, validateToml } from '../converter';
import { ClaudeCommand, GeminiCommand } from '../types';

describe('ClaudeCommandParser', () => {
  let parser: ClaudeCommandParser;

  beforeEach(() => {
    parser = new ClaudeCommandParser();
  });

  describe('parseMarkdown', () => {
    it('should parse claude markdown with yaml frontmatter', () => {
      const markdownContent = `---
allowed-tools: Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: "[topic]"
description: Explore relevant files and resources to gain enough context for a full understanding of the given PRD or topic.
---

You are an expert researcher and explorer. Your task is to thoroughly investigate $1 by examining all relevant files, documentation, and context within the codebase.

## Your Mission
Research and explore $1 comprehensively to provide full understanding of the topic.
`;

      const result = parser.parseMarkdown(markdownContent, 'explore');

      expect(result.metadata.description).toBe('Explore relevant files and resources to gain enough context for a full understanding of the given PRD or topic.');
      expect(result.metadata['allowed-tools']).toBe('Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch');
      expect(result.metadata['argument-hint']).toBe('[topic]');
      expect(result.prompt).toContain('Research and explore $1 comprehensively');
      expect(result.name).toBe('explore');
    });

    it('should handle markdown without argument-hint', () => {
      const markdownContent = `---
description: Simple command without arguments
---

Simple prompt content.
`;

      const result = parser.parseMarkdown(markdownContent, 'simple');

      expect(result.metadata.description).toBe('Simple command without arguments');
      expect(result.metadata['argument-hint']).toBeUndefined();
      expect(result.prompt).toBe('Simple prompt content.');
    });

    it('should throw error for markdown without description', () => {
      const markdownContent = `---
allowed-tools: Read, Write
---

Prompt content.
`;

      expect(() => {
        parser.parseMarkdown(markdownContent, 'invalid');
      }).toThrow('Command must have a description');
    });

    it('should throw error for invalid yaml frontmatter', () => {
      const markdownContent = `---
invalid: yaml: content:
---

Prompt content.
`;

      expect(() => {
        parser.parseMarkdown(markdownContent, 'invalid');
      }).toThrow();
    });
  });
});

describe('ArgumentConverter', () => {
  let converter: ArgumentConverter;

  beforeEach(() => {
    converter = new ArgumentConverter();
  });

  describe('convertArguments', () => {
    it('should convert single argument placeholder', () => {
      const prompt = 'Research and explore $1 comprehensively.';
      const result = converter.convertArguments(prompt);

      expect(result).toBe('Research and explore {{args}} comprehensively.');
    });

    it('should combine multiple arguments', () => {
      const prompt = 'Process $1 with settings $2 and output to $3.';
      const result = converter.convertArguments(prompt);

      expect(result).toBe('Process {{args}} with settings {{args}} and output to {{args}}.');
    });

    it('should handle prompt with no arguments', () => {
      const prompt = 'Simple command with no arguments.';
      const result = converter.convertArguments(prompt);

      expect(result).toBe('Simple command with no arguments.');
    });
  });
});

describe('GeminiCommandGenerator', () => {
  let generator: GeminiCommandGenerator;

  beforeEach(() => {
    generator = new GeminiCommandGenerator();
  });

  describe('generateToml', () => {
    it('should generate valid toml structure', () => {
      const geminiCommand: GeminiCommand = {
        description: 'Test command description',
        prompt: 'Test prompt with {{args}} placeholder'
      };

      const result = generator.generateToml(geminiCommand);

      expect(result).toContain('description = "Test command description"');
      expect(result).toContain('prompt = "Test prompt with {{args}} placeholder"');
    });
  });
});

describe('validateToml', () => {
  it('should validate correct TOML syntax', () => {
    const validToml = `description = "Test command"
prompt = "Test prompt"`;

    expect(validateToml(validToml)).toBe(true);
  });

  it('should throw error for invalid TOML syntax', () => {
    const invalidToml = `description = "Test command
prompt = invalid toml`;

    expect(() => validateToml(invalidToml)).toThrow('Invalid TOML syntax');
  });
});

describe('convertCommand', () => {
  it('should convert claude command to gemini toml', () => {
    const claudeMarkdown = `---
description: Explore relevant files and resources
---

Research and explore $1 comprehensively.`;

    const result = convertCommand(claudeMarkdown, 'explore');

    expect(result).toContain('description = "Explore relevant files and resources"');
    expect(result).toContain('prompt = "Research and explore {{args}} comprehensively."');
  });
});