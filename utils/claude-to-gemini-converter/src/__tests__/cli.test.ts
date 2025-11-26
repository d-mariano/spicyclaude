import * as fs from 'fs/promises';
import * as path from 'path';
import { processCommandsDirectory } from '../cli';

// Mock fs module
jest.mock('fs/promises');
const mockedFs = fs as jest.Mocked<typeof fs>;

describe('CLI', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('processCommandsDirectory', () => {
    it('should process commands directory successfully', async () => {
      // Mock directory access
      mockedFs.access.mockResolvedValue(undefined);

      // Mock readdir to return command files
      mockedFs.readdir.mockResolvedValue(['explore.md', 'plan.md'] as any);

      // Mock mkdir for output directory
      mockedFs.mkdir.mockResolvedValue(undefined as any);

      // Mock file reads
      const exploreContent = `---
description: Explore relevant files
---

Research and explore $1 comprehensively.`;

      const planContent = `---
description: Create implementation plan
---

Plan the implementation of $1.`;

      mockedFs.readFile
        .mockResolvedValueOnce(exploreContent)
        .mockResolvedValueOnce(planContent);

      // Mock file writes
      mockedFs.writeFile.mockResolvedValue(undefined);

      const result = await processCommandsDirectory('./commands', './.gemini/commands');

      expect(result.totalCommands).toBe(2);
      expect(result.successfulConversions).toBe(2);
      expect(result.failedConversions).toBe(0);
      expect(result.results).toHaveLength(2);
      expect(result.results[0].success).toBe(true);
      expect(result.results[1].success).toBe(true);
    });

    it('should handle missing commands directory', async () => {
      mockedFs.access.mockRejectedValue(new Error('ENOENT'));

      await expect(processCommandsDirectory('./nonexistent', './.gemini/commands'))
        .rejects.toThrow('Commands directory not found: ./nonexistent');
    });

    it('should handle directory with no command files', async () => {
      mockedFs.access.mockResolvedValue(undefined);
      mockedFs.readdir.mockResolvedValue(['README.txt', 'other.json'] as any);

      await expect(processCommandsDirectory('./empty', './.gemini/commands'))
        .rejects.toThrow('No command files found in ./empty');
    });

    it('should continue processing other files if individual conversion fails', async () => {
      mockedFs.access.mockResolvedValue(undefined);
      mockedFs.readdir.mockResolvedValue(['good.md', 'bad.md'] as any);
      mockedFs.mkdir.mockResolvedValue(undefined as any);

      const goodContent = `---
description: Good command
---

Valid prompt.`;

      const badContent = `---
# Invalid YAML
---

Prompt.`;

      mockedFs.readFile
        .mockResolvedValueOnce(goodContent)
        .mockResolvedValueOnce(badContent);

      mockedFs.writeFile.mockResolvedValue(undefined);

      const result = await processCommandsDirectory('./mixed', './.gemini/commands');

      expect(result.totalCommands).toBe(2);
      expect(result.successfulConversions).toBe(1);
      expect(result.failedConversions).toBe(1);
      expect(result.results[0].success).toBe(true);
      expect(result.results[1].success).toBe(false);
      expect(result.results[1].error).toBeDefined();
    });
  });
});