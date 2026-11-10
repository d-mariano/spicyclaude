# 🌶️ Spicy Claude

A collection of slash commands, agents, and skills for Claude Code organized around a structured **Design → Implement → Review** loop.

The whole repo is opinionated by [`CLAUDE.md`](CLAUDE.md): SOLID + KISS, delete more than you add, fail fast and loud, TDD by default, MVP over enterprise. Every workflow below reinforces those principles.

## 🎨 Design

Shape the work before writing it.

- **[skills/design-doc](skills/design-doc/)** — Walks a PRD into a Technical Design Document (TDD) section-by-section, with a companion contracts file for wire-level shapes.
- **[skills/design-breakdown](skills/design-breakdown/)** — Turns a TDD into epics and user stories with acceptance criteria, dependencies, and explicit out-of-scope items.
- **[skills/feasibility-study](skills/feasibility-study/)** — Pressure-tests a TDD with cold-read research and walks you through the findings.

## ⚡ Implementation

The day-to-day **scope → plan → build** loop, all in a single context window. Each phase writes into `/context/[nnn]-{feature}/` so the next phase can pick up where the last one left off.

1. **Scope** with [`/explore`](commands/explore.md) or [`/research`](commands/research.md). `/explore` is a no-output conversational scoping pass — use it when you're still deciding what the work is. [`/research`](commands/research.md) persists a deep-dive to `research-[nnn].md` and pushes hard on PRD/AC ambiguity upstream while you're still context-loaded.
2. **Plan** with [`/planner`](commands/planner.md). Reads the PRD and research and produces `plan-[nnn].md` with pre-flight findings, an AC trace table, full function signatures, RED/GREEN/REFACTOR task structure, and a footgun checklist.
3. **Build** with [`/execute`](commands/execute.md). Walks the plan's task checklist, loads the skills each parent task annotates, runs the full suite and commits per parent task, and tracks state in `progress-[nnn].md`.

## 🔬 SPICE (experimental)

**S**ubagent-**P**owered **I**terative **C**oding **E**ngine — a heavier SDLC workflow that runs ideation, research, design, and planning in subagents and keeps the main context lean for implementation. Reach for it when context window management matters: large multi-phase features, long sessions, or when you're brushing up against context limits with the standard flow.

→ **[skills/spice](skills/spice/)**

## 🧪 Skills that complement every workflow

The **[spicy-skills](spicy-skills/)** plugin holds the craft skills `/execute`, `/planner`, SPICE and the ship agents load by name. Install it even if you use this repo as your `~/.claude` rather than through the marketplace; those commands stop at their first `Skill()` call without it.

```bash
/plugin install spicy-skills --marketplace d-mariano/spicyclaude
```

Skills in the plugin:

- **[test-driven-development](spicy-skills/skills/test-driven-development/)** — RED/GREEN/REFACTOR cycle, test-double guidance, anti-patterns. Loaded unconditionally during implementation.
- **[python-development](spicy-skills/skills/python-development/)** — Python typing, structure, tooling (uv, ruff, mypy, pytest).
- **[terraform-development](spicy-skills/skills/terraform-development/)** — Modules, state, security, testing.

## 🔍 Review

The review suite ships as the **[spicy-review](spicy-review/)** plugin: `/spicy-review:review-heavy` for a risk-tiered, multi-reviewer pass with verification, `/spicy-review:code-review-light` for a fast single pass. Both score against one shared severity rubric and never approve or merge.

Legacy single-prompt reviews remain as commands: [`/review:pragmatic-code-review`](commands/review/pragmatic-code-review.md) and [`/review:my-developer-plan`](commands/review/my-developer-plan.md).

## 🚢 Ship

**[spicy-ship](spicy-ship/)** ships one story unattended: `/spicy-ship:ship-it <story>` explores, plans, reviews the plan, implements, reviews the code, and opens a PR, delegating each phase to an agent. Its `review-loop` has a deterministic gate script and its `question-policy` says when you get asked.

## 📦 Plugins

The repo is a Claude Code plugin marketplace. Plugins live in their own folders and are listed in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json).

```bash
/plugin marketplace add d-mariano/spicyclaude
/plugin install spicy-review --marketplace d-mariano/spicyclaude
```

Validate locally with `claude plugin validate --strict .` for the marketplace or `claude plugin validate --strict ./spicy-ship` for one plugin.

## 🤝 Agents

Specialized subagents (planner, researcher, executer, iterator, reviewers, crawler, etc.) live in [`agents/`](agents/). Most users will hit them indirectly through the slash commands above. See **[agents/README.md](agents/README.md)** for the full catalog.

## 📚 More

- **[commands/README.md](commands/README.md)** — All slash commands, including the `aidevtools` PRD/task generators, `/crawl`, and the `/design` router with its greenfield/integrate variants.
- **[agents/README.md](agents/README.md)** — Full agent catalog.
- **[skills/spice/SKILL.md](skills/spice/SKILL.md)** — SPICE deep dive.
- **[CLAUDE.md](CLAUDE.md)** — The full philosophy.

## 🌶️ Statusline

A custom statusline ([`statusline.sh`](statusline.sh), wired in [`settings.json`](settings.json)) shows current model, git status, context usage with color thresholds, and session cost — useful for knowing when to switch to SPICE.

## 📄 License

See [`LICENSE`](LICENSE).
