# spicy-ship

Ship stories unattended. `/spicy-ship:ship-it` takes one story: it explores, plans, reviews the plan, implements, reviews the code, and opens a pull request, delegating each phase to an agent and asking you only what the question policy lets through. `/spicy-ship:ship-fleet` takes a manifest of stories and ships them as stacked pull requests, each story in its own worktree and independent stories in parallel.

```bash
/plugin marketplace add d-mariano/spicyclaude
/plugin install spicy-ship --marketplace d-mariano/spicyclaude
```

Depends on `spicy-skills` for the craft skills the planner, executor and fixer load, and on `spicy-review` for the severity rubric and the reviewer agents.

## Usage

```
/spicy-ship:ship-it path/to/story.md
/spicy-ship:ship-it "Add refresh-token rotation; AC-1 ..., AC-2 ..." --questions=raise
/spicy-ship:ship-it --resume /context/012-auth-refresh
/spicy-ship:ship-fleet path/to/fleet.json --max-parallel=3
```

`ship-it` runs in the main session, delegates every phase to an agent, asks you only what the question policy lets through, and ends with a pull request or a named reason it stopped. Artifacts live in `/context/[nnn]-{slug}/`; `ship-state.json` there is the resume point.

`ship-fleet` reads a [fleet manifest](skills/ship-fleet/references/fleet-manifest.md) and keeps its progress in it, so running the same command again resumes the fleet. A story starts once the stories it depends on are done and stacks on its dependency's branch; a blocked story holds back only the stories behind it. Pull requests merge in manifest order, and two stories stacked on the same base can conflict when the second one merges.

## Skills

- [ship-it](skills/ship-it/SKILL.md): the user-invoked orchestrator for one story.
- [ship-fleet](skills/ship-fleet/SKILL.md): the user-invoked orchestrator for a manifest of stories.
- [ship-pipeline](skills/ship-pipeline/SKILL.md): the per-story procedure ship-it and each story-runner follow, with the [artifact layout](skills/ship-pipeline/references/artifacts.md). Model-invoked only.
- [review-loop](skills/review-loop/SKILL.md): the reviewer and fixer loop, its findings contract, and the four outcomes. Model-invoked only.
- [question-policy](skills/question-policy/SKILL.md): how agents that cannot ask the user still surface decisions, and when the main session asks. Model-invoked only.

## Agents

Phase agents under `agents/phase/`, addressed as `spicy-ship:phase:<name>`. Each takes paths, not content, cannot ask the user, and ends with the return envelope the question policy defines.

| Agent | Writes | Model |
|---|---|---|
| `explorer` | `research-[nnn].md` | sonnet |
| `planner` | `plan-[nnn].md` | opus |
| `plan-reviewer` | `plan-review-r{n}.json` | opus |
| `executor` | code, commits, `progress-[nnn].md` | sonnet |
| `code-reviewer` | `code-review-r{n}.json`, fanning out to the `spicy-review` lenses | opus |
| `fixer` | plan or code fixes, `<mode>-fixes-r{n}.json` | sonnet |

`story-runner`, addressed as `spicy-ship:story-runner`, runs one story of a fleet in its own worktree by following `ship-pipeline`, and hands questions back to `ship-fleet`. Model opus.

## Scripts

Standard library only, so they run wherever Claude Code runs.

- `scripts/ship_config.py` resolves configuration and prints JSON. With `--gate-flags=plan|code` it prints that reviewer's `review_gate.py` flags on one line instead, and with `--from=<ship-config.json>` it renders them from a story's frozen config rather than resolving again.
- `scripts/review_gate.py` validates a round's findings and prints the loop decision. After round 1 it needs `--prior` (the previous round's findings) and `--fixes` (the fixer's resolutions for that round).
- `scripts/fleet_plan.py` validates a fleet manifest, a list of stories with their dependencies, and prints which stories start now and the branch each stacks on. Stories that do not depend on each other start together, up to `--max-parallel`.

Run the tests with:

```bash
python3 -m unittest discover -s spicy-ship/scripts/tests -t spicy-ship/scripts
```

## Unattended runs

Phase agents follow the [conduct rules](skills/ship-pipeline/references/agent-conduct.md) for the shell and the file tools. They also load the craft skills by name, and the explorer and planner fetch from the web. Pre-approve that surface and nothing stalls on a prompt:

```json
{"permissions": {"allow": ["Bash(git *)", "Bash(python3 *)", "Edit", "Write", "Skill", "WebSearch", "WebFetch"]}}
```

Add the project's own test runner if it is not `python3`; the conduct file lists what stops matching these rules. `ship-it` itself pre-approves `Bash(gh pr create *)` for the pull request step through its own frontmatter.

Know what you are approving: `Bash(python3 *)` admits `python3 -c` and `Bash(git *)` admits `git -c core.fsmonitor=<cmd>`, so together they are an unrestricted shell for any agent that holds them. The agents treat everything they read as data rather than instructions, and the explorer and planner fetch from the web, so that guard is doing real work. Run unattended only on repositories and stories you trust.

The code-reviewer fans out to the review lenses one subagent level below itself, which is two levels below the main session under `ship-it` and three under `ship-fleet`, where a story-runner sits in between. In an interactive session the documented default depth of three levels covers both. In a headless run (`claude -p`) on the build this was tested with (2.1.319), a subagent had no Agent tool until the depth was set explicitly, so headless runs also need this in the project's settings; it is harmless elsewhere:

```json
{"env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"}}
```

Without it the code-reviewer falls back to a single consolidated pass, says `single-pass: Agent tool withheld` in its envelope, and `ship-it` repeats that in its final reply.

## Configuration

Highest precedence first.

| Source | Example |
|---|---|
| Skill arguments | `--max-review-rounds=5 --min-severity=Medium --plan-rounds=2 --questions=raise` |
| Environment | `SPICY_MAX_REVIEW_ROUNDS`, `SPICY_REVIEW_MIN_SEVERITY`, `SPICY_QUESTION_MODE`, `SPICY_PLAN_MAX_ROUNDS`, `SPICY_CODE_MIN_SEVERITY` |
| Project file | `.claude/spicyclaude.json`, see below |
| Plugin options | `/plugin configure spicy-ship@spicyclaude`; an option reaches the skill only when it is set and the plugin is installed from a marketplace, never from a `--plugin-dir` load |
| Defaults | 3 rounds, `High`, fix floor `Medium`, mode `auto`, escalate `irreversible` |

```json
{
  "review": {
    "default": {"max_rounds": 3, "min_severity": "High", "fix_floor": "Medium"},
    "plan": {"max_rounds": 2}
  },
  "questions": {"mode": "auto", "escalate": ["irreversible"]}
}
```

Invalid values stop the run with the offending key named. A fix floor stricter than the minimum severity is invalid. An empty value in any source means unset. Precedence is by source first: a `--max-review-rounds` argument beats a project file's `review.plan.max_rounds`, while inside one source a reviewer-specific key beats that source's default.
