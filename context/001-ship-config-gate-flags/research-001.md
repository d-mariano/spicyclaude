# Research 001: ship_config emits the gate flags for a reviewer

## Summary

The change is small and local to one file plus its test file. `ship_config.main` gains a `--gate-flags=<reviewer>` option that, instead of dumping the resolved config, prints one line of three `review_gate.py` flags for `plan` or `code`. `resolve()` is untouched, so every config source keeps applying. No third-party packages, no web research needed: the work is stdlib string handling over code already in the repo.

Baseline: `python3 -m unittest discover -s tests -t .` from `spicy-ship/scripts` runs 70 tests, all green.

## Files and blast radius

| File | Role | Change |
|---|---|---|
| `/Users/dave/src/spicelabs/spicyclaude/spicy-ship/scripts/ship_config.py` | The CLI. `main` at line 263 prints `json.dumps(resolve(...), indent=2)`. | Yes |
| `/Users/dave/src/spicelabs/spicyclaude/spicy-ship/scripts/tests/test_ship_config.py` | Existing tests exercise `resolve()` directly; none call `main`. | Add tests |
| `/Users/dave/src/spicelabs/spicyclaude/spicy-ship/scripts/review_gate.py` | Consumer of the flags (`--max-rounds`, `--min-severity`, `--fix-floor`, argparse lines 213-215). | No (out of scope) |
| `/Users/dave/src/spicelabs/spicyclaude/spicy-ship/skills/ship-pipeline/SKILL.md` | Lines 46-52 hand-map the three values. | No (out of scope, follow-up) |
| `/Users/dave/src/spicelabs/spicyclaude/spicy-ship/README.md` | Scripts section line 54 describes `ship_config.py` as "resolves configuration and prints JSON". | Optional one-line mention |

Nothing else calls `ship_config` programmatically. The only caller of `main` is the `__main__` guard. `resolve`, `ConfigError`, `project_file` are imported by the tests, so keep their signatures.

## How ship_config works today

- `resolve(argv, env, project_path=None)` splits `--plugin-config` pairs out of argv (`_split_argv`), then `_from_flags` treats every remaining token as `--flag=value`. A token without `=` raises `ConfigError("argument ... must look like --flag=value")`; a flag not in `ARG_PATHS` raises `ConfigError("unknown argument ...")`. So passing `--gate-flags=plan` to `resolve` as it stands would fail loud. The new flag must be removed from argv before `resolve` sees it, or `resolve` must learn to ignore it.
- `_finalize` returns `{"review": {"plan": {...}, "code": {...}}, "questions": {...}}`. Each reviewer section always has exactly `max_rounds`, `min_severity`, `fix_floor`, so no key can be missing.
- The module already defines `REVIEWERS = ("plan", "code")` and `REVIEW_KEYS = ("max_rounds", "min_severity", "fix_floor")`. `REVIEW_KEYS` is in exactly the order AC-1 prints (`max_rounds`, `min_severity`, `fix_floor`), so the line can be built from it with no new constants.
- `main(argv=None)` catches `ConfigError`, prints `ship_config: {exc}` to stderr and returns 1. This is already the AC-3 shape (stderr message, exit 1, nothing on stdout) as long as the error is raised before any `print` to stdout.
- `main` reads `os.environ` directly, and `project_file(env)` consults `CLAUDE_PROJECT_DIR` or `git rev-parse --show-toplevel`. This matters for test design (below).

## Recommended design

Keep `resolve()` pure and unchanged. Put all new behaviour in `main` plus two small helpers in the same file:

1. `_extract_gate_flags(argv)` returns `(reviewer_or_None, remaining_argv)`. It pulls out tokens that equal `--gate-flags` or start with `--gate-flags=`; the reviewer is the text after `=` (empty string when absent or empty). Last occurrence wins, matching how later flags overwrite earlier ones elsewhere.
2. `gate_flags(config, reviewer)` (public, with docblock) validates `reviewer in REVIEWERS`, else raises `ConfigError(f"--gate-flags must be one of {REVIEWERS}, got {reviewer!r}")`, and returns `" ".join(f"--{key.replace('_', '-')} {section[key]}" for key in REVIEW_KEYS)`.
3. `main`: extract, resolve with the remaining argv, then print either `gate_flags(config, reviewer)` or the existing JSON. All inside the existing `try/except ConfigError`.

Order of checks: validating the reviewer name before or after `resolve` both satisfy AC-3. Prefer validating inside `gate_flags` after resolve, so a single code path raises and only one `print` ever runs; stdout stays empty on any error. The only cost is that a bad reviewer plus a bad config reports the config error first, which is fine.

Output safety: every value is either a validated int or one of the `SEVERITIES` strings, so the line is safe to paste into a shell command with no quoting.

AC-4 is satisfied by leaving the JSON branch byte-identical: `print(json.dumps(config, indent=2))`.

Update the module docstring (lines 1-7) with one sentence on `--gate-flags`; docblock the new public function. Optionally add the flag to the README Scripts line. Do not touch any SKILL.md.

### Edge cases to cover or consciously leave

- `--gate-flags=` and `--gate-flags=Plan`, `--gate-flags=review` all fail with the AC-3 message naming `plan` and `code`.
- Bare `--gate-flags` (no `=`): handled as the empty value so the user sees the reviewer list rather than the generic "must look like --flag=value". Decision D2.
- `--gate-flags plan` (space form): `plan` is left in argv and `_from_flags` rejects it as "must look like --flag=value". Consistent with every other flag in the file, so left as is.
- `--plugin-config --gate-flags=plan` would consume the gate flag as a plugin pair. That is a pre-existing quirk of how `--plugin-config` takes the next token; ignore.
- Config errors combined with `--gate-flags` still exit 1 with nothing on stdout, since the error is raised before the print.

## Test design (AC-5, RED first)

Existing tests call `resolve()`; the new ones must call `main()` and capture streams. Pattern, standard library only:

- Capture with `contextlib.redirect_stdout` and `redirect_stderr` into `io.StringIO`, assert on `main([...])`'s return code.
- Hermetic environment is the one trap. `main` reads the real `os.environ` and, without `CLAUDE_PROJECT_DIR`, shells out to git and would pick up the repo's real `.claude/spicyclaude.json` and any ambient `SPICY_*` variables. Use `patch.dict(os.environ, {...}, clear=True)` with `CLAUDE_PROJECT_DIR` pointing at a `TemporaryDirectory` (no `.claude/spicyclaude.json` inside, so defaults apply). With `CLAUDE_PROJECT_DIR` set, git is never invoked, so clearing `PATH` is harmless.
- A small helper such as `run_main(argv, env=None)` returning `(code, stdout, stderr)` keeps each test to a few lines. Put the new tests in a new `GateFlagsTest` class in the existing `test_ship_config.py`, which already uses `unittest`.

Tests, mapped to criteria:

| AC | Test | Assertion |
|---|---|---|
| AC-1 | `--gate-flags=plan` with defaults | stdout is exactly `--max-rounds 3 --min-severity High --fix-floor Medium\n`, stderr empty, code 0 |
| AC-1 | `--gate-flags=code` | same for code; also a case where plan and code differ (`--code-rounds=5`) to prove the right section is read |
| AC-2 | `--plan-rounds=2 --gate-flags=plan` | `--max-rounds 2 --min-severity High --fix-floor Medium` |
| AC-2 | env `SPICY_CODE_MIN_SEVERITY=Critical`, `--gate-flags=code` | line contains `--min-severity Critical` |
| AC-2 (extra) | project file in the temp dir sets `review.plan.max_rounds` | reflected in the line, proving every source applies through `main` |
| AC-3 | `--gate-flags=docs`, `--gate-flags=`, bare `--gate-flags` | code 1, stdout empty, stderr contains `plan` and `code` |
| AC-3 (extra) | invalid config plus `--gate-flags=plan` (`--min-severity=Nit`) | code 1, stdout empty |
| AC-4 | no `--gate-flags` | code 0, `json.loads(stdout)` equals `resolve([], env, project)` result, and stdout equals `json.dumps(..., indent=2) + "\n"` |

RED first: write the tests, run the suite, confirm the new class fails (today `--gate-flags=plan` exits 1 with "unknown argument", so the AC-1 and AC-2 tests fail by assertion, and the AC-3 tests would pass by accident for the wrong reason unless they assert that stderr names `plan` and `code`; keep that assertion so they go RED too). Then implement and confirm green; the full suite should end at 70 plus the new count.

## Third-party types and packages

None needed or wanted. The story requires stdlib only. `argparse` is used in `review_gate.py` but `ship_config.py` hand-parses argv, and converting it to argparse would be a rewrite that risks AC-4 and the existing `--flag=value` semantics. Not recommended.

## Sources

No external sources were needed; behaviour was verified from the repository code and by running the existing suite (70 tests, OK).

## Open Questions

| Question | Working Assumption | Resolve By |
|---|---|---|
| Should bare `--gate-flags` (no `=`) report the reviewer list or the generic "must look like --flag=value" error? | Treat it as an empty value so the message names `plan` and `code` (AC-3 intent: fail loud with the allowed reviewers). | Planner; low stakes |
| Should repeated `--gate-flags` be an error or last-wins? | Last wins, matching how repeated flags overwrite each other elsewhere in the file. | Planner; low stakes |
| Mention the flag in `spicy-ship/README.md`? | Yes, one clause on the existing `ship_config.py` Scripts line; SKILL.md files stay untouched per the story. | Planner; low stakes |
