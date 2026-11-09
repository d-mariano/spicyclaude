#!/usr/bin/env python3
"""Resolve spicy-ship configuration and print it as JSON.

--gate-flags=plan|code prints that reviewer's review_gate.py flags on one line instead.

Precedence, highest first: CLI flags, SPICY_* environment variables, the
project file .claude/spicyclaude.json at the project root, plugin userConfig
values passed as --plugin-config KEY=VALUE, built-in defaults. An empty value
in any source means unset. Invalid input exits non-zero.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from severities import SEVERITIES, at_least  # noqa: E402

MODES = ("auto", "raise", "batch")
ESCALATIONS = ("irreversible", "external")
REVIEWERS = ("plan", "code")
REVIEW_KEYS = ("max_rounds", "min_severity", "fix_floor")
PROJECT_FILE = Path(".claude", "spicyclaude.json")
GATE_FLAGS = "--gate-flags"

DEFAULTS = {
    "review": {"default": {"max_rounds": 3, "min_severity": "High", "fix_floor": "Medium"}},
    "questions": {"mode": "auto", "escalate": ["irreversible"]},
}

ARG_PATHS = {
    "--max-review-rounds": ("review", "default", "max_rounds"),
    "--min-severity": ("review", "default", "min_severity"),
    "--fix-floor": ("review", "default", "fix_floor"),
    "--plan-rounds": ("review", "plan", "max_rounds"),
    "--code-rounds": ("review", "code", "max_rounds"),
    "--plan-min-severity": ("review", "plan", "min_severity"),
    "--code-min-severity": ("review", "code", "min_severity"),
    "--questions": ("questions", "mode"),
    "--escalate": ("questions", "escalate"),
}

ENV_PATHS = {
    "SPICY_MAX_REVIEW_ROUNDS": ("review", "default", "max_rounds"),
    "SPICY_REVIEW_MIN_SEVERITY": ("review", "default", "min_severity"),
    "SPICY_REVIEW_FIX_FLOOR": ("review", "default", "fix_floor"),
    "SPICY_PLAN_MAX_ROUNDS": ("review", "plan", "max_rounds"),
    "SPICY_CODE_MAX_ROUNDS": ("review", "code", "max_rounds"),
    "SPICY_PLAN_MIN_SEVERITY": ("review", "plan", "min_severity"),
    "SPICY_CODE_MIN_SEVERITY": ("review", "code", "min_severity"),
    "SPICY_QUESTION_MODE": ("questions", "mode"),
    "SPICY_QUESTION_ESCALATE": ("questions", "escalate"),
}

PLUGIN_CONFIG_PATHS = {
    "maxReviewRounds": ("review", "default", "max_rounds"),
    "minReviewSeverity": ("review", "default", "min_severity"),
    "questionMode": ("questions", "mode"),
}


class ConfigError(Exception):
    """Raised for any unknown key or invalid value. Never swallowed."""


def resolve(argv, env, project_path=None):
    """Merge every config source in precedence order and return the resolved config."""
    flags, plugin_pairs = _split_argv(argv)
    layers = [
        DEFAULTS,
        _from_plugin_config(plugin_pairs),
        _from_project_file(project_path if project_path is not None else project_file(env)),
        _from_paths(ENV_PATHS, env, "environment variable"),
        _from_flags(flags),
    ]
    merged = {}
    for layer in layers:
        _deep_merge(merged, layer)
    return _finalize(merged)


def project_file(env, cwd=None):
    """Locate .claude/spicyclaude.json from CLAUDE_PROJECT_DIR or the git top level, never the cwd."""
    root = env.get("CLAUDE_PROJECT_DIR")
    if not root:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True
            )
        except OSError as exc:
            raise ConfigError(f"cannot run git to locate the project root ({exc}); set CLAUDE_PROJECT_DIR") from exc
        if result.returncode != 0:
            raise ConfigError("cannot locate the project root: set CLAUDE_PROJECT_DIR or run inside a git repository")
        root = result.stdout.strip()
    return Path(root) / PROJECT_FILE


def _split_argv(argv):
    flags, plugin_pairs = [], []
    items = iter(argv)
    for raw in items:
        if raw == "--plugin-config":
            plugin_pairs.append(next(items, None))
        elif raw.startswith("--plugin-config="):
            plugin_pairs.append(raw.split("=", 1)[1])
        else:
            flags.append(raw)
    if None in plugin_pairs:
        raise ConfigError("--plugin-config needs KEY=VALUE")
    return flags, plugin_pairs


def _from_flags(flags):
    layer = {}
    for raw in flags:
        if "=" not in raw:
            raise ConfigError(f"argument {raw!r} must look like --flag=value")
        flag, value = raw.split("=", 1)
        if flag not in ARG_PATHS:
            raise ConfigError(f"unknown argument {flag!r}; known: {', '.join(sorted(ARG_PATHS))}")
        if value == "":
            continue
        _set(layer, ARG_PATHS[flag], _parse(ARG_PATHS[flag], value, f"argument {flag}"))
    return layer


def _from_plugin_config(pairs):
    layer = {}
    for pair in pairs:
        if "=" not in pair:
            raise ConfigError(f"--plugin-config value {pair!r} must look like KEY=VALUE")
        key, value = pair.split("=", 1)
        if key not in PLUGIN_CONFIG_PATHS:
            raise ConfigError(f"unknown plugin option {key!r}; known: {', '.join(sorted(PLUGIN_CONFIG_PATHS))}")
        if value == "":
            continue
        _set(layer, PLUGIN_CONFIG_PATHS[key], _parse(PLUGIN_CONFIG_PATHS[key], value, f"plugin option {key}"))
    return layer


def _from_paths(table, source, label):
    layer = {}
    for name, path in table.items():
        value = source.get(name)
        if value is None or value == "":
            continue
        _set(layer, path, _parse(path, value, f"{label} {name}"))
    return layer


def _from_project_file(path):
    path = Path(path)
    if not path.exists() and not path.is_symlink():
        return {}
    if not path.is_file():
        raise ConfigError(f"{path} exists but is not a readable file")
    try:
        data = json.loads(path.read_text())
    except OSError as exc:
        raise ConfigError(f"{path} cannot be read: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{path} is not valid JSON: {exc}") from exc
    _validate_project_shape(data, path)
    return data


def _validate_project_shape(data, project_file):
    _require_object(data, project_file, "top level")
    allowed_top = {"review", "questions"}
    unknown = set(data) - allowed_top
    if unknown:
        raise ConfigError(f"{project_file}: unknown top-level keys {sorted(unknown)}")
    review = data.get("review", {})
    _require_object(review, project_file, "review")
    for reviewer, section in review.items():
        if reviewer not in ("default",) + REVIEWERS:
            raise ConfigError(f"{project_file}: unknown review section {reviewer!r}")
        _require_object(section, project_file, f"review.{reviewer}")
        for key, value in section.items():
            if key not in REVIEW_KEYS:
                raise ConfigError(f"{project_file}: unknown review key {key!r}")
            section[key] = _parse(("review", reviewer, key), value, f"{project_file} review.{reviewer}.{key}")
    questions = data.get("questions", {})
    _require_object(questions, project_file, "questions")
    for key, value in questions.items():
        if key not in ("mode", "escalate"):
            raise ConfigError(f"{project_file}: unknown questions key {key!r}")
        questions[key] = _parse(("questions", key), value, f"{project_file} questions.{key}")


def _require_object(value, project_file, where):
    if not isinstance(value, dict):
        raise ConfigError(f"{project_file}: {where} must be a JSON object, got {type(value).__name__}")


def _parse(path, value, where):
    leaf = path[-1]
    if leaf == "max_rounds":
        rounds = _as_int(value)
        if rounds is None:
            raise ConfigError(f"{where}: max_rounds must be an integer, got {value!r}")
        if rounds < 1:
            raise ConfigError(f"{where}: max_rounds must be at least 1, got {rounds}")
        return rounds
    if leaf in ("min_severity", "fix_floor"):
        if value not in SEVERITIES:
            raise ConfigError(f"{where}: severity must be one of {SEVERITIES}, got {value!r}")
        return value
    if leaf == "mode":
        if value not in MODES:
            raise ConfigError(f"{where}: question mode must be one of {MODES}, got {value!r}")
        return value
    if leaf == "escalate":
        items = value if isinstance(value, list) else [v for v in str(value).split(",") if v]
        if items == ["none"]:
            return []
        for item in items:
            if item not in ESCALATIONS:
                raise ConfigError(f"{where}: escalate entries must be in {ESCALATIONS} or 'none', got {item!r}")
        return items
    raise ConfigError(f"{where}: unknown config key {leaf!r}")


def _as_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


def _set(layer, path, value):
    node = layer
    for key in path[:-1]:
        node = node.setdefault(key, {})
    node[path[-1]] = value


def _deep_merge(target, source):
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value if not isinstance(value, dict) else json.loads(json.dumps(value))


def _finalize(merged):
    default = merged["review"]["default"]
    review = {}
    for reviewer in REVIEWERS:
        section = dict(default)
        section.update(merged["review"].get(reviewer, {}))
        if at_least(section["fix_floor"], section["min_severity"]) and section["fix_floor"] != section["min_severity"]:
            raise ConfigError(
                f"review.{reviewer}: fix_floor {section['fix_floor']!r} is stricter than "
                f"min_severity {section['min_severity']!r}; a fix floor can only be equal or looser"
            )
        review[reviewer] = section
    return {"review": review, "questions": merged["questions"]}


def _pop_gate_flags(argv: list[str]) -> tuple[str | None, list[str]]:
    """Split --gate-flags out of argv and return (reviewer or None, remaining argv).

    The last occurrence wins; a bare flag counts as an empty value. Raises ConfigError naming
    the allowed reviewers when the flag is present with anything other than plan or code.
    """
    reviewer, rest = None, []
    for raw in argv:
        if raw == GATE_FLAGS or raw.startswith(GATE_FLAGS + "="):
            reviewer = raw.partition("=")[2]
        else:
            rest.append(raw)
    if reviewer is not None and reviewer not in REVIEWERS:
        raise ConfigError(f"{GATE_FLAGS} must be one of {', '.join(REVIEWERS)}, got {reviewer!r}")
    return reviewer, rest


def _gate_flags_line(section: dict[str, int | str]) -> str:
    """Render one resolved review section as review_gate.py flags, in REVIEW_KEYS order."""
    return " ".join(f"--{key.replace('_', '-')} {section[key]}" for key in REVIEW_KEYS)


def main(argv=None):
    """CLI entry point: print the resolved config, or with --gate-flags=plan|code that reviewer's
    review_gate.py flags on one line. On error print the message to stderr and exit non-zero."""
    try:
        argv = sys.argv[1:] if argv is None else argv
        reviewer, rest = _pop_gate_flags(argv)
        config = resolve(rest, os.environ)
        if reviewer is None:
            print(json.dumps(config, indent=2))
        else:
            print(_gate_flags_line(config["review"][reviewer]))
    except ConfigError as exc:
        print(f"ship_config: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
