---
name: review-heavy
description: "Multi-reviewer code review. Fans out a PR or branch diff to specialized read-only reviewer subagents (mental-alignment, security, code-quality, documentation) in parallel, aggregates with a confidence gate, and prints one severity-tiered report with a verdict. Never posts, never approves."
allowed-tools: Bash(gh *), Bash(git *), Read, Grep, Glob, Write, Task, mcp__atlassian__getJiraIssue, mcp__atlassian__getAccessibleAtlassianResources
disable-model-invocation: true
argument-hint: "[pr-number | branch | files]"
---

# Review (Heavy)

Orchestrate a multi-reviewer pass over a diff. You fetch context **once**, fan out to four read-only reviewer subagents in parallel, then aggregate. **Print to the terminal only — never post to GitHub, never approve or merge.** The human is the approver.

## 1. Resolve scope

From `$ARGUMENTS`:
- **PR number** (e.g. `123`) → review that PR.
- **Branch name** → diff it against the base (`origin/HEAD` or the repo default).
- **File set / paths** → review only those files in the working diff.
- **Empty** → review the current branch against `origin/HEAD`.

## 2. Fetch context once

Gather everything the reviewers need a single time so the diff isn't duplicated four times:

- **Diff + PR metadata:** `gh pr view <n> --json title,body` and `gh pr diff <n>` for a PR; otherwise `git diff --merge-base origin/HEAD`.
- **Jira ticket:** extract the ticket key (e.g. `ABC-123`) from the branch name or PR title. If found, fetch the issue (description + acceptance criteria) via the Atlassian MCP — resolve the site with `mcp__atlassian__getAccessibleAtlassianResources`, then `mcp__atlassian__getJiraIssue`. (API-token auth; the server prefix must match your configured Atlassian MCP server.) **If Jira is unreachable or no key is found, degrade gracefully** to PR-description-only and record that fact in the context file.

Write the assembled context to a temp file — create one with `mktemp` (e.g. `$(mktemp -d)/review-context.md`) — containing, in this order:
1. Scope (what's under review).
2. The full diff.
3. PR title + body.
4. Jira ticket (description + acceptance criteria), **or** a note that it was unavailable.

Hold onto that path; every reviewer reads it.

## 3. Fan out in parallel

Issue **all four** `Task` calls in a **single message** so they run concurrently. One call per reviewer subagent in `agents/review/`:

- `mental-alignment` · `security` · `code-quality` · `documentation`

Each prompt must pass the **path to the shared context file** and instruct the reviewer to review only the changed code and return its structured findings (or "No concerns identified").

## 4. Aggregate

Run `.claude/skills/review-heavy/references/verdict-algorithm.md` over the combined findings: collect → **drop confidence < 80** → deduplicate → reasonableness filter (`.claude/skills/review-heavy/references/what-not-to-flag.md`) → verdict. Score definitions live in `.claude/skills/review-heavy/references/severity-rubric.md`.

> Run the orchestrating session on **Opus** — aggregation (dedup, confidence gating, verdict) is the judgment-heavy step. The four reviewers stay on Sonnet for cheap parallel fan-out.

## 5. Print the report

Output one consolidated, severity-tiered report to the terminal:

```
## Code Review — <scope>
**Verdict: <Needs Work | Needs Attention | Ready to Merge>**

### Critical
- `file:line` — finding (confidence) → fix

### High
...

### Medium
...

### Low
...
```

Omit empty tiers. If nothing survives the gate, say so and give the verdict. **Do not post. Do not approve. Do not merge.**
