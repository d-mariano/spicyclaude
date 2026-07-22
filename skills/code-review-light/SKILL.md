---
name: code-review-light
description: Fast single-pass code review of a diff. Use for a quick read-only review of a PR or the current branch — pulls the diff, runs one consolidated pass against the shared severity rubric, and prints a severity-tiered summary. No subagents, never posts. For deep multi-reviewer review use /review-heavy.
argument-hint: "[pr-number | branch | files]"
context: fork
agent: Explore
allowed-tools: Bash(gh *), Bash(git *), Read, Grep, Glob
---

# Light Code Review (single pass)

A quick, **read-only**, single-pass review. No fan-out, no subagents. Pull the diff, review it
once against the shared standard, print a tiered summary. **Never post, approve, or merge.**

Argument (`$ARGUMENTS`): a PR number, a branch name, or a set of files. If empty, review the
current branch against its base.

## Steps

1. **Get the diff.**
   - PR number → `gh pr diff <n>` (and `gh pr view <n> --json title,body` for intent).
   - Branch → `git diff <base>...HEAD` (base is `main`/`master` unless the repo says otherwise).
   - Files → restrict to those paths in the current diff.
   Review **only the changed code**.

2. **One consolidated pass.** In a single read, look for: behavior that doesn't match the PR's
   stated intent, concretely exploitable security flaws, unnecessary complexity / over-engineering,
   and comment/doc rot. Apply the shared standard — do not restate it here:
   - score with [severity-rubric.md](${CLAUDE_SKILL_DIR}/../review-heavy/references/severity-rubric.md)
   - suppress with [what-not-to-flag.md](${CLAUDE_SKILL_DIR}/../review-heavy/references/what-not-to-flag.md)

3. **Filter.** Every finding needs **severity + confidence 0–100 + file:line + concrete fix**.
   Drop anything below confidence 80. Drop anything on the what-not-to-flag list.

4. **Print** a severity-tiered summary (Critical → High → Medium → Low), each line in the
   rubric's rendering format (`- [NN] path:line — **Title.** problem. Fix: …`). End with a
   one-line takeaway. If nothing survives the gate, say **No concerns identified.**

> Scope note: this runs in a forked Explore context, which does not load `CLAUDE.md`. For
> `CLAUDE.md` / guideline-violation checks, full coverage, or posting to a PR, use `/review-heavy`.
> This skill is also the **Low risk tier** fast path in
> [risk-tiering.md](${CLAUDE_SKILL_DIR}/../review-heavy/references/risk-tiering.md).
