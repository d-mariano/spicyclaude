# Story: ship_config emits the gate flags for a reviewer

## Context

`ship-pipeline` tells the orchestrator to call `review_gate.py` with `--max-rounds`, `--min-severity` and `--fix-floor` taken from the `plan` or `code` section of the config JSON that `ship_config.py` prints. Today the orchestrator reads the JSON and hand-maps three values into three flags on every round. A `--gate-flags=<reviewer>` option on `ship_config.py` removes that step: it prints the three flags for one reviewer on one line, ready to paste after the findings file.

Code lives in `spicy-ship/scripts/`. Tests live in `spicy-ship/scripts/tests/` and run from the repository root with `python3 -m unittest discover -s spicy-ship/scripts/tests -t spicy-ship/scripts`; a story's test command is always a single plain command runnable from the root. Standard library only; no new dependencies.

## Acceptance criteria

- AC-1: `python3 ship_config.py --gate-flags=plan` prints exactly one line, `--max-rounds 3 --min-severity High --fix-floor Medium` with the values of the resolved `review.plan` section, and prints nothing else. `--gate-flags=code` does the same for `review.code`.
- AC-2: Every other configuration source still applies. `python3 ship_config.py --plan-rounds=2 --gate-flags=plan` prints `--max-rounds 2 --min-severity High --fix-floor Medium`, and `SPICY_CODE_MIN_SEVERITY=Critical python3 ship_config.py --gate-flags=code` prints `--min-severity Critical` in its line.
- AC-3: `--gate-flags=<anything else>` and `--gate-flags=` fail loud: a message to stderr that names the allowed reviewers (`plan`, `code`), exit code 1, nothing on stdout.
- AC-4: Without `--gate-flags`, the output is the full JSON exactly as before.
- AC-5: Unit tests in `spicy-ship/scripts/tests/test_ship_config.py` cover AC-1 to AC-4, written RED first. The full suite stays green.

## Out of scope

- Changing `review_gate.py`.
- Changing any SKILL.md to use the new flag; that is a follow-up once the flag exists.
