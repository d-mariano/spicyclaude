# Pushing the breakdown to Jira (Atlassian CLI)

## Contents
- Terminology quirks (acli, "work item", ADF descriptions)
- Step 1: Detect the CLI
- Step 2: Check auth
- Step 3: Gather what you need from the user (project key, types, labels)
- Step 4: Dry-run (full command template and flag reference)
- Step 5: Create, then sync the keys back to markdown
- Step 6: Report back
- Pushback specific to Jira (big batches, markdown rendering, custom fields, renamed types)

Load this file only when the user has confirmed they want to push the breakdown to Jira. Creating tickets is a side effect with a clumsy undo path; do not invoke any of this proactively.

This uses the **official Atlassian CLI (`acli`)**. Docs: https://developer.atlassian.com/cloud/acli/. Notable terminology quirks worth internalising before running anything:

- The binary is **`acli`**, not `jira` or `atlassian`.
- Jira's CLI surface uses the term **"work item"** rather than "issue" — `acli jira workitem create`, not `acli jira issue create`. The work item *type* (Epic, Story, Task, Bug, ...) is set via `--type`.
- Descriptions accept **plain text or ADF** (Atlassian Document Format). Markdown is technically plain text, so it goes through, but Jira won't render headings, bold, or checkboxes the way GitHub does. Mention this to the user so they're not surprised by the rendering.

## Step 1: Detect the CLI

```bash
command -v acli
```

If that returns a path, the CLI is installed. Confirm version and that it's the modern `acli` (not an older third-party tool that may also be on PATH):

```bash
acli --help
acli jira workitem create --help
```

If `acli` isn't installed, tell the user the markdown breakdown is ready and offer:
- They can install ACLI per https://developer.atlassian.com/cloud/acli/guides/install-acli/ and re-run.
- They can paste each story's markdown into Jira manually.

Do **not** fall back to calling the Jira REST API with `curl` unless the user explicitly asks; that requires credentials this skill shouldn't be reaching for.

## Step 2: Check auth

ACLI supports OAuth (`acli jira auth login --web`, browser-based, easiest) and API tokens. Don't try to authenticate the user yourself — if they're not logged in, point them at one of:

```bash
# Easiest: OAuth via browser
acli jira auth login --web

# Or with an API token
echo "<token>" | acli jira auth login --site "yoursite.atlassian.net" --email "you@example.com" --token
```

Then attempt a low-impact command to confirm auth works before any creates:

```bash
acli jira project view --key <PROJECT_KEY>   # or any read-only command
```

If that fails with an auth error, stop and report. Don't proceed to creates.

## Step 3: Gather what you need from the user

Ask explicitly — do **not** guess:

- **Project key** (e.g. `PROJ`, `ENG`, `BILL`). Required.
- **Epic type name**. Usually `Epic`, but some Jira projects rename or disable it.
- **Story type name**. Usually `Story`, sometimes `Task`.
- **Labels** to apply to everything in this breakdown (optional but useful — a label like `design-doc-<slug>` makes the whole breakdown easy to find or bulk-edit later).
- **Assignee** (optional). `@me` self-assigns; an email address assigns to that user; leave unassigned by default.

If the project requires custom fields you don't know about, the first create will fail with a specific error. That's fine — it's the cheapest way to learn the requirement. Don't try to predict required fields.

## Step 4: Dry-run

Show the user the exact commands you plan to run, in order, and **wait for explicit "go"** before touching Jira. Template:

```bash
# 1. Create the epic, capture its key
EPIC_KEY=$(acli jira workitem create \
  --project "PROJ" \
  --type "Epic" \
  --summary "<epic title>" \
  --description-file "breakdown/epic.md" \
  --label "design-doc-<slug>" \
  --json | jq -r '.key')
echo "Created epic: $EPIC_KEY"

# 2. Create each story, linking to the epic via --parent
acli jira workitem create \
  --project "PROJ" \
  --type "Story" \
  --summary "<story title>" \
  --description-file "breakdown/01-<story-slug>.md" \
  --parent "$EPIC_KEY" \
  --label "design-doc-<slug>" \
  --json

# ... repeat per story
```

Key flags worth knowing (from `acli jira workitem create --help`):

| Flag | Purpose |
|---|---|
| `-p, --project` | Project key (e.g. `PROJ`) |
| `-t, --type` | `Epic`, `Story`, `Task`, `Bug`, etc. |
| `-s, --summary` | The title |
| `-d, --description` | Description as a string (plain text or ADF) |
| `--description-file` | Description from a file — use this for our markdown stories |
| `--parent` | Parent work item ID — this is how a story links to its epic |
| `-l, --label` | Comma-separated labels |
| `-a, --assignee` | Email, account ID, or `@me` |
| `--json` | Machine-readable output (use this when you need to capture the new key) |
| `--from-json` / `--generate-json` | For fully structured input — overkill for our flow, but mention if the user wants advanced control |

There's also `acli jira workitem create-bulk` for batch creates. It's faster for big breakdowns, but harder to recover from a partial failure. Default to per-story creates unless the user asks for bulk.

## Step 5: Create, then sync the keys back

After each successful create, append the new Jira key to the corresponding markdown file as a header line so the repo and Jira stay in sync:

```markdown
**Jira:** PROJ-1234
```

This makes future iteration (re-running, updating, closing) much easier. Future-you (or future-Claude) reading the markdown can tell at a glance which stories are already tracked.

If any create fails partway through, **stop and report**. Don't try to auto-clean up by deleting partial work — the user may prefer to keep what landed and resume from the failure point.

## Step 6: Report back

Give the user a flat list:

```
Created in Jira (project PROJ):
- PROJ-1234  Epic:    Migrate billing to event-driven pipeline
- PROJ-1235  Story 01: Introduce BillingEvent schema
- PROJ-1236  Story 02: ...
```

## Pushback specific to Jira

- **Big batches.** If the breakdown is many tickets (rough threshold: ~10+), offer to create the epic and the first 2–3 stories first so the user can sanity-check the rendering and labels before you create the rest. The cost of getting the format wrong scales with batch size.
- **Markdown rendering.** Mention once that headings, bold, and checkboxes in the markdown won't render the same way they do in a GitHub preview — Jira will show plain text. If the user cares, suggest editing the most-viewed tickets (the epic in particular) directly in Jira after creation, or generating an ADF description instead.
- **Custom workflows.** If the project enforces mandatory custom fields (the first create will tell you), don't try to invent values. Surface the requirement and ask the user.
- **Renamed/disabled types.** If `--type "Epic"` or `--type "Story"` fails, the project probably uses custom names. Ask rather than guess.
