# Shipping Stories and Epics with Composable Claude Code Skills: A Design for `ship-it` and `ship-fleet` on spicyclaude

You can build both orchestrators without dynamic workflows. Two thin orchestrator skills run in the main session and drive layers of nested subagents. That works because Claude Code now lets subagents spawn their own subagents, by default up to three layers below the main conversation. The design has to work around two hard constraints: subagents never get `AskUserQuestion`, and `isolation: worktree` branches from the default branch rather than the parent's `HEAD`. Questions therefore have to bubble up to the main session, and stacked work has to manage its own worktree.

## TL;DR

- **Architecture:** `ship-it` and `ship-fleet` are thin, user-invoked skills that run inline in the main session. They delegate to per-story subagents, which delegate to phase subagents (explorer → planner → plan-reviewer ⇄ fixer → executor → code-reviewer ⇄ fixer). All artifacts go to `/context/[nnn]-{feature}/`. A shared `review-loop` reference skill and a deterministic gate script enforce max 3 rounds and min severity `high`. Arguments, env vars, a project config file and plugin `userConfig` can each override both values.
- **Questions:** The default is `auto`: phase agents pick the recommended option and log it to `decisions.md`, and the log is copied into the PR body. `raise` mode batches the questions at checkpoints and asks them from the main session. That is the only place `AskUserQuestion` exists, since Claude Code removes it from every subagent. I recommend `auto` plus an "irreversible-only" escalation guard. A PreToolUse hook gives you a deterministic way to auto-answer legacy `AskUserQuestion` calls.
- **Branch and stacking:** I could not verify the plugin/skills-migration branches or PRs. Main has no `.claude-plugin/` yet. Stack this work on the migration branch only if that branch already has a valid `plugin.json` and the four core commands as skills; otherwise start from main with a minimal plugin layer. For epics, use the official `gh stack` extension (`github/gh-stack`), which is a separate extension, not built into `gh`. Only its non-interactive commands (`init`, `add`, `submit --auto`, `rebase --upstack`, `sync`, `view --json`) are safe for agents.

## Key Findings

### 1. The existing repo (what I could and could not verify)

**Verified on `main`** (landing page as of this research: public, MIT, 80 commits):

- **Top level:** `agents/`, `commands/`, `hooks/`, `skills/`, `CLAUDE.md`, `README.md`, `settings.json`, `statusline.sh`. There is **no `.claude-plugin/` directory**, so main is not a plugin yet. [github](https://github.com/d-mariano/spicyclaude)
- **Philosophy (from `CLAUDE.md`):** "SOLID + KISS, delete more than you add, fail fast and loud, TDD by default, MVP over enterprise." [github](https://github.com/d-mariano/spicyclaude)
- **Implementation loop:** the README describes "The day-to-day scope → plan → build loop, all in a single context window. Each phase writes into `/context/[nnn]-{feature}/`." [github](https://github.com/d-mariano/spicyclaude)

| Component | Path | What it does (per README) | Inputs → Outputs |
|---|---|---|---|
| `/explore` | `commands/explore.md` | "no-output conversational scoping pass" | conversation → nothing persisted |
| `/research` | `commands/research.md` | deep-dive that "pushes hard on PRD/AC ambiguity upstream" | PRD/story → `research-[nnn].md` |
| `/planner` | `commands/planner.md` | pre-flight findings, AC trace table, full signatures, RED/GREEN/REFACTOR tasks, footgun checklist | PRD + research → `plan-[nnn].md` |
| `/execute` | `commands/execute.md` | walks plan checklist, loads annotated skills, runs full suite, commits per parent task | plan → code + commits + `progress-[nnn].md` |
| `/review:pragmatic-code-review` | `commands/review/pragmatic-code-review.md` | "focuses on real issues, not nitpicks" | current branch diff → review |
| `/review:my-developer-plan` | `commands/review/my-developer-plan.md` | "Independent review of a plan before you start executing it" | plan → review |
| Other commands | `commands/README.md` | `aidevtools` PRD/task generators, `/crawl`, `/design` router (greenfield/integrate) | — |
| Design skills | `skills/design-doc`, `skills/design-breakdown`, `skills/feasibility-study` | PRD → TDD; TDD → epics/stories with ACs and dependencies; TDD pressure-test | — |
| SPICE | `skills/spice` | "Subagent-Powered Iterative Coding Engine": ideation/research/design/planning in subagents | — |
| Support skills | `skills/test-driven-development`, `skills/python-development` | loaded by `/execute` on demand; TDD "loaded unconditionally" | — |
| Agents | `agents/` (catalog in `agents/README.md`) | planner, researcher, executer, iterator, reviewers, crawler | — |

**Not verified (be explicit about this before building):**

- The branch list and any open PRs. The plugin and skills-migration branches you mention could not be fetched.
- The exact command bodies, including how each one phrases its `AskUserQuestion` / open-questions instructions.
- The contents of `hooks/`.
- Commands literally named `review-heavy` or "plan reviewer". On main's README, the closest matches are `/review:pragmatic-code-review` and `/review:my-developer-plan`. `review-heavy` may live on another branch.

The design below treats those as the code-review and plan-review building blocks. Run `git branch -a`, `gh pr list --state all`, and `grep -rn AskUserQuestion commands agents skills` locally to close this gap. This takes five minutes and changes only the "branch recommendation" section.

`design-breakdown` matters a lot here. It already turns a TDD into "epics and user stories with acceptance criteria, dependencies, and explicit out-of-scope items", which is exactly the input `ship-fleet` needs to decompose an epic. [github](https://github.com/d-mariano/spicyclaude) Reuse it; don't rebuild it.

### 2. Branch recommendation

Decide with this rule:

- **Stack on the migration branch** if it already has (a) a `.claude-plugin/plugin.json` that passes `claude plugin validate`, and (b) `explore/research/planner/execute` converted to `skills/<name>/SKILL.md`. Do it literally as a stack: `gh stack init --base main <migration-branch>` adopts the existing branch as layer 1, then `gh stack add ship-skills` puts this work on top. The plugin migration can then be reviewed and merged first, and your work rebases automatically.
- **Otherwise start from main.** Add a minimal plugin layer as the first PR of your own stack, then build on top.
  - A minimal layer is `.claude-plugin/plugin.json` plus `marketplace.json` with `source: "./"`. [claude](https://code.claude.com/docs/en/plugins/publish)
  - It costs almost nothing, because Claude Code docs say "Custom commands have been merged into skills". A file at `.claude/commands/deploy.md` and one at `.claude/skills/deploy/SKILL.md` "both create `/deploy` and work the same way", and existing `commands/` files keep working. [claude](https://code.claude.com/docs/en/skills)
  - The migration is therefore not a prerequisite. Only the new building blocks *must* be skills, because they need supporting files, `disable-model-invocation`, and preloading.

Either way, the plugin namespace changes command names: plugin skills are invoked as `/plugin-name:skill-name`, so `/execute` becomes `/spicyclaude:execute`. [claude](https://code.claude.com/docs/en/agent-sdk/plugins) [claude](https://code.claude.com/docs/en/skills) Note this in the README.

### 3. Platform constraints that shape the design (official docs)

| Capability | What the docs say | Design consequence |
|---|---|---|
| Nested subagents | "By default, a subagent can spawn subagents of its own, up to three layers below the main conversation. At the depth limit, Claude Code withholds the Agent tool." Depth is set by `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. [claude](https://code.claude.com/docs/en/sub-agents) | Main → story-runner (L1) → phase agents (L2) → review lenses (L3) fits exactly. Set the env var explicitly; the default changed several times in mid-2026 (official Claude Code changelog, v2.1.217 and v2.1.219). |
| Spawn restriction | In a subagent definition, listing `Agent` in `tools` allows spawning, but "any type list inside the parentheses is ignored". [claude](https://code.claude.com/docs/en/sub-agents) | You can't hard-restrict which agents a story-runner spawns. Constrain it by prompt, and audit with `SubagentStart` hooks. |
| Questions | `AskUserQuestion` is in the list of tools removed from every subagent. [claude](https://code.claude.com/docs/en/sub-agents) | Only the main session can ask. Subagents must return questions as data. |
| Workflows | `Workflow` is also removed from every subagent. [claude](https://code.claude.com/docs/en/sub-agents) | A subagent can't launch a dynamic workflow, so workflows could only ever be top-level. |
| Skills in subagents | The `skills` field preloads the full content. Subagents "can still invoke unlisted project, user, and plugin skills through the Skill tool". [claude](https://code.claude.com/docs/en/sub-agents) Skills with `disable-model-invocation: true` can't be preloaded. [claude](https://code.claude.com/docs/en/sub-agents) [claude](https://code.claude.com/docs/en/skills) | Keep the user-facing `ship-it` as `disable-model-invocation: true`. Put the reusable procedure in a separate preloadable skill (`ship-pipeline`). |
| Skill in a subagent | `context: fork` runs the skill in a new subagent of the `agent` type. [claude](https://code.claude.com/docs/en/skills) [claude](https://code.claude.com/docs/en/skills) | Don't fork the orchestrators: they would lose `AskUserQuestion`. Fork is fine for leaf skills such as `research`. |
| Worktrees | `isolation: worktree` uses a temporary worktree "branched by default from your default branch rather than the parent session's HEAD", auto-cleaned if there are no changes. [claude](https://code.claude.com/docs/en/sub-agents) | That breaks stacking. Story layers must be built on the layer below, so `ship-fleet` creates its own worktree and runs layers sequentially in it. Use `isolation: worktree` only for independent `ship-it` runs. |
| Models / effort | Order: per-invocation `model` → frontmatter `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → main model. [claude](https://code.claude.com/docs/en/agent-sdk/subagents) `effort` is set per agent. [claude](https://code.claude.com/docs/en/sub-agents) [claude](https://code.claude.com/docs/en/agent-sdk/typescript) | Use opus for planner and reviewers, sonnet for executor and fixer, haiku for status and gh plumbing. Spend effort where judgment matters. |
| Background | Subagents spawned from the main conversation start in the background. Background subagents surface permission prompts in the main session. [claude](https://code.claude.com/docs/en/agent-sdk/subagents) [claude](https://code.claude.com/docs/en/whats-new/2026-w27) Background subagents keep only a reduced built-in tool set (Read, Grep, Glob, Bash, Edit, Write, Skill, SendMessage, …). [claude](https://code.claude.com/docs/en/sub-agents) | Pre-approve `Bash(gh stack *)`, `Bash(git *)` and your test commands in settings, or long runs will stall on prompts. |
| Hooks | Frontmatter `Stop` hooks in an agent are converted to `SubagentStop`. Exit code 2 sends Claude back to work. [claude +2](https://code.claude.com/docs/en/best-practices) Plugin subagents ignore `hooks`, `mcpServers`, and `permissionMode`. [claude](https://code.claude.com/docs/en/sub-agents) | Validate findings JSON with plugin-level `hooks/hooks.json` (`SubagentStop` matcher = agent type), not agent frontmatter. |
| Context | Each subagent has its own context window and returns a summary. [Substack](https://responseawareness.substack.com/p/sub-agents-in-claude-code-the-subagent) `maxTurns` and `autoCompactWindow` are available. [claude](https://code.claude.com/docs/en/agent-sdk/typescript) Agent descriptions over 15,000 tokens combined trigger a warning. [claude](https://code.claude.com/docs/en/sub-agents) | Keep agent descriptions short, put the detail in bodies, and have the orchestrator keep only status lines. |

### 4. Dynamic workflows vs. composable skills

The official docs define a dynamic workflow as "a JavaScript script that orchestrates many subagents at once", which "a runtime executes … in the background". The key difference from skills is "who holds the plan": with skills, Claude decides turn by turn and "intermediate results live" in Claude's context window; with workflows, "the script" decides and intermediate results live in script variables. [claude](https://code.claude.com/docs/en/workflows)

- **What workflows add:**
  - Scale: up to 16 concurrent agents by default and 1,000 agents per run. [claude](https://code.claude.com/docs/en/workflows)
  - Structured output: an `agent()` `schema` with retries. [claude](https://code.claude.com/docs/en/workflows)
  - Resumability within the session. [claude](https://code.claude.com/docs/en/workflows)
  - Shareable `.claude/workflows/*.js`, which plugins can ship in a `workflows/` directory. [claude](https://code.claude.com/docs/en/workflows)
- **Why they're the wrong core for this design:**
  - **"No mid-run user input"** — a run pauses only for permission prompts and usage limits, and the docs say "For sign-off between stages, run each stage as its own workflow". [claude](https://code.claude.com/docs/en/workflows) That directly conflicts with `raise` mode and with any checkpoint batching.
  - The `Workflow` tool is unavailable to subagents. [claude](https://code.claude.com/docs/en/sub-agents)
  - Scripts can't touch the filesystem or shell directly; agents do that. [claude](https://code.claude.com/docs/en/workflows) Your `gh stack` choreography would end up as prompts anyway.
  - Workflows "consume meaningfully more usage", with a `Large workflow` warning above 25 agents or 1.5M projected tokens. [claude](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code) [claude](https://code.claude.com/docs/en/workflows)
- **What skills give up:** determinism. Claude may skip a step. Recover most of it with (a) a gate script that computes the loop decision from JSON, and (b) `SubagentStop` hooks that reject malformed reviewer output. The best-practices docs make the same point: for things that must always happen, use deterministic controls (hooks), not prose. [claude](https://code.claude.com/docs/en/best-practices)

**Conclusion:** composable skills, nested subagents and two orchestrator skills fully meet the requirements, and they support interactive escalation, which workflows can't. Keep one seam open. The review loop is defined by a JSON contract, so a future `review-sweep.js` workflow could replace the in-skill loop for very large fan-outs (e.g. 10+ parallel review lenses on a big PR) without changing any agent.

### 5. `gh stack` status as of late 2026

- **What it is:** an official GitHub CLI **extension**, `gh extension install github/gh-stack`, not built into `gh`. GitHub also ships an agent skill: `gh skill install github/gh-stack`. [github](https://docs.github.com/en/pull-requests/get-started/stacked-prs-quickstart) [betterstack](https://betterstack.com/community/guides/linux/github-stacked/)
- **Release dates:** GitHub's changelog announced the public preview on July 30, 2026. Its "Stacked pull requests generally available" entry (October 6, 2026) says stacked PRs "are available on all github.com plans and will be included in an upcoming GitHub Enterprise Server release", and that "the gh stack extension for GitHub CLI now supports Git worktrees."
- **Version requirements (conflicting in GitHub's own docs):** the CLI reference says `gh` 2.0+ and Git 2.36+; the quickstart says `gh` 2.90.0+ and Git 2.20+. [betterstack +2](https://betterstack.com/community/guides/linux/github-stacked/) Require **gh ≥ 2.90 and Git ≥ 2.36** to satisfy both.

**Agent-relevant commands and flags (from the CLI reference):**

| Command | Use in ship-fleet | Gotchas |
|---|---|---|
| `gh stack init --base <trunk> b1 [b2 …]` | create or adopt the stack | enables `git rerere` automatically [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack add <branch>` | new layer per story | "You must run this command while on the topmost branch" [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack view --json` | status reporting | `--json`/`--short` work in non-interactive terminals [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack submit --auto [--open]` | push and create/update PRs, link the stack | `--auto` creates **drafts** unless `--open`; non-interactive terminals skip the editor [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack rebase [--upstack/--downstack/--continue/--abort]` | cascade after lower-layer changes | switches to `--onto` automatically after a merged PR; pauses on conflicts [github +2](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack push` | push all active branches | `--force-with-lease` per branch; **not atomic** [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) [github](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-stacked-pull-requests) |
| `gh stack sync [--prune]` | after merges / trunk moves | "safe to run in automation"; in a non-interactive terminal a divergence **aborts and exits successfully**, so check state afterwards [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack checkout <n|pr|branch> --print-path` | locate worktrees | prints only a raw path; never prompts [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack merge <pr> --yes --squash` | optional final landing | all-or-nothing; "You cannot bypass merge requirements" [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack modify` | **don't use from agents** | interactive TUI; use `unstack` + `init` to restructure instead [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |
| `gh stack link` | adopt PRs made elsewhere | additive only [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) |

**Other limitations:**
- All branches must be in the same repository. [github](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs)
- Server-side rebases from the website are not signed, so rebase via the CLI if you require signed commits. [github](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests) [github](https://github.com/github/docs/blob/main/content/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests.md)
- Exit code 9 means stacked PRs aren't enabled for the repository. [github](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) `ship-fleet` should preflight for this and fall back to plain branch-on-branch PRs with `git rebase --update-refs`.

## Details

### 6. Recommended architecture

```
USER
 │  /spicyclaude:ship-fleet EPIC.md --max-review-rounds=3 --min-severity=high --questions=auto
 ▼
L0 MAIN SESSION — ship-fleet skill (inline; owns AskUserQuestion, gh stack, fleet.json)
 │   ├─ decompose: Skill(design-breakdown) or fleet-decomposer agent → stories.json (ordered DAG)
 │   ├─ CHECKPOINT A (raise/batch modes): ask batched questions about decomposition
 │   └─ for each story in topological order (sequential in one fleet worktree):
 │        gh stack add <story-branch>
 ▼
L1 story-runner agent (preloads ship-pipeline; tools include Agent)  ← same pipeline ship-it uses
 │   ├─ explorer (L2, read-only, sonnet)      