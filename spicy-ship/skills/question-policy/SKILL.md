---
name: question-policy
description: How ship pipelines handle open questions when the agent doing the work cannot ask the user. Defines the auto, raise, and batch modes, the irreversible-only escalation guard, the question contract agents return, and the decisions log that goes into the PR. Load when an agent hits a fork it cannot resolve from its inputs, or when an orchestrator receives NEEDS_INPUT.
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
| `batch` | proceed on `recommended` provisionally, log the question as `provisional`; a question with no `recommended` is guarded (below) | ask at the next checkpoint; an answer that differs from the recommendation re-runs the phase |

Checkpoints in `batch` mode are the natural seams: after decomposition, after each plan gate, and
before opening a PR.

## Escalation guard

`escalate` lists question properties that are never auto-decided. The default is
`["irreversible"]`; `"external"` adds questions whose `impact` is `external`. A question with no
`recommended` option is always guarded, whatever `escalate` says: a recommendation exists only
with an evidence-backed lean, and a coin flip logged as a decision would misrepresent itself. A
guarded question is never decided by the agent in any mode.

What each party does with a guarded question:

- **The agent** commits whatever is complete, returns `NEEDS_INPUT` with the question, and stops.
  This is the same in `auto`, `batch` and `raise`; an agent cannot queue anything.
- **The orchestrator** asks at once in `raise` mode, and in `auto` and `batch` holds the question
  until the next checkpoint, where it asks and then resumes the agent with `answers.json`.
- **Headless**, where nothing can be asked, the orchestrator marks the story `blocked` with the
  question in its status rather than guessing.

Set `--escalate=none` to drop the `irreversible` guard. Questions with no `recommended` option
stay guarded regardless.

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

`decisions.md` in the story's context folder, one line per decision, append-only:

```
- D3 · planner · Hash or encrypt refresh tokens? → bcrypt hash · costly · AC-3 requires leak resistance; hashing needs no key management
```

Provisional decisions in `batch` mode carry `· provisional` until the checkpoint confirms or
overrides them. The PR body copies this file verbatim so reviewers can object in review, which is
the cheapest place to revisit a call that was made without them.

## Resuming after an answer

The orchestrator writes `answers.json` keyed by question id: the chosen option's label as a string,
a list of labels for a `multiSelect` question, or the user's free text when they typed their own
answer, for example `{"Q4": "bcrypt hash (Recommended)", "Q5": ["test_login", "test_refresh"]}`.
It resumes the same agent with the path. The agent records each answer as a decision with `why: "user"` and
continues from where it stopped. It never re-asks a question that has an entry in `answers.json`.
