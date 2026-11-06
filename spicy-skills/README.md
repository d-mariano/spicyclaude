# spicy-skills

Craft skills that other plugins load while planning and implementing. Shared leaf dependency; nothing here invokes a subagent or asks a question.

```bash
/plugin marketplace add d-mariano/spicyclaude
/plugin install spicy-skills --marketplace d-mariano/spicyclaude
```

- [test-driven-development](skills/test-driven-development/SKILL.md): RED, GREEN, REFACTOR, test doubles, test-case discovery, anti-patterns. Loaded unconditionally during implementation; it self-gates on config-only, type-only and rename work.
- [python-development](skills/python-development/SKILL.md): typing, project structure, tooling with uv, ruff, mypy and pytest.
- [terraform-development](skills/terraform-development/SKILL.md): module development, state, security, testing, troubleshooting.

Plans annotate each parent task with a `**Skills:**` field drawn from these names; executors load them with `Skill(<name>)`.
