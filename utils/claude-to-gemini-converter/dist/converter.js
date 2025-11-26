"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.GeminiCommandGenerator = exports.ArgumentConverter = exports.ClaudeCommandParser = void 0;
exports.convertCommand = convertCommand;
exports.validateToml = validateToml;
const yaml = __importStar(require("js-yaml"));
const TOML = __importStar(require("@iarna/toml"));
/**
 * Parses Claude Code markdown files with YAML frontmatter
 */
class ClaudeCommandParser {
    /**
     * Parse a Claude Code markdown file
     * @param content - The markdown file content with YAML frontmatter
     * @param commandName - Name of the command file (without extension)
     * @returns Parsed Claude command structure
     */
    parseMarkdown(content, commandName) {
        // Split frontmatter from content
        const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);
        if (!frontmatterMatch) {
            throw new Error('Invalid markdown format: missing YAML frontmatter');
        }
        const [, frontmatterStr, promptContent] = frontmatterMatch;
        // Parse YAML frontmatter
        let metadata;
        try {
            metadata = yaml.load(frontmatterStr);
        }
        catch (error) {
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
exports.ClaudeCommandParser = ClaudeCommandParser;
/**
 * Converts Claude Code argument patterns to Gemini CLI format
 */
class ArgumentConverter {
    /**
     * Convert Claude Code argument placeholders ($1, $2, etc.) to Gemini format ({{args}})
     * @param prompt - The prompt content with Claude Code placeholders
     * @returns Prompt with Gemini CLI placeholders
     */
    convertArguments(prompt) {
        // Replace $1, $2, $3, etc. with {{args}}
        // For simplicity, we'll replace all argument placeholders with a single {{args}}
        return prompt.replace(/\$\d+/g, '{{args}}');
    }
}
exports.ArgumentConverter = ArgumentConverter;
/**
 * Generates Gemini CLI TOML command files
 */
class GeminiCommandGenerator {
    /**
     * Generate TOML content for a Gemini CLI command
     * @param geminiCommand - The Gemini command structure
     * @returns TOML string content
     */
    generateToml(geminiCommand) {
        const tomlData = {
            description: geminiCommand.description,
            prompt: geminiCommand.prompt
        };
        return TOML.stringify(tomlData);
    }
}
exports.GeminiCommandGenerator = GeminiCommandGenerator;
/**
 * Main converter function that orchestrates the conversion process
 * @param content - Claude Code markdown content
 * @param commandName - Name of the command
 * @returns Generated TOML content
 */
function convertCommand(content, commandName) {
    const parser = new ClaudeCommandParser();
    const argumentConverter = new ArgumentConverter();
    const generator = new GeminiCommandGenerator();
    // Parse Claude command
    const claudeCommand = parser.parseMarkdown(content, commandName);
    // Convert arguments
    const convertedPrompt = argumentConverter.convertArguments(claudeCommand.prompt);
    // Create Gemini command structure
    const geminiCommand = {
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
function validateToml(tomlContent) {
    try {
        TOML.parse(tomlContent);
        return true;
    }
    catch (error) {
        throw new Error(`Invalid TOML syntax: ${error}`);
    }
}
//# sourceMappingURL=converter.js.map