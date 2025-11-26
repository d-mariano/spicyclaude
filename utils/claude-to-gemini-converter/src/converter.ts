import * as yaml from 'js-yaml';
import * as TOML from '@iarna/toml';
import { ClaudeCommand, ClaudeCommandMetadata, GeminiCommand } from './types';

/**
 * Parses Claude Code markdown files with YAML frontmatter
 */
export class ClaudeCommandParser {
  /**
   * Parse a Claude Code markdown file
   * @param content - The markdown file content with YAML frontmatter
   * @param commandName - Name of the command file (without extension)
   * @returns Parsed Claude command structure
   */
  parseMarkdown(content: string, commandName: string): ClaudeCommand {
    // Split frontmatter from content
    const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);

    if (!frontmatterMatch) {
      throw new Error('Invalid markdown format: missing YAML frontmatter');
    }

    const [, frontmatterStr, promptContent] = frontmatterMatch;

    // Parse YAML frontmatter
    let metadata: ClaudeCommandMetadata;
    try {
      metadata = yaml.load(frontmatterStr) as ClaudeCommandMetadata;
    } catch (error) {
      throw new Error(`Invalid YAML frontmatter: ${error}`);
    }

    // Validate required fields
    if (!metadata.description) {
      throw new Error('Command must have a description');
    }

    return {
      metadata,
      prompt: promptContent.trim(),
      name: commandName
    };
  }
}

/**
 * Converts Claude Code argument patterns to Gemini CLI format
 */
export class ArgumentConverter {
  /**
   * Convert Claude Code argument placeholders ($1, $2, etc.) to Gemini format ({{args}})
   * @param prompt - The prompt content with Claude Code placeholders
   * @returns Prompt with Gemini CLI placeholders
   */
  convertArguments(prompt: string): string {
    // Replace $1, $2, $3, etc. with {{args}}
    // For simplicity, we'll replace all argument placeholders with a single {{args}}
    return prompt.replace(/\$\d+/g, '{{args}}');
  }
}

/**
 * Generates Gemini CLI TOML command files
 */
export class GeminiCommandGenerator {
  /**
   * Generate TOML content for a Gemini CLI command
   * @param geminiCommand - The Gemini command structure
   * @returns TOML string content
   */
  generateToml(geminiCommand: GeminiCommand): string {
    const tomlData = {
      description: geminiCommand.description,
      prompt: geminiCommand.prompt
    };

    return TOML.stringify(tomlData);
  }
}

/**
 * Main converter function that orchestrates the conversion process
 * @param content - Claude Code markdown content
 * @param commandName - Name of the command
 * @returns Generated TOML content
 */
export function convertCommand(content: string, commandName: string): string {
  const parser = new ClaudeCommandParser();
  const argumentConverter = new ArgumentConverter();
  const generator = new GeminiCommandGenerator();

  // Parse Claude command
  const claudeCommand = parser.parseMarkdown(content, commandName);

  // Convert arguments
  const convertedPrompt = argumentConverter.convertArguments(claudeCommand.prompt);

  // Create Gemini command structure
  const geminiCommand: GeminiCommand = {
    description: claudeCommand.metadata.description,
    prompt: convertedPrompt
  };

  // Generate TOML
  return generator.generateToml(geminiCommand);
}

/**
 * Validates TOML syntax
 * @param tomlContent - TOML string to validate
 * @returns True if valid, throws error if invalid
 */
export function validateToml(tomlContent: string): boolean {
  try {
    TOML.parse(tomlContent);
    return true;
  } catch (error) {
    throw new Error(`Invalid TOML syntax: ${error}`);
  }
}