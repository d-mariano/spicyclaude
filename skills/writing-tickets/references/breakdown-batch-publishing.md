# Publishing a design-doc breakdown to Jira (MCP, batch)

Load this file when the user wants to publish a whole batch — typically the output of the `design-breakdown` skill (one epic + N stories with a dependency graph). For one-off ticket publishing, use [`publishing-to-jira.md`](publishing-to-jira.md) instead.

The contract is shared with `design-breakdown` — that skill emits markdown files in the format described below, this file describes how to ingest them.

## The contract

`design-breakdown` writes one markdown file per ticket, with YAML frontmatter carrying the breakdown-time metadata and a publishable body below it. Filenames are `NN-slug.md` (the `NN` is sort-order only — never appears in titles or Jira summaries).

```markdown
---
breakdown_id: "06b"
type: task
size: M
blocks_on: ["01"]
coordinates_with: ["02", "03", "06", "11", "14"]
---
# [Worker] Ship graceful shutdown + concurrency cap + metrics exporter + checkpointer scaffold

# Summary

…body verbatim…

# Acceptance Criteria

…

# Engineering Notes

…
```

**Frontmatter fields:**

| Field | Required | Notes |
|---|---|---|
| `breakdown_id` | yes (children) | Quoted string. Stable handle that `blocks_on` / `coordinates_with` reference. Matches the leading `NN[a-z]?` in the filename. Absent on the epic file (the epic has no parent or siblings to reference it). |
| `type` | yes | Lowercase: `epic`, `story`, `task`, `spike`, `bug`. Drives the Jira issue-type selection. |
| `size` | optional | `S` / `M` / `L`. Breakdown-time sizing hint; not exported to Jira fields (Jira teams use their own estimation surfaces). |
| `blocks_on` | yes (use `[]` if empty) | List of quoted `breakdown_id`s. Each one becomes a `Blocks` issue link at publish time (this ticket "is blocked by" each). |
| `coordinates_with` | yes (use `[]` if empty) | List of quoted `breakdown_id`s. Each becomes a `Relates` issue link. The publisher dedupes pairs (A in B's list AND B in A's list → one link). |

**Why quote breakdown_ids?** YAML parses bare `01` as a number in some parsers and as a string in others. Quoting is safe and consistent across `01`, `06b`, `11a`.

**Why frontmatter and not a header block?** The frontmatter is mechanical to strip during publish (any YAML parser will do it). A prose header block requires fragile regex stripping and shows up in the Jira description if you miss it.

**Body rule:** everything below the frontmatter is publishable verbatim. The first `# H1` is the ticket summary; the rest is the description. The body should be self-contained — no references to "see story 06b above" or similar (those references survive into Jira where they don't resolve; reference Jira keys via the map below instead, after the first publish). Code/file references must already be permalinked per [`code-references.md`](code-references.md) — the pre-publish lint below stops the batch if they aren't.

## The key-map file

The publisher writes (and reads) `<breakdown-dir>/jira-keys.md` — a single-file index mapping `breakdown_id` → Jira key for the published batch. This is the **only place** the Jira key lives in the repo; do not duplicate it into per-file frontmatter (two-source-of-truth bug waiting to happen).

```markdown
# Jira keys for <project> breakdown

| Markdown file | Jira key |
|---|---|
| `epic.md` | [AGAI-595](https://sandboxquantum.atlassian.net/browse/AGAI-595) |
| `01-tf-foundation.md` | [AGAI-602](https://sandboxquantum.atlassian.net/browse/AGAI-602) |
| `02-temporal-namespace.md` | [AGAI-603](https://sandboxquantum.atlassian.net/browse/AGAI-603) |
| … | … |
```

Use the filename (not the `breakdown_id`) as the key — it's grep-friendly and unambiguous when a story is renamed. Mark unpublished rows with `_pending_` during in-flight publish so a partial-failure recovery is obvious.

## Pre-publish lint

Before creating anything, scan every body — this is the last stop before broken references ship:

- **Relative markdown links** (`](./`, `](../`): fail, with one exception — the epic's `./NN-slug.md` story links, which Pass 3 rewrites. `grep -nE '\]\((\./|\.\./)' *.md` finds them mechanically.
- **Bare repo paths with no permalink**: an Engineering Notes line naming `src/foo.ts` with no `https://` link alongside fails the reference contract ([`code-references.md`](code-references.md)).
- **Conversational references**: "see above", "as discussed", "story 06b" in prose.

On any hit: stop, report the per-file list, fix the markdown, re-run. Don't publish a batch you know is broken — editing 20 Jira descriptions after the fact is the expensive path.

## Publish flow

**Pass 1 — create issues + capture keys:**

1. Parse each markdown file's frontmatter + body.
2. Decide the Jira issue type from `type` field, mapping any types the project lacks (see below).
3. Call `createJiraIssue` with:
   - `summary` = the body's first H1 stripped of `#`
   - `description` = the body below the H1, `contentFormat: "markdown"`
   - `additional_fields.parent` = the epic's Jira key (set after the epic is created or already in `jira-keys.md`)
   - `additional_fields.labels` = a batch label like `<project>-v1` so the whole batch is JQL-filterable later
4. After each successful create, verify the returned issue carries `parent` and `labels` (per `publishing-to-jira.md` — these are silently droppable; follow up with `editJiraIssue` if missing).
5. Append the returned key to `jira-keys.md`.
6. Do the epic first (or `editJiraIssue` an existing epic the user wants reused), since children need its key.

**Pass 2 — apply issue links:**

1. Read `jira-keys.md` into an in-memory `{ breakdown_id → AGAI-NNN }` map.
2. For each story file, translate `blocks_on` and `coordinates_with`:
   - `blocks_on: ["X"]` → `createIssueLink` with `type: "Blocks"`, `inwardIssue: <key of X>` (the blocker), `outwardIssue: <key of this story>` (the blocked). The MCP tool's directionality is "inward = blocker, outward = blocked" — easy to invert; double-check before running.
   - `coordinates_with: ["X"]` → `createIssueLink` with `type: "Relates"`. Dedupe pairs by ordering `(min_id, max_id)` so each pair gets one link, not two.
3. Batch 8–10 link calls in parallel per message — each is independent.

**Pass 3 — rewrite the epic's story links:**

The epic body ships with relative `[<title>](./NN-slug.md)` links that resolve to nothing in Jira. Once all keys are captured:

1. Take the epic's markdown body and replace each `(./NN-slug.md)` target with the child's browse URL (`https://<site>.atlassian.net/browse/<KEY>`) from `jira-keys.md`.
2. `editJiraIssue` the epic with the rewritten description.
3. On re-publish, rewrite from the markdown epic body again (the source of truth) — never from the previously published description.

**Dry-run discipline.** Always publish exactly one ticket first (any Task or Story), pause, ask the user to eyeball the Jira rendering in the browser. Markdown rendering catches checkboxes (`- [ ]` becomes literal `\[ \]`), tables, fenced code, and structural fidelity. If the dry-run is off, switch to `contentFormat: "adf"` and re-render the single dry-run ticket before batching the rest.

## Field handling quirks

| Concern | What to do |
|---|---|
| Project lacks `Spike` issue type | Map `type: spike` → Jira `Task`. The intent is preserved by the title prefix the breakdown already includes (`[Phase 1] Spike: …` / `[Phase 2 gate] Spike: …`). Keep the `type: spike` in frontmatter so the source of truth stays accurate. |
| Project lacks `Story` (uses `Task` for everything) | Map `type: story` → `Task` and warn the user once. Don't silently downcast multiple types into one. |
| Custom required fields on create | First create will surface the requirement. Stop, ask the user, do not invent values. |
| Markdown checkboxes don't render | Cost-benefit: ADF gets real checkboxes but every description has to be hand-built as ADF nodes. Markdown is the default; switch to ADF only if the user cares enough to ask. |
| Parent / labels silently dropped on create | Verify by re-fetching one and follow up with `editJiraIssue` per dropped field (per `publishing-to-jira.md`). |
| Long descriptions (>32 KB rendered) | Jira accepts them but rendering slows. If a single story's body is that large, the breakdown probably needs splitting — surface to the user, don't truncate silently. |

## Re-publishing (when the markdown changes)

When a story's markdown changes after the first publish, **don't create a duplicate ticket** — `editJiraIssue` the existing one:

1. Look up the Jira key in `jira-keys.md` by filename.
2. If found, `editJiraIssue` with the updated `summary` / `description` / `labels` as appropriate.
3. If not found, `createJiraIssue` as in Pass 1 and append to the map.

For `blocks_on` / `coordinates_with` changes, the diff is annoying — old links don't auto-remove. Either:
- Diff old vs. new dep graph, `createIssueLink` for additions, ignore removals (cheap; clutters the issue with stale links).
- Or fetch existing issue links, compute the delta, and remove + add (correct; more MCP calls). Default to the second when a story is restructured.

If `breakdown_id` itself ever changes (rare — usually means a story was renumbered), update `jira-keys.md` first; the Jira key stays the same.

When the epic's markdown changes, re-run the Pass 3 link rewrite after the edit — always from the markdown source, so relative story links never reach Jira unrewritten.

## When publishing fails

Same recipes as [`publishing-to-jira.md`](publishing-to-jira.md): auth error → stop and ask the user to authenticate; required custom field → surface and ask; unknown type → ask; partial batch failure → stop and report what landed (don't auto-clean — the user may prefer to keep partial state and resume).

For batch publishes specifically: report progress in counts (`12/22 created, 4/77 links applied`) so a mid-flight failure is recoverable from a known position. The map file is the source of truth for "what's already created" — read it before assuming the batch is fresh.

## Output

After publishing, give the user a flat list grouped by phase (using the dep graph's wave structure if helpful) with the Epic on top. Same shape as `publishing-to-jira.md` Step 6 but multiplied for the batch.
