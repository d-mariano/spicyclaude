---
name: code-review-light
description: "Fast single-pass code review of a PR or branch diff. One consolidated read-only pass against the shared severity rubric, printing a severity-tiered summary. No subagents, no posting. Use for a quick gut-check; reach for review-heavy when you want the full multi-reviewer fan-out."
allowed-tools: Bash(gh *), Bash(git *), Read, Grep, Glob
context: fork
agent: Explore
argument-hint: "[pr-number | branch]"
---

# Code Review (Light)

A single read-only pass over a diff. You run in a forked Explore context — no conversation history, read-only tools. Pull the diff, review it once against the shared rubric, and print a severity-tiered summary. **No subagents. Do not post, approve, or merge.**

## Working diff (default scope)

- Changed files: !`git diff --name-only --merge-base origin/HEAD 2>/dev/null`
- Diff: !`git diff --merge-base origin/HEAD 2>/dev/null`

If `$ARGUMENTS` names a **PR number**, ignore the injected diff above and use `gh pr view <n> --json title,body` + `gh pr diff <n>` instead. If it names a **branch**, diff that branch against `origin/HEAD`.

## Pass

Review **only the changed code**. Run one consolidated pass covering the same ground the heavy reviewers split up — intent alignment, security, over-engineering, documentation — but in a single sweep. Score each finding with `severity` + `confidence` (0–100), `file:line`, and a concrete fix per `.claude/skills/review-heavy/references/severity-rubric.md`. Drop anything below **confidence 80**, and suppress everything in `.claude/skills/review-heavy/references/what-not-to-flag.md`.

## Output

Print a severity-tiered summary to the terminal:

```
## Code Review (Light) — <scope>

### Critical
- `file:line` — finding (confidence) → fix

### High
...

### Medium
...

### Low
...
```

Omit empty tiers. If nothing survives the gate, say so plainly. This is a fast gut-check — for the full multi-reviewer treatment and a formal verdict, use `/review-heavy`.
