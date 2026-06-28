# 🌶️ Spicy Claude

A Claude Code **plugin marketplace** of structured, iterative AI-assisted development workflows — from ideation and design through planning, implementation, and review. ✨

## 🤖 Overview

`spicyclaude` is a marketplace that distributes its workflows as a small set of cohesive [Claude Code plugins](https://code.claude.com/docs/en/plugins). Install only what you need; plugins declare their dependencies so the essentials come along automatically.

## 📦 Installation

```bash
/plugin marketplace add d-mariano/spicyclaude
/plugin install spice@spicyclaude
```

Install any subset of the plugins below. Installing a plugin pulls in its dependencies automatically.

## 🧩 Plugins

| Plugin | Namespace | Provides | Depends on |
|--------|-----------|----------|------------|
| **spice** | `/spice:*` | SPICE — Subagent-Powered Iterative Coding Engine: multi-phase SDLC (ideate → research → design → plan → implement → review) with context-efficient subagents | `spicy-dev-skills` |
| **spicy-dev-workflow** | `/spicy-dev-workflow:*` | Single-context research → plan → execute workflow, with the `implementation-planner` skill and plan review | `spicy-dev-skills` |
| **spicy-design** | `/spicy-design:*` | Design docs, feasibility studies, and ticket breakdown (`design-doc`, `feasibility-study`, `design-breakdown` + `writing-tickets`), plus the `design-reviewer` agent | — |
| **spicy-experimental** | `/spicy-experimental:*` | Phased greenfield/integration design workflows (`greenfield-design`, `feature-integration`, `refactor-modifier`) | — |
| **spicy-review** | `/spicy-review:*` | Pragmatic code review and frontend design review of pending changes | `spicy-dev-skills` |
| **spicy-dev-skills** | `/spicy-dev-skills:*` | Language and TDD craft skills: `python-development`, `terraform-development`, `frontend-development`, `test-driven-development`. The shared dependency. | — |
| **spicy-docs** | `/spicy-docs:*` | Generate and maintain `CLAUDE.md` files across a codebase via the `claude-crawler` agent | — |

### Dependency graph

```
spicy-dev-skills  (leaf)
   ▲   ▲   ▲
   │   │   └──── spicy-review        (frontend-development)
   │   └──────── spicy-dev-workflow  (test-driven-development, python-development, …)
   └──────────── spice               (TDD + language skills, by name)

spicy-design        (self-contained)
spicy-experimental  (self-contained)
spicy-docs          (self-contained)
```

> **Namespacing.** Plugin commands are namespaced by plugin name — e.g. `/spicy-dev-workflow:research`, `/spicy-design:design-update`, `/spice:plan`. This prevents collisions across plugins.

## 💎 Core Philosophy: CLAUDE.md

The repo's [`CLAUDE.md`](CLAUDE.md) holds the principles the workflows were tuned against. It is a plain repo file — **not** a plugin component — so read it from the repo if you want the same foundation. (Claude Code does not auto-load a plugin's `CLAUDE.md` into context.)

**SOLID & KISS** — pragmatic over clever; delete more than you add; one class per file.
**Test-Driven Development** — RED → GREEN → REFACTOR; tests are requirements; suite green before every commit.
**Validate at every step** — lint, type-check, and test immediately; fail fast and loud.
**Avoid slop** — no dead code, no needless abstractions, no backwards-compat unless asked.
**MVP mindset** — build for a rapidly iterating startup, not hypothetical futures.

## 🌶️ Enhanced Statusline

The repo also includes a custom statusline script ([`statusline.sh`](statusline.sh), referenced from [`settings.json`](settings.json)) that shows time, directory, git branch, model, real-time context usage (with color thresholds), and session cost. This is personal config, not part of any plugin.

## 🛠️ Local development

Test a plugin without installing:

```bash
claude --plugin-dir ./spice --plugin-dir ./spicy-dev-skills
```

Validate the marketplace and individual plugins:

```bash
claude plugin validate .            # marketplace.json
claude plugin validate ./spice      # a single plugin
```

## 📄 License

See [`LICENSE`](LICENSE).

## 🤝 Contributing

Contributions welcome — a living collection of workflows that evolves with experience. 🌱
