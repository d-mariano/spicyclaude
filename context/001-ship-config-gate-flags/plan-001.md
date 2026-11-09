# Plan 001: ship_config emits the gate flags for a reviewer

## Overview

`ship_config.main` gains a `--gate-flags=<reviewer>` option. `main` takes it out of argv before
`resolve()` runs, checks that the reviewer is `plan` or `code`, resolves the config as it does
today, and prints one line with the `review_gate.py` flags for that reviewer instead of the JSON.
`resolve()` and every config source stay untouched. The changes go in one source file, its test
file, and one README line.

## Key decisions

| # | Decision | Choice | Rationale |
|---|---|---|---|
| D1 | Where `--gate-flags` is handled | In `main`: removed from argv before `resolve()` | `resolve` stays pure; otherwise `_from_flags` rejects the flag as unknown (explorer, carried forward) |
| D2 | Bare `--gate-flags` with no `=` | Read as an empty value, so it fails with the reviewer list | AC-3 wants the allowed reviewers named (explorer, carried forward) |
| D3 | `--gate-flags` given more than once | The last one wins | Matches how repeated flags overwrite each other everywhere else in the file (explorer, carried forward) |
| D4 | When the reviewer name is checked | **When it is pulled from argv, before `resolve()`** (research suggested checking after resolve) | A wrong argument is reported whatever state the environment is in. Without this, `--gate-flags=docs` run outside a git repo would print the project-root error, not the reviewer list. Checking at parse time is also how `_from_flags` already handles every flag. Stdout stays empty either way, because the only `print` comes after both steps |
| D5 | Mention the flag in `spicy-ship/README.md` | Yes, one clause on the existing `ship_config.py` line in the Scripts section | The README is the map of the scripts. SKILL.md files stay untouched, as the story requires |
| D6 | Make the formatter a public `gate_flags()` (research's suggestion)? | No: two private helpers, `_pop_gate_flags` and `_gate_flags_line` | Nothing outside `main` calls them. Tests drive the CLI through `main`, which is where the behavior can be seen. A public function would add API surface no one uses |

There are no deliberate divergences from the acceptance criteria.

## Pre-flight findings

### Call-site survey

- `ship_config.main` has one caller, the `__main__` guard. No code calls `resolve()` except the
  tests and `main`. The SKILL.md files run the script as a CLI: with no arguments at
  `skills/ship-it/SKILL.md:16`, and at `skills/review-loop/SKILL.md:15`, whose text says it adds
  config flags. None
  passes `--gate-flags`, so every existing call takes the JSON branch, which stays byte-identical.
- The axes being changed are argv parsing and output format. Today every argv token goes to
  `_split_argv`, and `--plugin-config` takes the next token as its value. That is the one pattern
  that differs: the new extraction runs over raw argv *before* `_split_argv`. So
  `--plugin-config --gate-flags=plan` now treats the gate flag as a gate flag, where today it is an
  "unknown plugin option" error. In both cases `--plugin-config` then fails or takes the next real
  pair. It still fails loud and was never a supported form, so it is left alone.
- Consumer flag names come from `review_gate.py:213-215` (argparse): `--max-rounds` (int),
  `--min-severity` and `--fix-floor` (choices `SEVERITIES`). Turning each `REVIEW_KEYS` entry into
  a flag (`_` becomes `-`, prefixed with `--`) gives exactly these names, in the order AC-1 shows.

### Existing-test impact

None of the 70 existing tests calls `main`. All of them go through `resolve()`, `project_file()`
or `review_gate.decide`. None breaks.

### Sibling-test enumeration (`spicy-ship/scripts/tests/test_ship_config.py`, the only test file modified)

- CHANGED: none.
- UNCHANGED-but-named: `ValidationTest.test_unknown_arg_fails_loud`. It asserts that
  `--max-rounds=3` is an unknown argument to `resolve`. It stays correct: `--max-rounds` is a
  `review_gate` flag that appears in the *output*, not a `ship_config` input.
  `ProjectRootTest.*` is also named here: the new tests set `CLAUDE_PROJECT_DIR`, so the git
  fallback those tests cover is never reached through `main`.
- UNCHANGED-irrelevant: `DefaultsTest`, `PrecedenceTest`, `PerReviewerTest`, `QuestionsTest`,
  `EmptyValueTest`, `StrictTypesTest`, `ProjectFileErrorsTest`, and the other `ValidationTest`
  methods.

### Stale-reference search

Nothing is renamed or removed. A grep for `gate-flags` and `gate_flags` outside `context/` finds
only `spicy-ship/skills/ship-it/references/example-story.md`. That file is a reference copy of this
story and stays unchanged. The README line `scripts/ship_config.py resolves configuration and
prints JSON` becomes incomplete and is updated (D5). The module docstring line 2 says "print it as
JSON" and is updated.

### Sibling-story coupling

No other story in this run depends on this one, or is a dependency of it. The follow-up (switching
`ship-pipeline/SKILL.md:46-52` and `review-loop/SKILL.md:83` to the new flag) shares one surface
with it: the stdout line format and the `--gate-flags=<plan|code>` spelling. Until that follow-up
lands, users see no change. Orchestrators keep hand-mapping the JSON values, and the new flag is
available but unused.

### Research gap found

Research expected the AC-3 tests to go RED as long as they "assert that stderr names `plan` and
`code`". That is wrong. Today's error for `--gate-flags=docs` is
`unknown argument '--gate-flags'; known: --code-min-severity, --code-rounds, ... --plan-rounds`,
which already contains both substrings, so such tests would pass before any code is written.
Working assumption: the AC-3 tests assert the specific phrase `--gate-flags must be one of plan, code`,
which does not exist today.

## AC trace

| AC | Satisfied by | Test |
|---|---|---|
| AC-1 plan | `main` gate branch, `_gate_flags_line` | `test_plan_prints_one_line_of_gate_flags` |
| AC-1 code, right section | same | `test_code_reads_the_code_section` |
| AC-1 and AC-4 via the real CLI (argv defaults to `sys.argv[1:]`) | `main` argv default | `test_cli_entry_point_defaults_to_sys_argv` |
| AC-2 CLI flag | `resolve` unchanged, fed the leftover argv | `test_cli_flag_applies` |
| AC-2 env | same | `test_env_applies` |
| AC-2 project file and plugin config (every other source) | same | `test_project_file_applies`, `test_plugin_config_applies` |
| AC-3 bad reviewer, empty value, bare flag | `_pop_gate_flags` validation | `test_unknown_reviewer_fails_loud` (subTests) |
| AC-3 nothing on stdout when the config is invalid | a single `print` after `resolve` | `test_invalid_config_with_gate_flags_fails_loud` |
| AC-4 | JSON branch unchanged | `test_without_gate_flags_prints_full_json` |
| AC-5 | All of the above in a new `GateFlagsTest` class in `test_ship_config.py`, RED first. The full suite goes from 70 to 80 | full-suite run |

## Files to change

- MODIFIED `spicy-ship/scripts/ship_config.py`
  - Module docstring: add one sentence. `--gate-flags=plan|code` prints that reviewer's
    `review_gate.py` flags on one line instead of the JSON.
  - Add a constant `GATE_FLAGS = "--gate-flags"` next to the other module constants.
  - Add `_pop_gate_flags` and `_gate_flags_line` (signatures below), placed just above `main`.
  - `main`: inside the existing `try`, first set `argv = sys.argv[1:] if argv is None else argv`
    (the default moves out of the `resolve` call, so a real CLI run still works), call
    `_pop_gate_flags(argv)`, then `resolve(rest, os.environ)`, then exactly one `print`. With no reviewer it prints `json.dumps(config, indent=2)`; otherwise it
    prints `_gate_flags_line(config["review"][reviewer])`. Update the docblock to mention the gate
    line.
- MODIFIED `spicy-ship/scripts/tests/test_ship_config.py`. Add `import contextlib`, `import io`,
  `import os`, `import subprocess`, `import sys`, `from unittest.mock import patch` (skip any already imported), a module-level `run_main` helper, and a
  `GateFlagsTest` class.
- MODIFIED `spicy-ship/README.md:54`. Change it to: "`scripts/ship_config.py` resolves configuration
  and prints JSON, or with `--gate-flags=plan|code` the `review_gate.py` flags for that reviewer."
- NOT modified, considered:
  - `review_gate.py` (out of scope).
  - `skills/ship-pipeline/SKILL.md` and `skills/review-loop/SKILL.md` (out of scope, follow-up).
  - `skills/ship-it/references/example-story.md` (the reference input, must match the story).
  - `severities.py` (no change needed).

## New functions

```python
def _pop_gate_flags(argv: list[str]) -> tuple[str | None, list[str]]:
    """Split --gate-flags out of argv and return (reviewer or None, remaining argv).

    The last occurrence wins; a bare flag counts as an empty value. Raises ConfigError naming
    the allowed reviewers when the flag is present with anything other than plan or code.
    """

def _gate_flags_line(section: dict[str, int | str]) -> str:
    """Render one resolved review section as review_gate.py flags, in REVIEW_KEYS order."""
```

Intended bodies, for reference. The executor may reshape them, but the behavior must match:

- `_pop_gate_flags` goes through argv. A token equal to `GATE_FLAGS` or starting with
  `GATE_FLAGS + "="` sets `reviewer = raw.partition("=")[2]`. Every other token is appended to
  `rest`. After the loop, if `reviewer is not None and reviewer not in REVIEWERS`, raise
  `ConfigError(f"{GATE_FLAGS} must be one of {', '.join(REVIEWERS)}, got {reviewer!r}")`.
- `_gate_flags_line` returns `" ".join(f"--{key.replace('_', '-')} {section[key]}" for key in REVIEW_KEYS)`.

`main` keeps its `argv=None` signature and its `sys.argv[1:]` default, applied before `_pop_gate_flags`.

## Test impact

Test helper, module level in `test_ship_config.py`:

```python
def run_main(argv: list[str], env: dict[str, str] | None = None, project: dict | None = None) -> tuple[int, str, str]:
    """Run ship_config.main in a hermetic environment and return (exit code, stdout, stderr)."""
```

The helper creates a `TemporaryDirectory`. If `project` is given, it writes
`<tmp>/.claude/spicyclaude.json` from it. It then runs `main(argv)` under
`patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": tmp, **(env or {})}, clear=True)`, with
`contextlib.redirect_stdout` and `redirect_stderr` pointed at `io.StringIO`.

ADD (`GateFlagsTest`). The constant `DEFAULT_LINE = "--max-rounds 3 --min-severity High --fix-floor Medium"`
sits at class level, so the literal from the story appears once.

| Test | What it asserts | Observable change that would fail it |
|---|---|---|
| `test_plan_prints_one_line_of_gate_flags` | `run_main(["--gate-flags=plan"])` returns `(0, DEFAULT_LINE + "\n", "")` | Any extra output, a different flag order or spelling, JSON instead of the line. RED today: exit 1, "unknown argument" |
| `test_code_reads_the_code_section` | `["--code-rounds=5", "--gate-flags=code"]` prints `--max-rounds 5 ...`. Paired with `["--code-rounds=5", "--gate-flags=plan"]`, which prints `DEFAULT_LINE` | An implementation that always reads `plan`, or reads the wrong section. With defaults alone, plan and code print the same line, so this test is the only one that tells them apart |
| `test_cli_flag_applies` | `["--plan-rounds=2", "--gate-flags=plan"]` prints `--max-rounds 2 --min-severity High --fix-floor Medium\n` | The gate path skips CLI flags, for example by passing the original argv or dropping the leftover argv |
| `test_env_applies` | env `SPICY_CODE_MIN_SEVERITY=Critical`, `["--gate-flags=code"]` prints exactly `--max-rounds 3 --min-severity Critical --fix-floor Medium\n` | The gate path ignores `os.environ` |
| `test_project_file_applies` | project `{"review": {"plan": {"max_rounds": 1}}}` with `--gate-flags=plan` prints `--max-rounds 1 ...` | The gate path skips the project file |
| `test_plugin_config_applies` | `["--plugin-config", "maxReviewRounds=4", "--gate-flags=plan"]` prints `--max-rounds 4 ...` | Extraction breaks how `--plugin-config` pairs with its next token |
| `test_unknown_reviewer_fails_loud` | subTest over `--gate-flags=docs`, `--gate-flags=Plan`, `--gate-flags=`, `--gate-flags`: exit 1, stdout `""`, stderr contains `--gate-flags must be one of plan, code` | A missing or case-insensitive check, a message that doesn't name the reviewers, anything on stdout. RED today because the specific phrase is absent (see Research gap) |
| `test_invalid_config_with_gate_flags_fails_loud` | `["--gate-flags=plan", "--min-severity=Nit"]`: exit 1, stdout `""`, stderr contains `severity must be one of` | Printing before `resolve` fails, or the gate flag hiding the real config error. The gate flag comes first on purpose: `_from_flags` walks flags in order, so today it fails on `--gate-flags` with "unknown argument '--gate-flags'" and the test is RED. With the flag last it would hit the severity error first and pass before any code is written |
| `test_cli_entry_point_defaults_to_sys_argv` | `subprocess.run([sys.executable, ship_config.__file__, "--gate-flags=plan"], env={"CLAUDE_PROJECT_DIR": tmp}, capture_output=True, text=True)` with `tmp` a fresh `TemporaryDirectory`: returncode 0, stdout `DEFAULT_LINE + "\n"` | `main` dropping its `sys.argv[1:]` default, so a real CLI run raises `TypeError` on `None`. Every other test passes an explicit list and cannot see this. RED today: exit 1, "unknown argument" |
| `test_without_gate_flags_prints_full_json` | `run_main([])` returns code 0, and stdout equals `json.dumps(EXPECTED_DEFAULTS, indent=2) + "\n"`, where `EXPECTED_DEFAULTS` is a literal dict of the resolved defaults (not computed with `resolve`) | Any change to the JSON branch: indent, key set, extra output |

`test_without_gate_flags_prints_full_json` is a regression guard for AC-4 and passes at RED time
by design: AC-4 says "exactly as before". Comparing against a literal dict keeps it from being a
tautology of `resolve` compared with itself.

MODIFY: none. DELETE: none.

Not tested on purpose: "last wins" for repeated `--gate-flags` (D3). No AC needs it, and it falls
out of the loop naturally. Noted under risks.

## CLAUDE.md reinforcement

- Fail fast and loud. A bad reviewer raises `ConfigError`, which `main` already turns into stderr
  plus exit 1. No fallback to JSON, and no default reviewer.
- Delete more than you add, KISS. Use no argparse rewrite and no new module. Reuse `REVIEWERS`,
  `REVIEW_KEYS` and `ConfigError`.
- Docblocks on public functions. Update `main`'s docblock. The new helpers are private, but each
  gets a one-line docstring anyway, because the plan template requires it.
- No inline comments. No history in docs: the README and docstring describe what exists.
- Conventional commit with the attribution trailer.

## Commit granularity

One commit:
`feat: add --gate-flags to ship_config for review_gate flags`, containing the source, the tests and
the README line. The story is one feature in one file. The commit is made after task 2.2, when the
suite is green. The state after 1.2 still has an untested `KeyError` path for a bad reviewer and is
not worth a commit of its own. RED states are never committed.

## Follow-up tickets to file

- **Use `--gate-flags` in the ship skills.** Scope: replace the three hand-mapped flags in
  `skills/ship-pipeline/SKILL.md:46-52` and `skills/review-loop/SKILL.md:83` with
  `$(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ship_config.py --gate-flags=<phase> ...)` or the
  equivalent. Deferred because the story puts SKILL.md changes out of scope until the flag exists.

## Stakeholder decisions needed before merge

None. Every fork is reversible and local, and is logged in `decisions.md` (D1 to D6).

## Risks to surface in the PR description

- The output is built from `REVIEW_KEYS` by naming convention (`max_rounds` becomes
  `--max-rounds`). If `review_gate.py` renames a flag, the mismatch shows up loudly when the gate
  runs (argparse exits 2 on an unknown flag), not in this suite.
- `--gate-flags` is read before `--plugin-config` takes its next token. So
  `--plugin-config --gate-flags=plan` behaves differently from before. Both versions are errors
  unless a valid pair follows.
- Repeated `--gate-flags` is last-wins and not tested.

## Footgun checklist

- **Mutable global state in tests under random ordering.** `main` reads `os.environ` directly.
  `patch.dict(..., clear=True)` restores it on exit, which keeps ordering safe and keeps
  `SPICY_*` variables on the developer's machine out of the tests.
- **Ambient project file or git shell-out.** `CLAUDE_PROJECT_DIR` always points at a fresh temp dir,
  so the repo's real `.claude/spicyclaude.json` is never read and git is never called.
- **Stream capture.** `main` resolves `sys.stdout` and `sys.stderr` when `print` runs, so
  `redirect_stdout` and `redirect_stderr` capture both. Assert stderr is `""` on success paths.
- **Wire-boundary type mismatch.** `max_rounds` is an int and is formatted with `str()`. The
  severities are fixed strings from `SEVERITIES` with no spaces, so the line is shell-safe with no
  quoting.
- **Type narrowing.** `reviewer` is `str | None`. `None` means the JSON branch, and an empty string
  is invalid. Check `is None`, not truthiness.
- **Heterogeneous call sites.** Covered by `--plugin-config` pairing with the next token (the
  survey above, and `test_plugin_config_applies`).
- Not applicable: import-time side effects (none added), async, autouse fixtures, `**kwargs`, hot
  path I/O, moved patch targets (`os.environ` is patched in place), schema rollover.

## Tasks

- [x] **1.0 Print the gate flags line for a reviewer (AC-1, AC-2, AC-4, AC-3 invalid-config case)**
  - **Skills**: python-development, test-driven-development
  - **Files**: spicy-ship/scripts/ship_config.py, spicy-ship/scripts/tests/test_ship_config.py
  - **Depends on**: None
  - [x] 1.1 RED: Add the `run_main` helper, the `GateFlagsTest` class, and the AC-1, AC-2 and AC-4 tests
    - `test_plan_prints_one_line_of_gate_flags`: the plan line, exactly one line, empty stderr
    - `test_code_reads_the_code_section`: `--code-rounds=5` shows up only for `code`
    - `test_cli_flag_applies`, `test_env_applies`, `test_project_file_applies`, `test_plugin_config_applies`: each source reaches the line
    - `test_cli_entry_point_defaults_to_sys_argv`: runs the script as a subprocess with `--gate-flags=plan`, returncode 0, stdout `DEFAULT_LINE + "\n"`
    - `test_invalid_config_with_gate_flags_fails_loud`: argv `["--gate-flags=plan", "--min-severity=Nit"]` (gate flag first), exit 1, empty stdout, stderr contains `severity must be one of`. RED now because `_from_flags` hits `--gate-flags` first and stderr reads "unknown argument '--gate-flags'". It belongs here and not in 2.1, because it goes green in 1.2 when `resolve` sees the leftover argv.
    - `test_without_gate_flags_prints_full_json`: a guard, expected green now
    - Run `python3 -m unittest discover -s tests -t .` from `spicy-ship/scripts`. The eight AC-1, AC-2, CLI-entry and invalid-config tests fail on their assertions (exit 1 instead of 0, or the wrong stderr), not with an import or setup error.
  - [x] 1.2 GREEN: Add `GATE_FLAGS`, `_pop_gate_flags(argv: list[str]) -> tuple[str | None, list[str]]` (extraction only, no validation yet), `_gate_flags_line(section: dict[str, int | str]) -> str`, and the single-`print` branch in `main`, which keeps the `sys.argv[1:]` default for `argv=None`. The full suite is green.

- [x] **2.0 Fail loud on an unknown reviewer (AC-3)**
  - **Skills**: python-development, test-driven-development
  - **Files**: spicy-ship/scripts/ship_config.py, spicy-ship/scripts/tests/test_ship_config.py
  - **Depends on**: 1.0
  - [x] 2.1 RED: Write the failing AC-3 tests
    - `test_unknown_reviewer_fails_loud`: subTests `docs`, `Plan`, empty, bare. Exit 1, empty stdout, and stderr contains `--gate-flags must be one of plan, code`. After 1.2, each subTest is reported as an ERROR (an uncaught `KeyError` from `config["review"][reviewer]` escapes `main`), not a FAIL. That counts as the right reason: the check does not exist yet. It is not a setup error.
  - [x] 2.2 GREEN: Add the reviewer check to `_pop_gate_flags`, which raises `ConfigError`. The full suite is green, 80 tests.
  - [x] 2.3 REFACTOR: Update the module docstring and `main`'s docblock, and change `spicy-ship/README.md:54` to the wording above. Run the suite again, then make the single commit.
