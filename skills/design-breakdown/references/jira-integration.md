# Pushing the breakdown to Jira (acli)

Load this only when the user has confirmed they want to publish and the Atlassian MCP isn't available. Creating tickets is a side effect with a clumsy undo path — never proactive.

Mechanical work runs via [`publish-breakdown-acli.sh`](./publish-breakdown-acli.sh). This file covers the human-judgement parts: when to reach for `acli`, what to verify before running, and the failure modes.

## When to use this vs. the MCP flow

MCP batch flow ([`../../writing-tickets/references/breakdown-batch-publishing.md`](../../writing-tickets/references/breakdown-batch-publishing.md)) is the recommended default when the Atlassian MCP is authenticated. Reach for `acli` when:

- The MCP isn't installed or isn't authenticated for the user's site.
- The user explicitly prefers a scriptable / CI-runnable flow.
- The MCP server isn't reachable from the current environment but `acli` is.

Both paths read the same frontmatter contract and write the same `jira-keys.md`, so you can switch between them across batches without redoing work.

## Contract

Frontmatter + body shape is identical to the MCP flow — single source of truth lives in [`breakdown-batch-publishing.md §The contract`](../../writing-tickets/references/breakdown-batch-publishing.md). Nothing about file format is `acli`-specific.

## Prerequisites

Hard dependencies (script fails loud if missing): `acli`, `yq`, `jq`, `awk`, `sed`.

- **acli install**: <https://developer.atlassian.com/cloud/acli/guides/install-acli/>. The binary is `acli`, not `jira` or `atlassian`.
- **auth**: easiest is `acli jira auth login --web` (OAuth via browser). API token alternative: `echo "<token>" | acli jira auth login --site "yoursite.atlassian.net" --email "you@example.com" --token`.
- **auth check**: the script runs `acli jira project view --key <PROJECT_KEY>` as a smoke test before any creates.

## Terminology quirks worth internalising

- Jira's CLI calls them **work items**, not issues — `acli jira workitem create`. The type (Epic, Story, Task, Bug) is set via `--type`.
- `--description-file` accepts plain text or ADF. Markdown passes through as plain text — Jira **won't render** headings, bold, or checkboxes the way GitHub does. Warn the user upfront.

## Running the script

```bash
cd <breakdown-dir>
SITE="yoursite" BATCH_LABEL="my-project-v1" \
  ./publish-breakdown-acli.sh . PROJ
```

Reuse an existing epic instead of creating one:

```bash
./publish-breakdown-acli.sh . PROJ PROJ-595
```

The script lints first — any relative markdown link fails loud before anything is created (the epic's `./NN-slug.md` story links are exempt; Pass 3 rewrites them). Then Pass 1 (create epic + children, append to `jira-keys.md`), Pass 2 (apply `Blocks` + `Relates` links), and Pass 3 (rewrite the epic's story links to browse URLs — requires `SITE`, and only runs for epics the script created; for a reused epic use the MCP flow's re-publish path). Type mapping defaults: `epic→Epic`, `story→Story`, `task→Task`, `bug→Bug`, `spike→Task`. Override the `map_type()` function in the script if the project uses custom names.

## Dry-run discipline

The script publishes the whole batch in one go. **Before running on the real batch**, do a dry run on one ticket:

1. Copy a single `NN-*.md` (a simple Task) and the epic into a scratch dir.
2. Run the script against the scratch dir.
3. Open the created ticket in Jira and eyeball: description rendering, parent link, label, type.

Only run on the full breakdown after the dry-run looks right. If markdown rendering is bad enough that the team cares, the relevant knob is generating ADF for `--description-file` — a meaningful refactor; confirm with the user before doing it.

## Failure modes specific to acli

- **Flag-name drift between versions.** `acli jira workitem link` flag names (`--type` / `--from` / `--to`) have shifted across releases. The script uses the current shape; if it fails, run `acli jira workitem link --help` and fix the script before re-running.
- **Custom required fields.** First create fails with a specific error naming the missing field. Don't invent values — surface to the user.
- **Renamed/disabled types.** If `--type "Story"` fails, the project probably uses a custom name. Ask the user; edit `map_type()`.
- **Partial-batch failure.** Script exits on first error. `jira-keys.md` records what landed. To resume, you'll currently need to manually trim already-created files from the batch — the script has no resume mode (idempotency is a future improvement; for now this matches the MCP path's "stop and report" behavior).
- **Big batches (10+).** Even after a clean dry-run, consider publishing the epic + first 2–3 children, pausing to eyeball, then running again for the rest. The cost of a format mistake scales with batch size.

## Reporting

The script prints a summary on success:

```
Done. Created 23 issues in PROJ.
Links applied: 7 Blocks, 12 Relates.
Map persisted to ./jira-keys.md.
```

For a longer human-readable report (grouped by type, with titles), build it from `jira-keys.md` after the script completes.

## Re-publishing (markdown changed after first push)

The current script always creates. For re-publish, prefer the MCP flow's `editJiraIssue` path — see [`breakdown-batch-publishing.md §Re-publishing`](../../writing-tickets/references/breakdown-batch-publishing.md). If you must use `acli`, swap `acli jira workitem create` for `acli jira workitem edit --key <KEY>` in a manual loop driven by `jira-keys.md`; the script doesn't do this yet.
