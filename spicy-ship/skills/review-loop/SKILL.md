---
name: review-loop
description: The reviewer-fixer loop that ship pipelines run after planning and after implementation. Defines the findings contract, how many rounds run, which severities force another round, and what each outcome means. Load when orchestrating or acting inside a review loop.
user-invocable: false
---

# Review loop

One reviewer and one fixer alternate until nothing at or above the severity floor remains, the
round budget runs out, or the two stop making progress. The loop decision is never made by a
model: `review_gate.py` computes it from the findings file.

## Configuration

Resolve once per run with `${CLAUDE_PLUGIN_ROOT}/scripts/ship_config.py`, adding
`--plugin-config KEY=VALUE` for each plugin option that is set and the skill's own flags last, and
pass the `plan` or `code` section to the gate. The orchestrator skill owns that call; this skill
only consumes its output.

| Key | Default | Meaning |
|---|---|---|
| `max_rounds` | 3 | Reviewer rounds before `EXHAUSTED` |
| `min_severity` | `High` | Lowest severity that forces another round |
| `fix_floor` | `Medium` | Lowest severity the fixer is handed; never causes a re-review on its own |

## Severity and confidence

Use the shared rubric from `spicy-review`: `Critical`, `High`, `Medium`, `Low`, plus a confidence
score from 0 to 100. The gate drops anything under 80 before deciding. Reviewers apply the
rubric's `what-not-to-flag` list and are told plainly that a round with no findings is a valid,
expected result. A reviewer asked to find problems will find something; the floor is the
structural fix for that.

## Findings contract

Each round the reviewer writes `<phase>-review-r<round>.json` in the story's context folder.
[references/findings.schema.json](references/findings.schema.json) is the normative schema.

```json
{
  "reviewer": "code-reviewer",
  "target": "plan-012.md or a git range",
  "round": 2,
  "prior_findings": [{"id": "F1", "status": "resolved"}, {"id": "F2", "status": "unresolved"}],
  "findings": [
    {
      "id": "F2",
      "title": "Refresh token stored in plaintext",
      "severity": "High",
      "confidence": 90,
      "location": "src/auth/refresh.py:88",
      "category": "security",
      "problem": "The token is written to the sessions table unhashed, so a DB read leaks live credentials.",
      "fix": "Hash with bcrypt before insert; compare with bcrypt.checkpw on refresh."
    }
  ]
}
```

Rules the gate enforces:

- An empty `findings` list is the only way to say the round is clean; there is no separate verdict
  field, the gate derives the outcome.
- Every round after the first is gated with `--prior` pointing at the previous round's findings
  and `--fixes` pointing at the fixer's `<phase>-fixes-r<round-1>.json`.
  Every finding in the prior file gets a `status`, and no id outside it may appear. A prior finding
  that is `unresolved` or `regressed` is re-listed in `findings` under the same `id`, with a fresh
  location and confidence; one marked `resolved` may not be.
- The fixes file has exactly one entry for every prior finding at or above the fix floor that
  passed the confidence gate, each `fixed` or `rejected` with a note. A finding the fixer never
  mentions fails the round, so a skip cannot hide as progress.
- Ids look like `F12` and are unique within a round; no key outside the schema appears anywhere in
  the file. Keeping an id stable across rounds for the same issue is the reviewer's duty, which the
  gate cannot check.
- `category` is one of the schema's enumerated values and `location` is `path`, `path:line` or
  `path:start-end`, so fingerprints compare like with like.
- Identity across rounds is the fingerprint of category, file path, and normalized title, so a
  finding that moves a few lines after a fix still counts as the same finding.

## Algorithm

```
for round in 1..max_rounds:
    reviewer writes <phase>-review-r<round>.json (round 1 has no prior)
    decision = review_gate.py <current> [--prior <previous> --fixes <previous fixes>] --max-rounds N --min-severity S --fix-floor F
    PASS      -> stop; the gate is green; decision.fixable, if any, goes to the PR body unfixed
    EXHAUSTED -> stop; apply the question policy to the blocking findings
    STALLED   -> stop; reviewer and fixer disagree, escalate
    CONTINUE  -> fixer applies decision.fixable by id, records fixed or rejected-with-reason
```

`STALLED` fires when every blocking finding this round repeats one from the previous round, by id
or by fingerprint, and the fixer recorded `rejected` for each of them. That is a disagreement, and
another round would only restate it, however many other findings the fixer did resolve. A repeat after a fix the fixer recorded as `fixed` is
progress the reviewer judged insufficient; the loop continues while the budget lasts.

## Outcomes

| Outcome | In `auto` mode | In `raise` or `batch` mode |
|---|---|---|
| `PASS` | proceed; list `fixable` findings in the PR body under "Advisory findings" | same |
| `EXHAUSTED`, no `Critical` | proceed, list blocking findings in the PR body under "Unresolved findings" | ask the user |
| `EXHAUSTED`, `critical: true` | mark the story blocked; never open the PR | ask the user |
| `STALLED` | mark the story blocked | ask the user |

## Roles

The phase agents in this plugin implement the first two roles: `spicy-ship:phase:plan-reviewer` and
`spicy-ship:phase:code-reviewer` review, `spicy-ship:phase:fixer` fixes. Whatever drives the loop,
a skill in the main session or an agent one level up, is the orchestrator and runs the gate.

**Reviewer.** Read-only. Reviews only the target it is given against the story's acceptance
criteria and the codebase. On a re-review it first verifies every prior finding, reading the
fixer's `<phase>-fixes-r<round>.json` to judge rejections on their merits, then looks for
regressions the fixes introduced. Writes the findings file; returns a two-line summary.

**Fixer.** Applies only the findings it is handed, by id. For each it records `fixed` or
`rejected` with a one-sentence reason in `<phase>-fixes-r<round>.json`, so the next review can
judge the rejection. It never widens scope and never touches findings below the fix floor unless
they share a file and a root cause with one it is already fixing.

**Orchestrator.** Passes paths, not content. Keeps one line per round in its own context. Runs
the gate script; never guesses the outcome.
