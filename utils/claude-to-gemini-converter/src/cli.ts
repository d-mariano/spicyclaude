import * as fs from 'fs/promises';
import * as path from 'path';
import { convertCommand, validateToml } from './converter';
import { ConversionResult, ConversionSummary } from './types';

/**
 * Process all Claude Code commands in a directory
 * @param inputDir - Directory containing Claude Code .md command files
 * @param outputDir - Directory to write Gemini CLI .toml files
 * @returns Summary of conversion results
 */
export async function processCommandsDirectory(
  inputDir: string,
  outputDir: string
): Promise<ConversionSummary> {
  // Check if input directory exists
  try {
    await fs.access(inputDir);
  } catch {
    throw new Error(`Commands directory not found: ${inputDir}`);
  }

  // Create output directory if it doesn't exist
  await fs.mkdir(outputDir, { recursive: true });

  // Get all .md files from input directory
  const files = await fs.readdir(inputDir);
  const commandFiles = files.filter(file => file.endsWith('.md'));

  if (commandFiles.length === 0) {
    throw new Error(`No command files found in ${inputDir}`);
  }

  const results: ConversionResult[] = [];

  // Process each command file
  for (const file of commandFiles) {
    const commandName = path.basename(file, '.md');
    const inputPath = path.join(inputDir, file);
    const outputPath = path.join(outputDir, `${commandName}.toml`);

    try {
      // Read Claude Code command file
      const content = await fs.readFile(inputPath, 'utf-8');

      // Convert to Gemini format
      const tomlContent = convertCommand(content, commandName);

      // Validate TOML syntax
      validateToml(tomlContent);

      // Write TOML file
      await fs.writeFile(outputPath, tomlContent, 'utf-8');

      results.push({
        commandName,
        success: true,
        tomlContent
      });

    } catch (error) {
      results.push({
        commandName,
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  // Generate summary
  const successfulConversions = results.filter(r => r.success).length;
  const failedConversions = results.filter(r => !r.success).length;

  return {
    totalCommands: commandFiles.length,
    successfulConversions,
    failedConversions,
    results
  };
}