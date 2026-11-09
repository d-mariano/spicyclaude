---
name: question-policy
description: How ship pipelines handle open questions when the agent doing the work cannot ask the user. Defines the auto and raise modes, the escalation guard (irreversible questions by default, and always a question with no recommendation), the question contract agents return, and the decisions log that goes into the PR. Load when an agent hits a fork it cannot resolve from its inputs, or when an orchestrator receives NEEDS_INPUT.
user-invocable: false
---

# Question policy

Claude Code removes `AskUserQuestion` from every subagent. Only the main session can ask. So
every agent in a pipeline emits questions as data, and the orchestrator in the main session decides
whether to ask, using the mode resolved by `ship_config.py`.

## Modes

| Mode | Agent behavior | Orchestrator behavior |
|---|---|---|
| `auto` (default) | pick `recommended`, append to `decisions.md`, continue; a question with no `recommended` is guarded (below) | copy `decisions.md` into the PR body under "Decisions made autonomously" |
| `raise` | stop and return `NEEDS_INPUT` with the questions | ask at once, write `answers.json`, resume the same agent |

## Escalation guard

`escalate` lists question properties that are never auto-decided. The default is
`["irreversible"]`; `"external"` adds questions whose `impact` is `external`. A question with no
`recommended` option is always guarded, whatever `escalate` says: a recommendation exists only
with an evidence-backed lean, and a coin flip logged as a decision would misrepresent itself. A
guarded question is never decided by the agent in any mode.

A guarded question is handled as in `raise` mode, whatever the mode. Headless, where nothing can be
asked, the orchestrator marks the story `blocked` with the question in its status rather than
guessing.

Set `--escalate=none` to drop the `irreversible` guard. Questions with no `recommended` option
stay guarded regardless.

## What is not a question

A permission denial, a missing tool, a command that will not run, or a path that does not exist is
an operational block, not a fork in the work. An agent that hits one returns `FAILED` with the
blocker in `summary` and does not dress it up as a question; the orchestrator marks the story
blocked and names the blocker, because the remedy is in the environment, not in an answer. The
code-reviewer without the Agent tool is not blocked: it reviews in a single pass and says so.

## Question contract

Agents return questions inside their envelope. [references/question.schema.json](references/question.schema.json)
is the normative schema. The shape mirrors the house rules every interactive command in this
marketplace already follows, so a question renders faithfully through `AskUserQuestion`:

- Two to four options. When the inputs support a lean, the recommended option is first, its label
  ends with `(Recommended)`, and `recommended` carries that label. Never mark one from absence of
  contrary signal; omit `recommended` instead.
- Every option's description is `<implication> · Counter: <trade-off or objection>`. The recommended
  option carries the strongest counter.
- A defer option is always present unless work cannot proceed without an answer:
  `Defer — file under Stakeholder decisions needed before merge`.
- No "Other" option; the tool adds free text itself.
- `header` is at most 12 characters.
- Options come from the inputs. If the inputs suggest none, that is an unknown to flag, not a
  reason to invent options.

```json
{
  "id": "Q4",
  "phase": "planner",
  "header": "Token store",
  "question": "AC-3 requires refresh tokens to survive a DB leak. Hash or encrypt them?",
  "options": [
    {"label": "bcrypt hash (Recommended)", "description": "Leaked rows are useless · Counter: tokens cannot be recovered for debugging"},
    {"label": "AES-GCM encrypt", "description": "Reversible for support tooling · Counter: a leaked key leaks every token"},
    {"label": "Defer — file under Stakeholder decisions needed before merge", "description": "Keep plaintext behind a TODO · Counter: AC-3 stays unmet"}
  ],
  "recommended": "bcrypt hash (Recommended)",
  "reversibility": "costly",
  "impact": "local",
  "multiSelect": false
}
```

`reversibility` is `reversible`, `costly`, or `irreversible`. `impact` is `local`, `cross-story`,
or `external`. These two fields drive the escalation guard; model-reported confidence does not,
because it is poorly calibrated.

## Return envelope

Every phase agent ends with one fenced JSON block:

```json
{
  "status": "DONE | NEEDS_INPUT | FAILED",
  "artifact": "/context/012-auth/plan-012.md",
  "summary": "at most five lines",
  "questions": [],
  "decisions": [{"id": "D3", "question": "...", "chosen": "bcrypt hash", "why": "...", "reversibility": "costly"}]
}
```

`questions` is non-empty only with `NEEDS_INPUT`. `decisions` lists what the agent decided itself
this run.

## Decisions log

`decisions.md` in the story's context folder, one line per decision, append-only. Create it with
Write when it does not exist; otherwise append with the Edit tool. Never Write over an existing
file, which replaces what earlier phases logged:

```
- D3 · planner · Hash or encrypt refresh tokens? → bcrypt hash · costly · AC-3 requires leak resistance; hashing needs no key management
```

The PR body copies this file verbatim so reviewers can object in review, which is the cheapest
place to revisit a call that was made without them.

## Resuming after an answer

The orchestrator writes `answers.json` keyed by `<phase>:<id>`, since every agent numbers its own
questions from `Q1`: the chosen option's label as a string, a list of labels for a `multiSelect`
question, or the user's free text when they typed their own answer, for example
`{"planner:Q4": "bcrypt hash (Recommended)", "planner:Q5": ["test_login", "test_refresh"]}`. The
file accumulates across the story; an answer is never removed. It resumes the same agent with the
path, and the agent reads only the keys that carry its own phase. The agent records each answer as a decision with `why: "user"` and
continues from where it stopped. It never re-asks a question that has an entry in `answers.json`.
