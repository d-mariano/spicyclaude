# Story artifacts

Everything a story produces lives in `/context/[nnn]-{slug}/`. `nnn` is the next unused
three-digit number under `/context/`; `slug` is kebab-case from the story title, at most five words.

| File | Written by | Purpose |
|---|---|---|
| `story.md` | orchestrator | the story text and acceptance criteria as given |
| `ship-state.json` | orchestrator | phase, round, status, gates, base_sha; the resume point |
| `ship-config.json` | orchestrator | the config resolved once at the start; every agent and gate reads this, never a fresh resolution |
| `questions.json` | orchestrator | the phase and questions array from the last NEEDS_INPUT; replaced each time |
| `research-[nnn].md` | explorer | findings, usage examples, Open Questions table |
| `plan-[nnn].md` | planner, then fixer in plan mode | the plan; its `## Tasks` checklist is the execution protocol |
| `plan-review-r{n}.json` | plan-reviewer | round `n` findings, per the review-loop contract |
| `plan-fixes-r{n}.json` | fixer | round `n` resolutions, one per handed finding |
| `progress-[nnn].md` | executor | task, commit, test command, result |
| `code-review-context-r{n}.md` | code-reviewer | shared context the lenses read |
| `code-review-r{n}.json` | code-reviewer | round `n` findings |
| `code-fixes-r{n}.json` | fixer | round `n` resolutions |
| `decisions.md` | every agent, append-only | one line per autonomous decision; copied into the PR body |
| `answers.json` | orchestrator | the user's answers, keyed by `<phase>:<id>`, accumulated across the story |

`nnn` inside file names matches the folder. Rounds start at 1. Research and every review and
fixes JSON are write-once. The plan and `progress-[nnn].md` are updated in place, `decisions.md`
and `answers.json` only grow, and `ship-state.json` and `questions.json` are replaced. Nothing is
deleted.
