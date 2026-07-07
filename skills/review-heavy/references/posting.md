# Posting to the PR

How the orchestrator posts review findings to a GitHub PR. Posting is a **deliberate, opt-in**
action — the print-only path stays the default.

## Guardrails (non-negotiable)

- **Opt-in only.** Post only when the user passes `--post` **and** the scope is a real PR number.
  Never post on a branch/file review, and never post by default.
- **Only verified findings.** Post only the set confirmed by the [verification pass](verification.md).
  Never post dropped or sub-80-confidence findings.
- **Never reproduce secret material.** If a finding quotes an apparent secret / credential / token
  value, redact it (e.g. `sk-***REDACTED***`) before the payload is built — the posted comment
  cites `file:line` and the remediation, never the literal value. Applies to inline comments and
  the summary body alike.
- **Never `APPROVE`. Never merge.** The human stays the approver. Post the review with
  `event=COMMENT`. `REQUEST_CHANGES` is allowed **only** if the user explicitly passes
  `--request-changes` and the verdict is *Needs Work*; otherwise use `COMMENT`.
- **Post once.** One review per run. Before posting, check for an existing open review from this
  bot on the PR (`gh api repos/{owner}/{repo}/pulls/{n}/reviews`) and don't duplicate it.

## Comment format

Every posted finding — inline comment or summary bullet — uses this shape:

```
`<Severity>` · `<Category>` · `<confidence>`
**<Minimal title — fewest words that name the issue>**

<one short paragraph: the concrete problem and why it matters>

**Fix:** <the specific change>
```

Rules:
- **Chips first**: metadata as backtick chips on the top line. **Capitalize** the category for
  display (`Security`, `Code-Quality`, `Mental-Alignment`, …) even though the structured finding
  carries it lowercase. Confidence is the **bare number** — no "conf" label.
- **Bolded minimal title** on the next line (use the finding's `title` from the
  [rubric shape](severity-rubric.md); derive one if a reviewer omitted it).
- Summary-body bullets compress the same elements to one line:
  `- [<confidence>] path:line — **<Title>.** Fix: <change>`.

## Mechanism (gh)

Use `gh` — the same tooling the orchestrator already uses to fetch PR context — not the GitHub MCP.

1. Resolve `owner`/`repo`/`pr`: `gh repo view --json owner,name` and the PR number from scope.
2. Build a JSON review payload with the **Write** tool:
   ```json
   {
     "event": "COMMENT",
     "body": "<summary: verdict + tiered counts + notes + any findings that could not be anchored inline>",
     "comments": [
       { "path": "src/auth.ts", "line": 42, "side": "RIGHT",
         "body": "`High` · `Security` · `88`\n**SQL built by string concatenation**\n\nUser input reaches the query string unparameterized at line 42.\n\n**Fix:** use a parameterized query." }
     ]
   }
   ```
3. Post it:
   ```
   gh api --method POST repos/{owner}/{repo}/pulls/{pr}/reviews --input <payload.json>
   ```

## Inline anchoring

- GitHub only accepts an inline comment on a line that is **part of the PR diff**. For a finding
  whose `line` isn't in the diff, do **not** inline it — move it into the summary `body` instead
  (GitHub rejects the whole review if any comment targets a line outside the diff).
- Use `side: "RIGHT"` for added/changed lines; `LEFT` only for removed lines.

## Summary body

The review `body` carries the verdict header, the per-severity counts, the `## Notes` (Jira status,
risk tier + reviewer set, counts dropped by the gate and by verification), and any findings that
couldn't be anchored inline — so nothing verified is lost.

After posting, also print the same report to the terminal and tell the user what was posted (review
URL, event type, inline vs. summary counts).
