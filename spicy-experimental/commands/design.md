---
allowed-tools: AskUserQuestion, Read, Grep, Glob, Write, WebSearch, WebFetch
argument-hint: "<task description>"
description: Design workflow router — detects your codebase and task, recommends the right workflow
---

I need to create a technical design for the following task:

$ARGUMENTS

Before starting, determine the right workflow:

1. Check if an existing codebase is present in the working directory. Look for package manifests, src directories, and code files.

2. Classify the task:
   - **Greenfield**: No relevant codebase, or building an entirely new system/service → Read and follow `${CLAUDE_PLUGIN_ROOT}/skills/greenfield-design/SKILL.md`
   - **Feature Integration**: Adding to an existing codebase, preserving existing patterns → Read and follow `${CLAUDE_PLUGIN_ROOT}/skills/feature-integration/SKILL.md`
   - **Greenfield + Refactor**: Rebuilding a system from scratch with migration from the old → Read `${CLAUDE_PLUGIN_ROOT}/skills/greenfield-design/SKILL.md` AND `${CLAUDE_PLUGIN_ROOT}/skills/refactor-modifier/SKILL.md`, apply the modifier's additions at each phase
   - **Integration + Refactor**: Restructuring within an existing system → Read `${CLAUDE_PLUGIN_ROOT}/skills/feature-integration/SKILL.md` AND `${CLAUDE_PLUGIN_ROOT}/skills/refactor-modifier/SKILL.md`, apply the modifier's additions at each phase

3. Present your classification to me with reasoning. Ask me to confirm or override before proceeding.

4. Once confirmed, execute the selected workflow from Phase 1, pausing after each phase for my review.
