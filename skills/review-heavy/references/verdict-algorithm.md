# Verdict Algorithm

How the orchestrator turns raw reviewer output into one consolidated report. Run these steps in order.

## 1. Collect

Gather every structured finding from all reviewers. Each must carry: `severity`, `confidence` (0–100), `file:line`, `category`, and a concrete fix. Drop anything missing these — a finding you can't act on isn't a finding.

## 2. Confidence filter

Drop every finding with **confidence < 80**. (See `severity-rubric.md`.) No exceptions.

## 3. Deduplicate

Multiple reviewers may flag the same line. Collapse duplicates into one finding. Keep the best-fit category and re-categorize anything misfiled (e.g. a "documentation" reviewer flagging a real security hole → security).

## 4. Reasonableness filter

Drop findings that are speculative or theoretical, pure nitpicks, lint-catchable, or contradicted by the repo's own conventions. See `what-not-to-flag.md`. This filter runs *after* the confidence gate — a high-confidence nitpick is still a nitpick.

## 5. Verdict

From the surviving findings:

- Any **Critical** → **Needs Work**
- Any **High** → **Needs Work**
- **Medium** only → **Needs Attention**
- **Low** only, or clean → **Ready to Merge**

## 6. Never auto-approve

"Ready to Merge" is a recommendation, not an approval. The human stays the approver. Never auto-approve and never auto-merge.
