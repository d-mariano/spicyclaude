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
exports.processCommandsDirectory = processCommandsDirectory;
const fs = __importStar(require("fs/promises"));
const path = __importStar(require("path"));
const converter_1 = require("./converter");
/**
 * Process all Claude Code commands in a directory
 * @param inputDir - Directory containing Claude Code .md command files
 * @param outputDir - Directory to write Gemini CLI .toml files
 * @returns Summary of conversion results
 */
async function processCommandsDirectory(inputDir, outputDir) {
    // Check if input directory exists
    try {
        await fs.access(inputDir);
    }
    catch {
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
    const results = [];
    // Process each command file
    for (const file of commandFiles) {
        const commandName = path.basename(file, '.md');
        const inputPath = path.join(inputDir, file);
        const outputPath = path.join(outputDir, `${commandName}.toml`);
        try {
            // Read Claude Code command file
            const content = await fs.readFile(inputPath, 'utf-8');
            // Convert to Gemini format
            const tomlContent = (0, converter_1.convertCommand)(content, commandName);
            // Validate TOML syntax
            (0, converter_1.validateToml)(tomlContent);
            // Write TOML file
            await fs.writeFile(outputPath, tomlContent, 'utf-8');
            results.push({
                commandName,
                success: true,
                tomlContent
            });
        }
        catch (error) {
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
//# sourceMappingURL=cli.js.map