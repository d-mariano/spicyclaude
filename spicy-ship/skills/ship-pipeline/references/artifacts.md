# Story artifacts

Everything a story produces lives in `/context/[nnn]-{slug}/`. `nnn` is the next unused
three-digit number under `/context/`; `slug` is kebab-case from the story title, at most five words.

| File | Written by | Purpose |
|---|---|---|
| `story.md` | orchestrator | the story text and acceptance criteria as given |
| `ship-state.json` | orchestrator | phase, round, status, gates; the resume point |
| `research-[nnn].md` | explorer | findings, usage examples, Open Questions table |
| `plan-[nnn].md` | planner, then fixer in plan mode | the plan; its `## Tasks` checklist is the execution protocol |
| `plan-review-r{n}.json` | plan-reviewer | round `n` findings, per the review-loop contract |
| `plan-fixes-r{n}.json` | fixer | round `n` resolutions, one per handed finding |
| `progress-[nnn].md` | executor | task, commit, test command, result |
| `code-review-context-r{n}.md` | code-reviewer | shared context the lenses read |
| `code-review-r{n}.json` | code-reviewer | round `n` findings |
| `code-fixes-r{n}.json` | fixer | round `n` resolutions |
| `decisions.md` | every agent, append-only | one line per autonomous decision; copied into the PR body |
| `answers.json` | orchestrator | the user's answers, keyed by question id |

`nnn` inside file names matches the folder. Rounds start at 1. Nothing here is ever deleted or
rewritten except `ship-state.json` and the plan.
