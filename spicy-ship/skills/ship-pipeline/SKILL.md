---
name: ship-pipeline
description: The per-story procedure a ship orchestrator follows: explore, plan, plan review loop, execute, code review loop, with a state file and the phase agents to spawn at each step. Load when orchestrating one story end to end.
user-invocable: false
---

# Ship pipeline

One story, five phases, two review loops. You orchestrate; you never do phase work yourself.
Every phase is a `spicy-ship:phase:*` agent that gets paths, writes an artifact, and ends with the
return envelope from `question-policy`. Your own context holds one line per phase and the
envelopes, nothing else.

## Inputs

- The story: text plus acceptance criteria, already written to `story.md` in the context folder.
- The context folder `/context/[nnn]-{slug}/`. [references/artifacts.md](references/artifacts.md)
  lists every file that lives there.
- The resolved config JSON from `ship_config.py`.
- The question mode, from that config.

## Phases

| # | Agent | Reads | Writes | Gate |
|---|---|---|---|---|
| 1 | `spicy-ship:phase:explorer` | `story.md` | `research-[nnn].md` | none |
| 2 | `spicy-ship:phase:planner` | `story.md`, `research-[nnn].md` | `plan-[nnn].md` | none |
| 3 | review loop: `spicy-ship:phase:plan-reviewer` and `spicy-ship:phase:fixer` in `plan` mode | `plan-[nnn].md`, `story.md` | `plan-review-r{n}.json`, `plan-fixes-r{n}.json` | `review.plan` |
| 4 | `spicy-ship:phase:executor` | `plan-[nnn].md`, `research-[nnn].md` | commits, `progress-[nnn].md` | none |
| 5 | review loop: `spicy-ship:phase:code-reviewer` and `spicy-ship:phase:fixer` in `code` mode | git range, `story.md`, `plan-[nnn].md` | `code-review-r{n}.json`, `code-fixes-r{n}.json` | `review.code` |

Phase 4 runs only after the plan gate is `PASS`, or `EXHAUSTED` with `critical: false`. Anything
else stops the story.

## Running a review loop

Follow `review-loop` exactly. Per round `n`:

1. Spawn the reviewer with the target, the story, the round number, and for `n > 1` the previous
   findings file and the previous fixes file.
2. Run the gate. Never guess its outcome.

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/review_gate.py <phase>-review-r{n}.json \
     [--prior <phase>-review-r{n-1}.json --fixes <phase>-fixes-r{n-1}.json] \
     --max-rounds <cfg.review.<phase>.max_rounds> \
     --min-severity <cfg.review.<phase>.min_severity> \
     --fix-floor <cfg.review.<phase>.fix_floor>
   ```

3. On `CONTINUE`, spawn the fixer with the findings file, the `fixable` ids, and the mode. Then
   the next round.
4. On anything else, record the outcome in `ship-state.json` and act on it per the review-loop
   outcomes table.

A non-zero exit from the gate is a contract violation by the reviewer or the fixer. Spawn the same
agent again with the gate's message; do not patch the file yourself.

## Handling envelopes

- `DONE`: record the artifact in `ship-state.json`, append `decisions` to `decisions.md`, move on.
- `NEEDS_INPUT`: apply `question-policy` for the resolved mode. After answers exist in
  `answers.json`, resume the same agent when the harness allows it; otherwise spawn a fresh one
  with the same inputs plus the answers path. All state is on disk, so a fresh agent loses nothing.
- `FAILED`: set `status: blocked` with the summary and stop. Do not retry a `FAILED` phase without
  a change in inputs.

## State

`ship-state.json` is the only memory that survives compaction or a new session. Write it after
every phase and every gate:

```json
{
  "story": "story.md",
  "slug": "012-auth-refresh",
  "branch": "ship/012-auth-refresh",
  "phase": "code-review",
  "round": 2,
  "status": "running | needs_input | blocked | done",
  "gates": {"plan": "PASS", "code": null},
  "artifacts": {"research": "research-012.md", "plan": "plan-012.md", "progress": "progress-012.md"},
  "blocked_reason": null
}
```

To resume, read it and continue from `phase` and `round`. Never redo a phase whose artifact exists
and whose gate passed.

## Rules

- Paths, not content. Never paste an artifact into a prompt.
- One agent per phase at a time; the two agents of a review loop alternate, they never overlap.
- The executor's test run is the executor's claim. Before the story is called done, run the suite
  once yourself and keep the command and its result line.
- Only the main session asks the user. If you are an agent, `NEEDS_INPUT` goes up, not out.
