/**
 * Types for Claude Code to Gemini CLI converter
 */
/** Claude Code command metadata from YAML frontmatter */
export interface ClaudeCommandMetadata {
    /** Tools that the command is allowed to use */
    'allowed-tools'?: string;
    /** Hint for command arguments shown to user */
    'argument-hint'?: string;
    /** Description of what the command does */
    description: string;
}
/** Parsed Claude Code command structure */
export interface ClaudeCommand {
    /** Metadata from YAML frontmatter */
    metadata: ClaudeCommandMetadata;
    /** Main prompt content */
    prompt: string;
    /** Original filename without extension */
    name: string;
}
/** Gemini CLI command structure */
export interface GeminiCommand {
    /** Description of what the command does */
    description: string;
    /** Prompt template with {{args}} placeholders */
    prompt: string;
}
/** Conversion result for a single command */
export interface ConversionResult {
    /** Original command name */
    commandName: string;
    /** Whether conversion succeeded */
    success: boolean;
    /** Error message if conversion failed */
    error?: string;
    /** Generated TOML content */
    tomlContent?: string;
}
/** Summary of batch conversion operation */
export interface ConversionSummary {
    /** Total commands processed */
    totalCommands: number;
    /** Successfully converted commands */
    successfulConversions: number;
    /** Failed conversions */
    failedConversions: number;
    /** List of conversion results */
    results: ConversionResult[];
}
//# sourceMappingURL=types.d.ts.map