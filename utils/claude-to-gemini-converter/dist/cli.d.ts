import { ConversionSummary } from './types';
/**
 * Process all Claude Code commands in a directory
 * @param inputDir - Directory containing Claude Code .md command files
 * @param outputDir - Directory to write Gemini CLI .toml files
 * @returns Summary of conversion results
 */
export declare function processCommandsDirectory(inputDir: string, outputDir: string): Promise<ConversionSummary>;
//# sourceMappingURL=cli.d.ts.map