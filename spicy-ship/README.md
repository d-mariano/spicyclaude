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

## Scripts

Standard library only, so they run wherever Claude Code runs.

- `scripts/ship_config.py` resolves configuration and prints JSON.
- `scripts/review_gate.py` validates a round's findings and prints the loop decision. After round 1 it needs `--prior` (the previous round's findings) and `--fixes` (the fixer's resolutions for that round).

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
