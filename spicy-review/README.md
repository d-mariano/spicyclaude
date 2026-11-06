# spicy-review

Risk-tiered code review for Claude Code. Never approves, never merges, posts to a PR only on request.

```bash
/plugin marketplace add d-mariano/spicyclaude
/plugin install spicy-review --marketplace d-mariano/spicyclaude
```

## Skills

- `/spicy-review:review-heavy [pr|branch|files] [--post] [--request-changes]` sizes the change, fans out to the reviewer agents the risk tier calls for, verifies the survivors, and prints one severity-tiered report.
- `/spicy-review:code-review-light [pr|branch|files]` is the single-pass fast path for small, low-risk diffs.

## Agents

Read-only reviewers, one lens each: `mental-alignment`, `security`, `code-quality`, `documentation`, `tests`, `performance`, `deps`, `observability`, `simplification`, plus `verification`, which re-checks candidate findings before anything is surfaced. Address them as `spicy-review:<name>`.

## Shared contract

Every reviewer scores against [skills/review-heavy/references/severity-rubric.md](skills/review-heavy/references/severity-rubric.md): four severities, a 0 to 100 confidence score, and a hard gate at 80. [what-not-to-flag.md](skills/review-heavy/references/what-not-to-flag.md) is the suppression list. Other plugins that consume findings, such as `spicy-ship`, build on this rubric.
