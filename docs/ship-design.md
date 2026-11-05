# Shipping Stories and Epics with Composable Claude Code Skills: A Design for `ship-it` and `ship-fleet` on spicyclaude

You can build both orchestrators without dynamic workflows. Two thin orchestrator skills run in the main session and drive layers of nested subagents. That works because Claude Code now lets subagents spawn their own subagents, by default up to three layers below the main conversation. The design has to work around two hard constraints: subagents never get `AskUserQuestion`, and `isolation: worktree` branches from the default branch rather than the parent's `HEAD`. Questions therefore have to bubble up to the main session, and stacked work has to manage its own worktree.

## TL;DR

- **Architecture:** `ship-it` and `ship-fleet` are thin, user-invoked skills that run inline in the main session. They delegate to per-story subagents, which delegate to phase subagents (explorer → planner → plan-reviewer ⇄ fixer → executor → code-reviewer ⇄ fixer). All artifacts go to `/context/[nnn]-{feature}/`. A shared `review-loop` reference skill and a deterministic gate script enforce max 3 rounds and min severity `high`. Arguments, env vars, a project config file and plugin `userConfig` can each override both values.
- **Questions:** The default is `auto`: phase agents pick the recommended option and log it to `decisions.md`, and the log is copied into the PR body. `raise` mode batches the questions at checkpoints and asks them from the main session. That is the only place `AskUserQuestion` exists, since Claude Code removes it from every subagent. I recommend `auto` plus an "irreversible-only" escalation guard. A PreToolUse hook gives you a deterministic way to auto-answer legacy `AskUserQuestion` calls.
- **Branch and stacking:** I could not verify the plugin/skills-migration branches or PRs. Main has no `.claude-plugin/` yet. Stack this work on the migration branch only if that branch already has a valid `plugin.json` and the four core commands as skills; otherwise start from main with a minimal plugin layer. For epics, use the official `gh stack` extension (`github/gh-stack`), which is a separate extension, not built into `gh`. Only its non-interactive commands (`init`, `add`, `submit --auto`, `rebase --upstack`, `sync`, `view --json`) are safe for agents.

## Key Findings

### 1. The existing repo (what I could and could not verify)

**Verified on `main`** (landing page as of this research: public, MIT, 80 commits):

- **Top level:** `agents/`, `commands/`, `hooks/`, `skills/`, `CLAUDE.md`, `README.md`, `settings.json`, `statusline.sh`. There is **no `.claude-plugin/` directory**, so main is not a plugin yet.\[1\]
- **Philosophy (from `CLAUDE.md`):** "SOLID + KISS, delete more than you add, fail fast and loud, TDD by default, MVP over enterprise."\[1\]
- **Implementation loop:** the README describes "The day-to-day scope → plan → build loop, all in a single context window. Each phase writes into `/context/[nnn]-{feature}/`."\[1\]

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

`design-breakdown` matters a lot here. It already turns a TDD into "epics and user stories with acceptance criteria, dependencies, and explicit out-of-scope items", which is exactly the input `ship-fleet` needs to decompose an epic.\[1\] Reuse it; don't rebuild it.

### 2. Branch recommendation

Decide with this rule:

- **Stack on the migration branch** if it already has (a) a `.claude-plugin/plugin.json` that passes `claude plugin validate`, and (b) `explore/research/planner/execute` converted to `skills/<name>/SKILL.md`. Do it literally as a stack: `gh stack init --base main <migration-branch>` adopts the existing branch as layer 1, then `gh stack add ship-skills` puts this work on top. The plugin migration can then be reviewed and merged first, and your work rebases automatically.
- **Otherwise start from main.** Add a minimal plugin layer as the first PR of your own stack, then build on top.
  - A minimal layer is `.claude-plugin/plugin.json` plus `marketplace.json` with `source: "./"`.\[2\]
  - It costs almost nothing, because Claude Code docs say "Custom commands have been merged into skills". A file at `.claude/commands/deploy.md` and one at `.claude/skills/deploy/SKILL.md` "both create `/deploy` and work the same way", and existing `commands/` files keep working.\[3\]
  - The migration is therefore not a prerequisite. Only the new building blocks *must* be skills, because they need supporting files, `disable-model-invocation`, and preloading.

Either way, the plugin namespace changes command names: plugin skills are invoked as `/plugin-name:skill-name`, so `/execute` becomes `/spicyclaude:execute`.\[3\]\[4\] Note this in the README.

### 3. Platform constraints that shape the design (official docs)

| Capability | What the docs say | Design consequence |
|---|---|---|
| Nested subagents | "By default, a subagent can spawn subagents of its own, up to three layers below the main conversation. At the depth limit, Claude Code withholds the Agent tool." Depth is set by `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`.\[5\] | Main → story-runner (L1) → phase agents (L2) → review lenses (L3) fits exactly. Set the env var explicitly; the default changed several times in mid-2026 (official Claude Code changelog, v2.1.217 and v2.1.219). |
| Spawn restriction | In a subagent definition, listing `Agent` in `tools` allows spawning, but "any type list inside the parentheses is ignored".\[5\] | You can't hard-restrict which agents a story-runner spawns. Constrain it by prompt, and audit with `SubagentStart` hooks. |
| Questions | `AskUserQuestion` is in the list of tools removed from every subagent.\[5\] | Only the main session can ask. Subagents must return questions as data. |
| Workflows | `Workflow` is also removed from every subagent.\[5\] | A subagent can't launch a dynamic workflow, so workflows could only ever be top-level. |
| Skills in subagents | The `skills` field preloads the full content. Subagents "can still invoke unlisted project, user, and plugin skills through the Skill tool".\[5\] Skills with `disable-model-invocation: true` can't be preloaded.\[3\]\[5\] | Keep the user-facing `ship-it` as `disable-model-invocation: true`. Put the reusable procedure in a separate preloadable skill (`ship-pipeline`). |
| Skill in a subagent | `context: fork` runs the skill in a new subagent of the `agent` type.\[3\] | Don't fork the orchestrators: they would lose `AskUserQuestion`. Fork is fine for leaf skills such as `research`. |
| Worktrees | `isolation: worktree` uses a temporary worktree "branched by default from your default branch rather than the parent session's HEAD", auto-cleaned if there are no changes.\[5\] | That breaks stacking. Story layers must be built on the layer below, so `ship-fleet` creates its own worktree and runs layers sequentially in it. Use `isolation: worktree` only for independent `ship-it` runs. |
| Models / effort | Order: per-invocation `model` → frontmatter `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → main model.\[6\] `effort` is set per agent.\[5\]\[7\] | Use opus for planner and reviewers, sonnet for executor and fixer, haiku for status and gh plumbing. Spend effort where judgment matters. |
| Background | Subagents spawned from the main conversation start in the background. Background subagents surface permission prompts in the main session.\[6\]\[8\] Background subagents keep only a reduced built-in tool set (Read, Grep, Glob, Bash, Edit, Write, Skill, SendMessage, …).\[5\] | Pre-approve `Bash(gh stack *)`, `Bash(git *)` and your test commands in settings, or long runs will stall on prompts. |
| Hooks | Frontmatter `Stop` hooks in an agent are converted to `SubagentStop`. Exit code 2 sends Claude back to work.\[5\]\[9\]\[10\] Plugin subagents ignore `hooks`, `mcpServers`, and `permissionMode`.\[5\] | Validate findings JSON with plugin-level `hooks/hooks.json` (`SubagentStop` matcher = agent type), not agent frontmatter. |
| Context | Each subagent has its own context window and returns a summary.\[11\] `maxTurns` and `autoCompactWindow` are available.\[7\] Agent descriptions over 15,000 tokens combined trigger a warning.\[5\] | Keep agent descriptions short, put the detail in bodies, and have the orchestrator keep only status lines. |

### 4. Dynamic workflows vs. composable skills

The official docs define a dynamic workflow as "a JavaScript script that orchestrates many subagents at once", which "a runtime executes … in the background". The key difference from skills is "who holds the plan": with skills, Claude decides turn by turn and "intermediate results live" in Claude's context window; with workflows, "the script" decides and intermediate results live in script variables.\[12\]

- **What workflows add:**
  - Scale: up to 16 concurrent agents by default and 1,000 agents per run.\[12\]
  - Structured output: an `agent()` `schema` with retries.\[12\]
  - Resumability within the session.\[12\]
  - Shareable `.claude/workflows/*.js`, which plugins can ship in a `workflows/` directory.\[12\]
- **Why they're the wrong core for this design:**
  - **"No mid-run user input"** — a run pauses only for permission prompts and usage limits, and the docs say "For sign-off between stages, run each stage as its own workflow".\[12\] That directly conflicts with `raise` mode and with any checkpoint batching.
  - The `Workflow` tool is unavailable to subagents.\[5\]
  - Scripts can't touch the filesystem or shell directly; agents do that.\[12\] Your `gh stack` choreography would end up as prompts anyway.
  - Workflows "consume meaningfully more usage", with a `Large workflow` warning above 25 agents or 1.5M projected tokens.\[12\]\[13\]
- **What skills give up:** determinism. Claude may skip a step. Recover most of it with (a) a gate script that computes the loop decision from JSON, and (b) `SubagentStop` hooks that reject malformed reviewer output. The best-practices docs make the same point: for things that must always happen, use deterministic controls (hooks), not prose.\[9\]

**Conclusion:** composable skills, nested subagents and two orchestrator skills fully meet the requirements, and they support interactive escalation, which workflows can't. Keep one seam open. The review loop is defined by a JSON contract, so a future `review-sweep.js` workflow could replace the in-skill loop for very large fan-outs (e.g. 10+ parallel review lenses on a big PR) without changing any agent.

### 5. `gh stack` status as of late 2026

- **What it is:** an official GitHub CLI **extension**, `gh extension install github/gh-stack`, not built into `gh`. GitHub also ships an agent skill: `gh skill install github/gh-stack`.\[14\]\[15\]
- **Release dates:** GitHub's changelog announced the public preview on July 30, 2026. Its "Stacked pull requests generally available" entry (October 6, 2026) says stacked PRs "are available on all github.com plans and will be included in an upcoming GitHub Enterprise Server release", and that "the gh stack extension for GitHub CLI now supports Git worktrees."
- **Version requirements (conflicting in GitHub's own docs):** the CLI reference says `gh` 2.0+ and Git 2.36+; the quickstart says `gh` 2.90.0+ and Git 2.20+.\[14\]\[15\]\[16\] Require **gh ≥ 2.90 and Git ≥ 2.36** to satisfy both.

**Agent-relevant commands and flags (from the CLI reference):**

| Command | Use in ship-fleet | Gotchas |
|---|---|---|
| `gh stack init --base <trunk> b1 [b2 …]` | create or adopt the stack | enables `git rerere` automatically\[16\] |
| `gh stack add <branch>` | new layer per story | "You must run this command while on the topmost branch"\[16\] |
| `gh stack view --json` | status reporting | `--json`/`--short` work in non-interactive terminals\[16\] |
| `gh stack submit --auto [--open]` | push and create/update PRs, link the stack | `--auto` creates **drafts** unless `--open`; non-interactive terminals skip the editor\[16\] |
| `gh stack rebase [--upstack/--downstack/--continue/--abort]` | cascade after lower-layer changes | switches to `--onto` automatically after a merged PR; pauses on conflicts\[16\]\[17\]\[18\] |
| `gh stack push` | push all active branches | `--force-with-lease` per branch; **not atomic**\[16\]\[19\] |
| `gh stack sync [--prune]` | after merges / trunk moves | "safe to run in automation"; in a non-interactive terminal a divergence **aborts and exits successfully**, so check state afterwards\[16\] |
| `gh stack checkout <n|pr|branch> --print-path` | locate worktrees | prints only a raw path; never prompts\[16\] |
| `gh stack merge <pr> --yes --squash` | optional final landing | all-or-nothing; "You cannot bypass merge requirements"\[16\] |
| `gh stack modify` | **don't use from agents** | interactive TUI; use `unstack` + `init` to restructure instead\[16\] |
| `gh stack link` | adopt PRs made elsewhere | additive only\[16\] |

**Other limitations:**
- All branches must be in the same repository.\[20\]
- Server-side rebases from the website are not signed, so rebase via the CLI if you require signed commits.\[17\]\[21\]
- Exit code 9 means stacked PRs aren't enabled for the repository.\[16\] `ship-fleet` should preflight for this and fall back to plain branch-on-branch PRs with `git rebase --update-refs`.

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
 │   ├─ explorer (L2, read-only, sonnet)         → research-[nnn].md
 │   ├─ planner (L2, opus)                        → plan-[nnn].md
 │   ├─ REVIEW LOOP: plan-reviewer (L2, opus) ⇄ plan-fixer (L2)   → plan-review-r{n}.json
 │   ├─ returns NEEDS_INPUT ⇢ L0 asks ⇢ L0 resumes L1   (raise mode only)
 │   ├─ executor (L2, sonnet; TDD + python skills)  → commits, progress-[nnn].md
 │   └─ REVIEW LOOP: code-reviewer (L2, opus) ─┬─ L3 lens agents (correctness / security / tests / design)
 │                                             └─ ⇄ code-fixer (L2) → code-review-r{n}.json
 ▼
L0: gate checks (tests green, review gate PASS) → gh stack submit --auto → update STATUS.md → next story
```

`ship-it` is the same picture without L1: the main session runs `ship-pipeline` directly, so phase agents sit at L1 and review lenses at L2. That leaves a spare depth level.

**Why sequential stories:** each layer must compile on the layer below.\[22\] Run the *explorer* for story N+1 in parallel with the *executor* for story N; it's read-only and cheap. Don't plan N+1 until N's code review passes, or the plan goes stale. Stories in the DAG with no dependency on each other can go in **separate stacks**, each in its own worktree, and run in parallel.

### 7. Reuse vs. new

| Today | Becomes | Notes |
|---|---|---|
| `/explore` | stays a user skill (conversational); plus a new **`explorer` agent** for pipelines | the interactive pass can't run unattended |
| `/research` | skill `research` (`context: fork`, `agent: explorer`) + reused by explorer | keeps the `research-[nnn].md` contract |
| `/planner` | skill `planner` + **`planner` agent** (preloads `planner` skill body via a `planner-method` reference skill) | keep the AC trace table and footgun checklist |
| `/review:my-developer-plan` | **`plan-reviewer` agent** emitting the findings contract | add severity labels |
| `/review:pragmatic-code-review` (/ `review-heavy` if on a branch) | **`code-reviewer` agent** + optional L3 lens agents | "real issues, not nitpicks" maps onto the severity floor |
| `/execute` | **`executor` agent** (preloads `test-driven-development`) | keep commit-per-parent-task and `progress-[nnn].md` |
| `iterator` agent | **`fixer` agent** (plan-fix and code-fix modes) | applies findings only; no scope creep |
| `design-breakdown` | used by `ship-fleet` for decomposition | add a `stories.json` emitter |
| SPICE | leave as-is; `ship-it` is its unattended sibling | link them in the README |
| **New** | `ship-it`, `ship-fleet`, `ship-pipeline`, `review-loop`, `question-policy`, `stack-ops`, `story-runner`, `fleet-decomposer`, `restacker` | |

### 8. Proposed file tree

```
spicyclaude/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json            # one entry, source "./"
├── skills/
│   ├── ship-it/SKILL.md                     # user-invoked orchestrator (single story)
│   ├── ship-fleet/
│   │   ├── SKILL.md                         # user-invoked orchestrator (epic → stack)
│   │   └── references/stack-playbook.md     # gh stack choreography, recovery
│   ├── ship-pipeline/
│   │   ├── SKILL.md                         # user-invocable: false; the per-story procedure
│   │   └── references/artifacts.md          # /context layout + file contracts
│   ├── review-loop/
│   │   ├── SKILL.md                         # user-invocable: false; algorithm + contract
│   │   └── references/findings.schema.json
│   ├── question-policy/SKILL.md             # user-invocable: false; modes + question contract
│   ├── stack-ops/SKILL.md                   # user-invocable: false; wraps gh stack safely
│   ├── explore/ research/ planner/ execute/ # migrated commands (or keep commands/*.md)
│   └── design-doc/ design-breakdown/ feasibility-study/ spice/ test-driven-development/ python-development/
├── agents/
│   ├── ship/story-runner.md
│   ├── ship/fleet-decomposer.md
│   ├── ship/restacker.md
│   ├── phase/explorer.md
│   ├── phase/planner.md
│   ├── phase/plan-reviewer.md
│   ├── phase/executor.md
│   ├── phase/code-reviewer.md
│   ├── phase/fixer.md
│   └── lens/{correctness,security,tests,design}-lens.md
├── hooks/hooks.json                         # SubagentStop validators, AskUserQuestion auto-answer (opt-in)
├── scripts/
│   ├── ship-config.py                       # resolves config precedence → JSON
│   ├── review-gate.py                       # findings JSON → CONTINUE|PASS|EXHAUSTED|STALLED
│   ├── validate-findings.py                 # SubagentStop hook: schema check
│   └── auto-answer.py                       # PreToolUse hook for legacy AskUserQuestion
├── commands/ …                              # legacy, still works
└── CLAUDE.md  README.md  settings.json  statusline.sh
```

Note that plugin `agents/` subfolders become part of the scoped identifier: `agents/phase/planner.md` registers as `spicyclaude:phase:planner`.\[5\]\[23\] Reference agents by that full name in skill bodies.

### 9. Draft definitions

**`.claude-plugin/plugin.json`** (outline): `name: "spicyclaude"`, `description`, `version`, `author`, `repository`, and `userConfig` entries for `maxReviewRounds` (default 3), `minReviewSeverity` (default `high`) and `questionMode` (default `auto`). Plugin `userConfig` is the documented way for Claude Code to prompt users for plugin settings.\[24\]

**`skills/ship-it/SKILL.md`**

```markdown
---
name: ship-it
description: Implement one well-defined story end to end (explore → plan → plan review loop → execute → code review loop → PR). Use when the user says ship it / implement this story.
argument-hint: "<story-file|issue#|text> [--max-review-rounds=N] [--min-severity=critical|high|medium|low] [--questions=auto|raise|batch] [--pr|--no-pr]"
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(gh *) Bash(python3 *) Read Write
---
## Config
!`python3 scripts/ship-config.py`
Apply overrides parsed from: $ARGUMENTS (arguments beat the resolved config above).

## Procedure
1. Create /context/[nnn]-{slug}/ and write story.md (story text + ACs). Write ship-state.json {phase, round, status}.
2. Follow the ship-pipeline skill exactly. Spawn spicyclaude:phase:* agents; never do phase work yourself.
3. You are the ONLY agent that may call AskUserQuestion. When an agent returns status NEEDS_INPUT, apply the question-policy skill; in raise/batch mode ask (max 4 questions per call), write answers to answers.json, then resume that agent.
4. Finish only when: tests green (show command + output), plan gate PASS, code gate PASS or EXHAUSTED with escalation recorded.
5. If --pr: push and `gh pr create` with body = summary + AC trace + "Decisions made autonomously" (from decisions.md) + unresolved findings below threshold.
6. Reply with ≤15 lines: status, PR link, rounds used per reviewer, open decisions.
```

**`skills/ship-pipeline/SKILL.md`** (`user-invocable: false`, preloaded by story-runner). Body outline:

- **Phase table:** agent, input files, output file, model.
- **Rules:**
  - Each agent gets *paths*, not pasted content.
  - Each agent returns the return envelope (below).
  - Run `review-loop` for `plan` (reviewer `plan-reviewer`, fixer `fixer --mode=plan`) and for `code` (reviewer `code-reviewer`, fixer `fixer --mode=code`).
  - Run the executor only after the plan gate is `PASS`/`EXHAUSTED`.
  - Explorer and reviewers are read-only.
  - Keep the orchestrator context to one line per phase.

**Return envelope** (every phase agent ends with this fenced JSON):

```json
{"status":"DONE|NEEDS_INPUT|FAILED","artifact":"/context/012-auth/plan-012.md",
 "summary":"≤5 lines","questions":[/* question contract, see §11 */],
 "decisions":[{"id":"D3","question":"…","chosen":"B","why":"…","reversible":true}]}
```

**`agents/ship/story-runner.md`**

```markdown
---
name: story-runner
description: Runs the full ship pipeline for ONE story inside the current worktree/branch and returns a status envelope.
tools: Agent, Read, Write, Edit, Bash, Grep, Glob, Skill
skills: [ship-pipeline, review-loop, question-policy]
model: sonnet
effort: medium
maxTurns: 200
---
You orchestrate; you do not implement. Spawn spicyclaude:phase:* agents per ship-pipeline.
You cannot ask the user anything. If an agent returns NEEDS_INPUT and question mode is raise/batch,
stop and return NEEDS_INPUT with the merged questions; the caller will resume you with answers.json.
Never switch branches or run gh stack commands; the caller owns the stack.
```

**`agents/phase/plan-reviewer.md`** (the same pattern applies to `code-reviewer`)

```markdown
---
name: plan-reviewer
description: Independently reviews plan-[nnn].md against story ACs and the codebase; emits severity-labelled findings JSON.
tools: Read, Grep, Glob, Bash, Write
model: opus
effort: high
omitClaudeMd: false
---
Review ONLY for issues that would make the implementation wrong, unsafe, untestable, or miss an AC.
Skip style. Label every finding with the severity rubric in review-loop. Do not invent issues to fill a quota;
"no findings" is a valid, expected outcome. Write /context/.../plan-review-r{round}.json per findings.schema.json.
Re-reviews: first verify each prior finding id is resolved, then look for regressions introduced by the fixes.
```

**`agents/phase/executor.md`**: `tools: Read, Edit, Write, Bash, Grep, Glob, Skill`; `skills: [test-driven-development, python-development]`; `model: sonnet`. The body keeps `/execute`'s rules: commit per parent task, full suite before each commit, and update `progress-[nnn].md`. It must emit the return envelope. Questions found mid-execution are handled per `question-policy`: never block in `auto`.

**`agents/phase/fixer.md`**: applies only the findings it is given (by id), records `resolution` per id (`fixed|rejected-with-reason`), and never broadens scope. Its two modes write to the plan file or to code plus commits.

**`agents/ship/restacker.md`**: `model: sonnet`, tools `Bash, Read, Edit, Grep`. It resolves `gh stack rebase` conflicts in the named worktree, runs that layer's tests, then calls `gh stack rebase --continue`. It aborts with `gh stack rebase --abort` after two failed attempts and returns FAILED.\[17\]

**`skills/ship-fleet/SKILL.md`**

```markdown
---
name: ship-fleet
description: Implement an entire epic as a stack of PRs using gh stack; one story per layer.
argument-hint: "<epic.md|TDD path|issue#> [--trunk=main] [--max-review-rounds=N] [--min-severity=…] [--questions=…] [--open] [--resume]"
disable-model-invocation: true
allowed-tools: Bash(gh *) Bash(git *) Bash(python3 *) Read Write
---
## Preflight
!`gh --version | head -1; git --version; gh extension list | grep -i stack || echo "gh-stack MISSING"`
!`python3 scripts/ship-config.py`
Stop with install instructions if gh-stack is missing. If any gh stack call exits 9, fall back to plain stacked branches (see references/stack-playbook.md).

## 1 Decompose
Use design-breakdown (or spawn spicyclaude:ship:fleet-decomposer) → /context/[nnn]-{epic}/stories.json:
[{id, title, acs[], depends_on[], est_size, layer_hint}]. Rules: lower layers hold shared types/schema;
each layer must build and pass tests alone; split any story > ~400 changed lines.
Topologically sort. Independent chains → separate stacks.
CHECKPOINT A: in raise/batch mode, ask decomposition questions (≤4 per AskUserQuestion call).

## 2 Prepare isolation
Create ONE fleet worktree per stack (git worktree add ../.ship/<epic> -b <first-branch> <trunk>), cd into it,
`gh stack init --base <trunk> <first-branch>`. Never use agent isolation: worktree for stacked layers.

## 3 Per story (sequential)
For story k>1: ensure on top branch, `gh stack add <epic>/<k>-<slug>`.
Spawn spicyclaude:ship:story-runner (foreground) with story id, paths, resolved config.
On NEEDS_INPUT: ask (raise/batch) → write answers.json → resume the same runner.
On DONE: verify gate files, then `gh stack submit --auto` (+ --open if requested). Append to fleet.json.
On FAILED: mark blocked; stop the chain above it; continue other independent stacks.

## 4 Restack when a lower layer changes
Triggers: review feedback on PR j, trunk moved, or a fix in story j discovered while building k.
`gh stack checkout <branch-j>` → spawn story-runner in fix mode (review loop only) → commit →
`gh stack rebase --upstack` → on conflict spawn restacker → rerun tests on every upper layer →
`gh stack push`. After merges: `gh stack sync --prune`, then re-check `gh stack view --json`
(non-interactive divergence aborts silently).

## 5 Report
Write STATUS.md from `gh stack view --json` + fleet.json: per layer PR#, CI, review rounds used,
gate result, open decisions, blocked reasons. Reply with the table only.
```

**`skills/stack-ops/SKILL.md`** (`user-invocable: false`) captures the gotchas so agents never hit interactive paths:

- Always `--auto` on `submit`.
- Never `modify` or `switch`.
- `add` only from the top branch.
- Check `push` results per branch, since it is non-atomic.
- Treat a `sync` exit of 0 as "verify state", not "success".
- Use `checkout --print-path` to locate worktrees.

### 10. Review-loop specification

**Severity taxonomy** (ordered):

| Level | Meaning | Examples |
|---|---|---|
| `critical` | will cause data loss, security breach, outage, or a fundamentally wrong design | auth bypass, destructive migration without backup, plan solves the wrong problem |
| `high` | incorrect behavior, unmet AC, missing test for a core path, likely regression | off-by-one in billing, AC #3 not traced, race condition |
| `medium` | maintainability or robustness risk that won't break ACs now | leaky abstraction, weak error handling on rare path |
| `low` | minor improvement | naming, small duplication |
| `nit` | style/preference | formatting — reviewers should mostly skip these |

**Findings contract** (`findings.schema.json`):

```json
{"reviewer":"code-reviewer","target":"plan-012.md|<git range>","round":2,
 "verdict":"PASS|CHANGES_REQUESTED",
 "prior_findings":[{"id":"F2","status":"resolved|unresolved|regressed"}],
 "findings":[{"id":"F5","severity":"high","category":"correctness|security|tests|design|ac-coverage",
   "location":"src/auth/refresh.py:88","evidence":"…","recommendation":"…",
   "fingerprint":"sha1(category+location+normalized claim)","confidence":0.8}]}
```

**Algorithm** (implemented once in `review-gate.py`; the skill only follows its verdict):

```
cfg ← resolve(reviewer)                      # max_rounds=3, min_severity=high by default
for r in 1..cfg.max_rounds:
    F ← run reviewer(round=r, prior=F_prev)   # writes *-review-r{r}.json; SubagentStop hook validates schema
    blocking ← {f ∈ F.findings ∪ unresolved(F.prior) : sev(f) ≥ cfg.min_severity}
    if blocking = ∅: return PASS(r)                       # early stop: nothing at/above threshold
    if r = cfg.max_rounds: return EXHAUSTED(blocking)      # escalate per question policy
    if repeated(blocking.fingerprints, F_prev) twice: return STALLED(blocking)  # fixer/reviewer disagree
    run fixer(findings = {f : sev(f) ≥ cfg.fix_floor})    # fix_floor defaults to "medium"; fixes may include lower items
    F_prev ← F
```

Semantics:

- **When a new round happens:** only findings at or above `min_severity` trigger another round, which is your "minimum severity that triggers another review round after fixes are folded in".
- **Lower-severity findings** may still be fixed (`fix_floor`), but they never cause a re-review on their own. They are listed in the PR body.
- **`STALLED`** stops an "argue forever" loop when the fixer rejects a finding and the reviewer re-raises it.
- **`EXHAUSTED`:**
  - In `auto` mode it proceeds, provided no `critical` finding remains; a remaining `critical` *always* blocks the PR and marks the story blocked.
  - In `raise` mode it asks the user.
- **Prompting guidance:** reviewers are told explicitly that "no findings" is valid. The official best-practices page warns that "A reviewer that's asked to find problems will always find *something*. If you fix every finding, you end up with extra abstraction layers and tests for cases that can't happen".\[9\] The severity floor is the structural fix for that.

**Override mechanism** (highest precedence first; `ship-config.py` resolves and prints JSON, injected via `!` dynamic context):

1. **Skill arguments:** `--max-review-rounds=5 --min-severity=medium`, plus per-reviewer forms such as `--plan-rounds=2 --code-min-severity=critical`.
2. **Environment variables**, which you can set in the `env` block of settings: `SPICY_MAX_REVIEW_ROUNDS`, `SPICY_REVIEW_MIN_SEVERITY`, `SPICY_QUESTION_MODE`, and per-reviewer variants `SPICY_PLAN_MAX_ROUNDS`, `SPICY_CODE_MIN_SEVERITY`.
3. **Project file:** `.claude/spicyclaude.json`, for example `{"review":{"default":{"max_rounds":3,"min_severity":"high","fix_floor":"medium"},"plan":{"max_rounds":2}},"questions":{"mode":"auto","escalate":["irreversible"]}}`.
4. **Plugin `userConfig`** values.
5. **Built-in defaults:** 3 rounds and `high`.

Frontmatter is not a good override channel: it's static per file, and plugin agents ignore several fields. Use it only for defaults that never change, such as model and effort.

### 11. Open-questions policy

**Hard constraint:** subagents can't call `AskUserQuestion`. The Agent SDK docs also state that `AskUserQuestion` "is not currently available in subagents spawned via the Agent tool", and that each call supports 1–4 questions with 2–4 options.\[25\] So every design is ultimately "agents emit questions as data; the main session decides whether to ask".

**Question contract** (inside the return envelope):

```json
{"id":"Q4","phase":"planner","question":"Store refresh tokens hashed or encrypted?",
 "options":[{"key":"A","label":"bcrypt-hash","tradeoff":"…"},{"key":"B","label":"AES-GCM","tradeoff":"…"}],
 "recommended":"A","confidence":0.7,"reversibility":"reversible|costly|irreversible",
 "impact":"local|cross-story|external","default_if_unanswered":"A"}
```

**Modes compared:**

| Mode | How it works | Pros | Cons |
|---|---|---|---|
| **`auto` (default)** | agent picks `recommended`, appends to `decisions.md`, continues | zero interruptions; fully unattended | silent wrong turns compound across stories |
| **`raise`** | agent returns NEEDS_INPUT; story-runner bubbles up; main asks immediately; runner resumed | maximal control | blocks the pipeline per question; unusable headless |
| **`batch` (checkpoint)** | agents proceed on recommended options *provisionally*; questions batched at fixed checkpoints (after decomposition, after each plan gate) and asked ≤4 at a time; answers that differ trigger a re-plan | few interruptions at natural seams | re-plan cost when you override |
| **Threshold escalation** | auto-decide unless `confidence < τ` or `reversibility = irreversible` or `impact = external` | interruptions only where they matter | model-reported confidence is poorly calibrated, so use it only as a secondary signal |
| **Async decision log** | `decisions.md` copied into a PR-body "Decisions made autonomously" section; reviewers object in PR comments; `ship-fleet` fix mode picks objections up | fits review culture; no blocking | decisions are revisited after the code exists |
| **Hook auto-answer** | a `PreToolUse` hook on `AskUserQuestion` returns `updatedInput` with the recommended option and `permissionDecision: "allow"`; Claude Code supports this "enabling headless integrations that collect answers via their own UI"\[26\] | deterministic auto mode for *legacy* commands that call `AskUserQuestion` in the main session, with no prompt edits | only works where the tool exists (main session); needs a way to know which option is "recommended" (convention: first option labelled "(Recommended)") |

**Recommendation:**
- Ship `auto` as the default, exactly as you asked, and always produce the decision log in the PR body (async review costs nothing).
- Add one guard on by default and easy to disable: `escalate: ["irreversible"]`.
  - In `auto`, irreversible or external-impact questions are queued for the next checkpoint instead of being auto-answered.
  - In headless runs (`claude -p`), where nothing can be asked, queued questions mark the story `blocked` instead of guessing.
- Use `batch` rather than `raise` as the interactive mode for `ship-fleet`; `raise` stays available for `ship-it`.
- Update existing commands to replace "use AskUserQuestion" with "apply the question-policy skill". The hook covers anything not yet migrated.

### 12. Artifacts, context management and long epics

- **Per-story layout:** `/context/[nnn]-{slug}/` holds `story.md`, `research-[nnn].md`, `plan-[nnn].md`, `plan-review-r{n}.json`, `progress-[nnn].md`, `code-review-r{n}.json`, `decisions.md`, `questions.json`, `answers.json`, and `ship-state.json`.
- **Per-epic layout:** `/context/[nnn]-{epic}/` holds `stories.json`, `fleet.json` (story → branch → PR → status) and `STATUS.md`.
- **Pass paths, not content.** The orchestrator's context then grows by about one envelope per phase, not by the artifacts.
- **Resumability:** `ship-fleet --resume` reads `fleet.json` and `gh stack view --json` and continues from the first non-DONE story. That makes multi-day epics survive session restarts and compaction. The docs note auto-compaction happens automatically, but a state file is the only reliable memory.
- **Budgets:**
  - Set `maxTurns` on every agent.
  - Set `autoCompactWindow` on the executor.
  - For unattended runs use `claude -p "/spicyclaude:ship-fleet …" --max-budget-usd <n>`. The best-practices page lists `--max-turns` and `--max-budget-usd` with `-p` as the deterministic spend controls.\[9\]
- **Cost:** In "How we built our multi-agent research system" (June 2025), Anthropic reported that "a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval", and that "multi-agent systems use about 15× more tokens than chats". Route mechanical phases to cheaper models.
- **Deterministic guards in `hooks/hooks.json`:**
  - `SubagentStop` with matcher `spicyclaude:phase:plan-reviewer|spicyclaude:phase:code-reviewer` runs `validate-findings.py`. Exit 2 with the schema error sends the reviewer back to fix its JSON.\[10\]\[27\]
  - The executor's tests can be enforced the same way.
  - The stop-block cap is 8 consecutive blocks; `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` raises it.\[9\]

## Recommendations

1. **Spend 5 minutes on verification first:** list branches and PRs, and grep for `AskUserQuestion`. Then apply the §2 rule: stack on the migration branch if it has a validating `plugin.json` and the four core skills, otherwise start from main.
2. **Build in this order, one PR per layer (dogfood `gh stack`):**
   - (1) plugin manifest + `review-loop` + `question-policy` + scripts;
   - (2) phase agents from existing commands;
   - (3) `ship-pipeline` + `ship-it`;
   - (4) `stack-ops` + `ship-fleet`;
   - (5) hooks.
3. **Pin the platform:**
   - Document a minimum Claude Code version and set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=3` explicitly in project settings `env`. Plugin `settings.json` only supports the `agent` and `subagentStatusLine` keys, so it can't carry env vars.\[23\]
   - Require gh ≥ 2.90 and Git ≥ 2.36.
4. **Pre-approve tools for unattended runs:** `Bash(gh stack *)`, `Bash(git *)` and test commands in allow rules, plus `ask` on `Bash(gh stack merge *)`. Never let agents merge by default.
5. **Don't adopt dynamic workflows for the core.** Revisit them only if a single PR review needs >10 parallel lenses. The findings contract makes that a drop-in swap.

## Caveats

- **Repo internals unverified:** branches, PRs, command bodies and `hooks/` contents are inferred from the README only. `review-heavy` was not visible on main.
- **Moving defaults:**
  - Nested-subagent defaults changed in July 2026, per the official Claude Code changelog. v2.1.217 (July 21) "Changed subagents to no longer spawn nested subagents by default; set CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH to allow deeper nesting." v2.1.219 (July 24) says "Subagents can now spawn nested subagents up to depth 3 by default (was 1)." anthropics/claude-code issue #80083 ("[DOCS] Nested-subagent docs still describe a fixed depth and omit the default-disabled behavior") flagged that the sub-agents page lagged those changes. Set the depth env var explicitly rather than relying on defaults.
  - Concurrency caps also exist: the v2.1.217 changelog "Added a cap on concurrently-running subagents (default 20...)", configurable via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`.
- **gh-stack docs conflict on minimum versions.** GA timing comes from GitHub's October 6, 2026 changelog entry. `sync` aborts silently on divergence in non-interactive terminals.
- **Skill orchestration is model-directed, not guaranteed.** Hooks and the gate script cover the critical invariants, but an orchestrator can still skip a step. Spot-check `ship-state.json` on early runs.
- **The confidence field in questions is self-reported** and poorly calibrated. Treat reversibility and impact as the primary escalation signals.

## Sources

1. [GitHub - d-mariano/spicyclaude: Spicy Claude](https://github.com/d-mariano/spicyclaude)
2. [Publish and distribute a plugin - Claude Code Docs](https://code.claude.com/docs/en/plugins/publish)
3. [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
4. [Plugins in the SDK - Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/plugins)
5. [Create custom subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
6. [Subagents in the SDK - Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/subagents)
7. [Agent SDK reference - TypeScript - Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/typescript)
8. [Week 27 · June 29](https://code.claude.com/docs/en/whats-new/2026-w27)
9. <https://code.claude.com/docs/en/best-practices>
10. [Hooks reference - Claude Code Docs](https://code.claude.com/docs/en/hooks)
11. [Sub-Agents in Claude Code: The Subagent Orchestration Behind the Response Awareness Methodology](https://responseawareness.substack.com/p/sub-agents-in-claude-code-the-subagent)
12. <https://code.claude.com/docs/en/workflows>
13. [Introducing dynamic workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)
14. [Quickstart for stacked pull requests - GitHub Docs](https://docs.github.com/en/pull-requests/get-started/stacked-prs-quickstart)
15. [Stacked Pull Requests on GitHub: A Practical Guide to the New Workflow](https://betterstack.com/community/guides/linux/github-stacked/)
16. [Stacked pull requests CLI commands - GitHub Docs](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands)
17. [Managing stacked pull requests - GitHub Docs](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests)
18. [GitHub - github/gh-stack: GitHub Stacked PRs · GitHub](https://github.com/github/gh-stack)
19. [Reviewing stacked pull requests - GitHub Docs](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-stacked-pull-requests)
20. [About stacked pull requests - GitHub Docs](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs)
21. [docs/content/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests.md at main · github/docs · GitHub](https://github.com/github/docs/blob/main/content/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests.md)
22. [GitHub stacked PRs: how to use gh stack or plain Git](https://www.cubic.dev/blog/stacked-pull-requests)
23. [Plugins 参考 - Claude Code Docs](https://code.claude.com/docs/zh-CN/plugins-reference)
24. [Plugin manifest reference - Claude Code Docs](https://code.claude.com/docs/en/plugins/manifest-reference)
25. [Handle approvals and user input - Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/user-input)
26. [Claude Code changelog - Claude Code Docs](https://code.claude.com/docs/en/changelog)
27. [Automate workflows with hooks - Claude Code Docs](https://code.claude.com/docs/en/hooks-guide?8adb0641_page=4&cc61befa_page=2&d7430fcd_page=5&r=0)
