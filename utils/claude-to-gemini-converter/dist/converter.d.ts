import { ClaudeCommand, GeminiCommand } from './types';
/**
 * Parses Claude Code markdown files with YAML frontmatter
 */
export declare class ClaudeCommandParser {
    /**
     * Parse a Claude Code markdown file
     * @param content - The markdown file content with YAML frontmatter
     * @param commandName - Name of the command file (without extension)
     * @returns Parsed Claude command structure
     */
    parseMarkdown(content: string, commandName: string): ClaudeCommand;
}
/**
 * Converts Claude Code argument patterns to Gemini CLI format
 */
export declare class ArgumentConverter {
    /**
     * Convert Claude Code argument placeholders ($1, $2, etc.) to Gemini format ({{args}})
     * @param prompt - The prompt content with Claude Code placeholders
     * @returns Prompt with Gemini CLI placeholders
     */
    convertArguments(prompt: string): string;
}
/**
 * Generates Gemini CLI TOML command files
 */
export declare class GeminiCommandGenerator {
    /**
     * Generate TOML content for a Gemini CLI command
     * @param geminiCommand - The Gemini command structure
     * @returns TOML string content
     */
    generateToml(geminiCommand: GeminiCommand): string;
}
/**
 * Main converter function that orchestrates the conversion process
 * @param content - Claude Code markdown content
 * @param commandName - Name of the command
 * @returns Generated TOML content
 */
export declare function convertCommand(content: string, commandName: string): string;
/**
 * Validates TOML syntax
 * @param tomlContent - TOML string to validate
 * @returns True if valid, throws error if invalid
 */
export declare function validateToml(tomlContent: string): boolean;
//# sourceMappingURL=converter.d.ts.map