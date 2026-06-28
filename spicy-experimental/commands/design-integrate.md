---
allowed-tools: AskUserQuestion, Read, Grep, Glob, Write, WebSearch, WebFetch
argument-hint: "<task description>"
description: Design a feature for an existing codebase — reconnaissance, strategy, integration design, review
---

I need to design a feature for the existing codebase:

$ARGUMENTS

Read and follow the workflow in `${CLAUDE_PLUGIN_ROOT}/skills/feature-integration/SKILL.md`. Execute from Phase 1, pausing after each phase for my review. Actually read the codebase during Phase 1 — use Grep, Glob, Read, and Bash to explore.

If the task involves significant restructuring or replacement of existing code, also read `${CLAUDE_PLUGIN_ROOT}/skills/refactor-modifier/SKILL.md` and apply its additions at each phase.
