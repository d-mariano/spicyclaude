# spicy-ship

Building blocks for shipping a story unattended: the contracts that review loops and open questions follow, and the scripts that make the loop decision deterministic.

```bash
/plugin marketplace add d-mariano/spicyclaude
/plugin install spicy-ship --marketplace d-mariano/spicyclaude
```

Depends on `spicy-review` for the severity rubric and the reviewer agents.

## Skills

Both are model-invoked only; they are reference material for orchestrators and agents, not commands.

- [review-loop](skills/review-loop/SKILL.md): the reviewer and fixer loop, its findings contract, and the four outcomes.
- [question-policy](skills/question-policy/SKILL.md): how agents that cannot ask the user still surface decisions, and when the main session asks.

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

## Scripts

Standard library only, so they run wherever Claude Code runs.

- `scripts/ship_config.py` resolves configuration and prints JSON.
- `scripts/review_gate.py` validates a round's findings and prints the loop decision.

Run the tests with:

```bash
python3 -m unittest discover -s spicy-ship/scripts/tests -t spicy-ship/scripts
```

## Configuration

Highest precedence first.

| Source | Example |
|---|---|
| Skill arguments | `--max-review-rounds=5 --min-severity=Medium --plan-rounds=2 --questions=batch` |
| Environment | `SPICY_MAX_REVIEW_ROUNDS`, `SPICY_REVIEW_MIN_SEVERITY`, `SPICY_QUESTION_MODE`, `SPICY_PLAN_MAX_ROUNDS`, `SPICY_CODE_MIN_SEVERITY` |
| Project file | `.claude/spicyclaude.json`, see below |
| Plugin options | `/plugin configure spicy-ship@spicyclaude` |
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

Invalid values stop the run with the offending key named. A fix floor stricter than the minimum severity is invalid.
