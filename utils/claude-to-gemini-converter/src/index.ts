#!/usr/bin/env node

import { Command } from 'commander';
import { processCommandsDirectory } from './cli';

const program = new Command();

program
  .name('claude-to-gemini')
  .description('Convert Claude Code commands to Gemini CLI format')
  .version('1.0.0');

program
  .command('convert')
  .description('Convert all Claude Code commands to Gemini CLI TOML format')
  .option('-i, --input <dir>', 'Input directory containing Claude Code commands', './commands')
  .option('-o, --output <dir>', 'Output directory for Gemini commands', './.gemini/commands')
  .action(async (options) => {
    try {
      const summary = await processCommandsDirectory(options.input, options.output);

      console.log(`\n✅ Conversion Complete!`);
      console.log(`📁 Processed ${summary.totalCommands} commands`);
      console.log(`✅ Successfully converted ${summary.successfulConversions} commands`);

      if (summary.failedConversions > 0) {
        console.log(`❌ Failed to convert ${summary.failedConversions} commands`);
        console.log('\nFailed conversions:');
        summary.results
          .filter(result => !result.success)
          .forEach(result => {
            console.log(`  - ${result.commandName}: ${result.error}`);
          });
      }

      console.log(`\n📂 Output directory: ${options.output}`);
    } catch (error) {
      console.error('❌ Conversion failed:', error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse();