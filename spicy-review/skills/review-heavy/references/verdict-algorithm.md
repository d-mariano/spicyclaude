# Verdict Algorithm (orchestrator aggregation)

The orchestrator runs this after the reviewer subagents return. Input: the raw structured
findings from all reviewers. Output: a deduplicated, filtered, severity-tiered report plus a
single verdict. Apply the steps in order.

## 1. Collect structured findings

Gather every finding from every reviewer. Each must carry: **severity, confidence (0–100),
location (file:line), category, problem, concrete fix.** Discard malformed entries that lack a
location or a concrete fix — an unactionable finding is noise.

## 2. Confidence filter

**Drop every finding with confidence < 80.** This is the hard gate from
[severity-rubric.md](severity-rubric.md). No exceptions, no "but it might be important."

## 3. Deduplicate across reviewers

Multiple reviewers may report the same underlying issue. Merge findings that point at the same
location and root cause:
- Keep the **best-fit category** (e.g. a "missing input validation" hit by both security and
  code-quality stays under **security**).
- Keep the **highest severity** and the **highest confidence** among the merged copies.
- **Re-categorize misfiled findings** — if code-quality flagged something that is really a
  security bug, move it to security.

## 4. Reasonableness filter

Apply [what-not-to-flag.md](what-not-to-flag.md) once more at the aggregate level. Drop anything
that is:
- speculative / theoretical (unlikely preconditions),
- a nitpick or taste argument,
- lint- or formatter-catchable,
- contradicted by the repo's own conventions / `CLAUDE.md`.

## 5. Verify (cross-check)

Run the [verification pass](verification.md) on the survivors. Pass them to the `verification`
subagent and apply its results: **CONFIRM** keeps a finding, **ADJUST** updates its
severity/confidence (then re-apply the confidence gate — drop if it falls below 80), **DROP**
removes it. Only the **confirmed** set continues.

## 6. Verdict

Decide from the **confirmed** findings:

| Condition                         | Verdict             |
| :-------------------------------- | :------------------ |
| Any **Critical**                  | **Needs Work**      |
| Any **High** (no Critical)        | **Needs Work**      |
| **Medium** only                   | **Needs Attention** |
| **Low** only, or nothing survives | **Ready to Merge**  |

## 7. Posting & approval policy

The verdict is a recommendation to a human, never an action. The report always prints to the
terminal. Posting happens **only** when the user passed `--post` with a PR scope, and only with the
**confirmed** findings, under the guardrails in [posting.md](posting.md). The human stays the
approver.

## Report shape

```
# Multi-Agent Code Review — <scope>   ·   Verdict: <verdict>

## Critical
<findings in the rubric's rendering format>

## High
…

## Medium
…

## Low
…

<one-line takeaway>
```

Each finding uses the rendering format from [severity-rubric.md](severity-rubric.md). Omit any
severity section that has no confirmed findings.
