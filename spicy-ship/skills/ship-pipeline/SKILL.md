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
- `ship-config.json` in the context folder: the config resolved once at the start of the story.
  Agents get its path; the question mode and the gate parameters come from it, never from a
  second resolution.

## Phases

| # | Agent | Reads | Writes | Gate |
|---|---|---|---|---|
| 1 | `spicy-ship:phase:explorer` | `story.md` | `research-[nnn].md` | none |
| 2 | `spicy-ship:phase:planner` | `story.md`, `research-[nnn].md` | `plan-[nnn].md` | none |
| 3 | review loop: `spicy-ship:phase:plan-reviewer` and `spicy-ship:phase:fixer` in `plan` mode | `plan-[nnn].md`, `story.md` | `plan-review-r{n}.json`, `plan-fixes-r{n}.json` | `review.plan` |
| 4 | `spicy-ship:phase:executor` | `plan-[nnn].md`, `research-[nnn].md` | commits, `progress-[nnn].md` | none |
| 5 | review loop: `spicy-ship:phase:code-reviewer` and `spicy-ship:phase:fixer` in `code` mode | `base_sha..HEAD`, `story.md`, `plan-[nnn].md` | `code-review-r{n}.json`, `code-fixes-r{n}.json` | `review.code` |

Phase 4 runs only after the plan gate is `PASS`, or `EXHAUSTED` with `critical: false`. Anything
else stops the story. Before spawning the executor, record `git rev-parse HEAD` as `base_sha` in
`ship-state.json`; every later phase reviews `base_sha..HEAD` and nothing older, whatever else the
branch carries.

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

3. On `CONTINUE`, spawn the fixer with the findings file, the `fixable` ids, the mode, and in
   `code` mode the progress file, whose recorded test command the fixer must run. Then the next
   round.
4. On anything else, record the outcome in `ship-state.json` and act on it per the review-loop
   outcomes table.

A non-zero exit from the gate is a contract violation by the reviewer or the fixer. Spawn the same
agent once more with the gate's message; do not patch the file yourself. If the second attempt
fails the gate too, set `status: blocked` with the gate's message and stop.

## Handling envelopes

- Every envelope, whatever its status, is appended as one line to `envelopes.jsonl` in the
  context folder, with the phase and round added. The summaries are the only record of what each
  agent reported, including a code-reviewer's `single-pass: Agent tool withheld`.
- `DONE`: record the artifact in `ship-state.json` and move on. The agent has already appended its
  `decisions` to `decisions.md`; the envelope copy is for your reply and the PR summary, never for
  writing to the log a second time.
- `NEEDS_INPUT`: write the envelope's `questions` array to `questions.json` as it is, with the
  agent's phase alongside (`{"phase": "planner", "questions": [...]}`), set `status: needs_input`,
  then apply `question-policy` for the resolved mode. After answers exist in `answers.json`,
  resume the same agent when the harness allows it; otherwise spawn a fresh one with the same
  inputs plus the answers path. All state is on disk, so a fresh agent loses nothing.
- `FAILED`: set `status: blocked` with the summary and stop. Do not retry a `FAILED` phase without
  a change in inputs. A permission denial, a missing tool, or an unreadable path is `FAILED`, not
  `NEEDS_INPUT`: no question to the user changes it, and the fix is in the environment.

## State

`ship-state.json` is the only memory that survives compaction or a new session. Write it after
every phase and every gate:

```json
{
  "story": "story.md",
  "slug": "012-auth-refresh",
  "branch": "ship/012-auth-refresh",
  "base_sha": "3f1c2ab",
  "phase": "code-review",
  "round": 2,
  "status": "running | needs_input | blocked | done",
  "gates": {"plan": "PASS", "code": null},
  "artifacts": {"research": "research-012.md", "plan": "plan-012.md", "progress": "progress-012.md"},
  "blocked_reason": null
}
```

To resume, read it and continue from `phase` and `round`. Never redo a phase whose artifact exists
and whose gate passed. With `status: needs_input`, every question in `questions.json` whose
`<phase>:<id>` key is absent from `answers.json` is still open; ask those before anything else. Inside a review loop the files
decide the next step: no findings file for `round` means spawn the reviewer; findings but no fixes
file means run the gate again, which is idempotent, and act on it; both present means the next
round.

## Rules

- Paths, not content. Never paste an artifact into a prompt.
- Spawn every phase agent with `run_in_background: false`, and whatever the harness does with that
  flag, wait for the agent's envelope before the next step. Agents spawned from the main session
  run in the background in interactive sessions regardless; their completion arrives as a
  notification, and nothing in this pipeline can proceed without the previous phase's artifact.
  Never reply to the user, in part or in full, while a phase agent is still running.
- Every phase agent's definition confines its shell use to git, the plugin scripts, and the
  recorded test command; you do not need to repeat that, only to pass the paths it needs.
- Run every shell command you issue, the gate above all, as one plain command from the
  repository root: no `cd`, no pipe, no `&&`, `;` or `echo`. The same allow rules the agents live
  under apply to you, and a compound command stops matching them and prompts or fails.
- One agent per phase at a time; the two agents of a review loop alternate, they never overlap.
- The executor's test run is the executor's claim. Before the story is called done, run the
  command it recorded in `progress-[nnn].md` once yourself and keep it with its result line.
- Only the main session asks the user. If you are an agent, `NEEDS_INPUT` goes up, not out.
