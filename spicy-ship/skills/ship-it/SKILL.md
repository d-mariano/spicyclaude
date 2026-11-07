---
name: ship-it
description: Implement one well-defined story end to end without supervision: explore, plan, plan review loop, execute, code review loop, pull request. Use when the user says ship it, ship this story, or implement this story unattended.
argument-hint: "<story-file | story text> [--max-review-rounds=N] [--min-severity=Critical|High|Medium|Low] [--questions=auto|raise|batch] [--no-pr] [--resume <context-folder>]"
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(gh *) Bash(python3 *) Bash(ls *) Read Write Edit Glob Grep Agent AskUserQuestion
---

# Ship it

You run in the main session, which makes you the only participant that can ask the user anything.
Everything else is delegated to `spicy-ship:phase:*` agents by following `ship-pipeline` exactly.

## Config

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ship_config.py`

That is the baseline: environment, project file and defaults. Two more sources may apply, and
if either does you run the command once yourself and use its output instead:

- **Plugin options.** As configured: `maxReviewRounds=${user_config.maxReviewRounds}`,
  `minReviewSeverity=${user_config.minReviewSeverity}`, `questionMode=${user_config.questionMode}`.
  An option whose value above still reads `${user_config...}` is unset, or the plugin was loaded
  from a directory rather than installed; skip it. Pass each set one as `--plugin-config KEY=VALUE`.
- **Skill arguments.** Any `--max-review-rounds`, `--min-severity`, `--fix-floor`, `--questions`,
  `--escalate`, `--plan-*` or `--code-*` flag in `$ARGUMENTS` is appended after the plugin options;
  arguments beat every other source.

Never put a `${...}` placeholder into a shell command; the command is refused before it runs.

## Preflight

!`git status --porcelain --untracked-files=no | head -5; git branch --show-current; printenv CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH || echo "depth unset"`

- Tracked changes in the tree stop the run. Say what is uncommitted and stop. The untracked
  `context/` folder is expected and is not a reason to stop.
- An unset depth is fine for `ship-it`: phases run one level down and the code-reviewer's lenses
  two levels down, within the default. Mention it in the final reply so the user knows.

## Procedure

1. **Story.** `$ARGUMENTS` minus the flags is a file path or the story text; a story carries
   context, numbered acceptance criteria, the test command, and what is out of scope, shaped like
   [references/example-story.md](references/example-story.md). With `--resume`,
   read `ship-state.json` in the named folder, check out its `branch`, use the folder's
   `ship-config.json` instead of the config above, and continue from its `phase` per the pipeline's
   resume rules; skip the rest of this step. Otherwise pick the next `nnn` and the slug, and if you
   are on the default branch create and check out `ship/[nnn]-{slug}`; on any other branch stay on
   it. Then create `/context/[nnn]-{slug}/`, write `story.md`, write the resolved config to
   `ship-config.json`, and write `ship-state.json` with `status: running`, `phase: explore`, and
   the branch name.
2. **Pipeline.** Follow `ship-pipeline`. Spawn each phase agent with paths, including the path to
   `ship-config.json`. Keep one line per phase in your context.
3. **Questions.** On `NEEDS_INPUT`, apply `question-policy` for the resolved mode. When you ask,
   render each question through `AskUserQuestion` as the contract specifies, at most four per
   call, options in the given order, no "Other". Write `answers.json`, then resume the agent.
   In `auto` and `batch` mode the policy holds a guarded question until the next checkpoint. A
   single story has no checkpoint that can run before the answer, since every later phase needs
   the stopped agent's artifact, so the hold collapses to asking now.
4. **Done means.** The plan gate and the code gate each ended `PASS`, or `EXHAUSTED` with
   `critical: false`. You ran the test command recorded in `progress-[nnn].md` yourself after the
   code gate and it is green. Any
   `STALLED`, `FAILED`, or critical `EXHAUSTED` ends the run with `status: blocked`; say why and
   stop. Never open a PR for a blocked story.
5. **Pull request.** Unless `--no-pr`: push the branch and open a PR with `gh pr create`. Body
   sections, in order: Summary, the plan's AC trace table, "Decisions made autonomously" copied
   verbatim from `decisions.md`, "Advisory findings" listing, from the final round of each gate,
   every `fixable` finding below the severity floor and any `EXHAUSTED` blocking findings with
   their ids, and the test command with its result line. Never merge.
6. **Reply.** At most fifteen lines: status, PR link or blocked reason, rounds used per gate with
   their outcomes, open decisions count, and the test result line.

## Never

- Do phase work yourself, however small. If an agent fails, the fix is a better input, not your
  own edit.
- Guess a gate outcome. The script decides.
- Ask more than the policy allows, or ask in `auto` mode for anything but a guarded question.
