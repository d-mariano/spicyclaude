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

These get loaded by `/execute` (and SPICE) on demand:

- **[test-driven-development](skills/test-driven-development/)** — RED/GREEN/REFACTOR cycle, test-double guidance, anti-patterns. Loaded unconditionally during implementation.
- **[python-development](skills/python-development/)** — Python typing, structure, tooling (uv, ruff, mypy, pytest).

## 🔍 Review

- [`/review:pragmatic-code-review`](commands/review/pragmatic-code-review.md) — Pragmatic review of the current branch; focuses on real issues, not nitpicks.
- [`/review:my-developer-plan`](commands/review/my-developer-plan.md) — Independent review of a plan before you start executing it.

## 🤝 Agents

Specialized subagents (planner, researcher, executer, iterator, reviewers, crawler, etc.) live in [`agents/`](agents/). Most users will hit them indirectly through the slash commands above. See **[agents/README.md](agents/README.md)** for the full catalog.

## 📚 More

- **[commands/README.md](commands/README.md)** — All slash commands, including the `aidevtools` PRD/task generators, `/crawl`, and the `/design` router with its greenfield/integrate variants.
- **[agents/README.md](agents/README.md)** — Full agent catalog.
- **[skills/spice/README.md](skills/spice/README.md)** — SPICE deep dive.
- **[references.md](references.md)** — Inspirations, video talks, and external resources.
- **[CLAUDE.md](CLAUDE.md)** — The full philosophy.

## 🌶️ Statusline

A custom statusline ([`statusline.sh`](statusline.sh), wired in [`settings.json`](settings.json)) shows current model, git status, context usage with color thresholds, and session cost — useful for knowing when to switch to SPICE.

## 📄 License

See [`LICENSE`](LICENSE).
