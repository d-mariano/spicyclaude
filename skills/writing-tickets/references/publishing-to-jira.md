# Publishing tickets to Jira (Atlassian MCP)

Load this file only when the user has confirmed they want a ticket pushed to Jira. Publishing has side effects that are clumsy to undo — do not invoke any of this proactively.

This covers **one-off ticket publishing** via the Atlassian MCP. For pushing an entire design-doc breakdown (epic + N stories, with `--parent` links and a per-doc label), see [`../../design-breakdown/references/jira-integration.md`](../../design-breakdown/references/jira-integration.md) — different surface (`acli`), different recipe.

## Tool surface

The Atlassian MCP exposes Jira operations as `mcp__atlassian__*` tools. The two you'll reach for most:

- `createJiraIssue` — create a new work item (Epic, Story, Task, Spike, Bug). Returns the new issue key.
- `editJiraIssue` — update an existing issue. Needed as a follow-up when `createJiraIssue` silently drops fields (see below).

If the MCP server isn't authenticated, the first call will surface an auth error. Stop and ask the user to authenticate; don't try to work around it with the REST API or `curl`.

## Field handling quirks

Two things bite repeatedly:

### Issue Links and Epic parent

`Issue Links` (`blocks` / `is blocked by` / `relates to`) and `Epic parent` are Jira fields, **not body content**. Set them via `additional_fields` on `createJiraIssue`:

```jsonc
{
  "additional_fields": {
    "parent": { "key": "PROJ-1234" },         // Epic parent
    "issuelinks": [
      { "type": { "name": "Blocks" }, "outwardIssue": { "key": "PROJ-1235" } }
    ]
  }
}
```

### Create may drop these fields

If `createJiraIssue` accepts the call but the returned issue is missing the `parent` or `issuelinks` you set (different Jira projects have different schemas for what's settable at create time), follow up with `editJiraIssue` against the new key to apply them. Don't assume the create stuck.

### Subtasks

**Never create subtasks.** They have weird parent-child semantics across Jira projects and surface poorly in most reporting views. Use issue links (`is blocked by` / `relates to`) instead.

## Linking to an Epic

Stories, Spikes, Tasks, and Bugs should attach to an Epic unless the user explicitly says otherwise. If the Epic isn't named in the conversation, **ask** — don't guess based on the project key or recent work. The cost of asking is a single message; the cost of attaching to the wrong Epic is a sprint-planning headache.

If the user is creating an Epic in this same flow, use the returned Epic key as the `parent` for the children.

## Output

After each successful create, report back with:

- The issue key (e.g. `PROJ-1234`)
- A link to the issue (the MCP response includes a `self` URL; convert it to the browser URL form `https://<site>.atlassian.net/browse/<KEY>`)

For multiple tickets in one flow, return them as a flat list so the user can copy/paste into a status update.

## When publishing fails

- **Auth error**: stop, ask the user to authenticate the Atlassian MCP, don't retry.
- **Required custom field missing**: the error message will name the field. Surface the requirement and ask the user — don't invent a value.
- **Unknown issue type**: the project probably uses renamed/disabled types. Ask rather than guess.
- **Partial batch failure**: stop and report what landed. Don't auto-clean up; the user may prefer to keep what was created and resume.
