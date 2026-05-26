# Evaluations

Three scenarios that test the failure modes this skill is built to prevent. Run these whenever you change the skill — they're the source of truth for whether it still works.

## Format

Each `*.json` file follows the format from the [skills best-practices docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#evaluation-and-iteration):

```json
{
  "skills": ["breaking-down-design-docs"],
  "query": "<user's first message>",
  "files": ["fixtures/<name>.md"],
  "expected_behavior": ["...", "..."]
}
```

There is no built-in runner. Two ways to use these:

1. **Manual.** Open a fresh Claude session with the skill loaded, paste the `query` and the contents of the `files`, and check whether the response matches `expected_behavior`. Note any item it misses.
2. **Automated.** Wire them into your own runner — the JSON is structured for that.

## What each scenario tests

| File | Tests | Primary failure mode it catches |
|---|---|---|
| `01-happy-path.json` | Phase 1 → 2 → 3 workflow with a clean, well-written design doc | Skipping the hard gate between Phase 2 and Phase 3 |
| `02-problem-statement.json` | Early-exit when the "design" is actually goals without a solution | Producing a fake breakdown of goals as if they were stories |
| `03-ambiguous-doc.json` | Pushback when the doc contradicts itself or references phantom systems | Papering over ambiguity to produce a clean-looking output |

## Adding more

If you observe a new failure mode in real use, add a fixture and eval here before fixing the skill. The eval is the regression test.
