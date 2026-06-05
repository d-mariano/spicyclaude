---
name: writing-tickets
description: Drafts and refines tickets (Story, Task, Bug, Spike, Epic) with concrete acceptance criteria, observable behaviour, and explicit out-of-scope. Use whenever the work is to write up a piece of work — a story, ticket, issue, AC, "write this up", "turn this into a ticket" — regardless of whether it will be published to Jira, Linear, GitHub Issues, kept as a local markdown file, or pasted into chat. Also handles publishing to Jira via the Atlassian MCP when the user asks; loads tracker-specific guidance only on demand.
---

# Ticket Authoring

Pick the issue type that fits the work, then read the sub-file for the template and type-specific guidance before drafting.

## Issue Types
- **Epic** — multi-sprint features, typically born from a PRD. Use on request. See [epic.md](epic.md)
- **Spike** — research or PoC work that may produce more issues. See [spike.md](spike.md)
- **Story** — user-facing features and behaviour changes. See [story.md](story.md)
- **Task** — technical or operational work. See [task.md](task.md)
- **Bug** — defects. See [bug.md](bug.md)

## Definitions
- **Acceptance Criteria**: observable behaviour or deliverables. Testable from the outside.
- **Engineering Notes**: how-to. Libraries, patterns, code pointers, citations.

## Steps
- ALWAYS use the template from the matching sub-file
- If there are any gaps in the details, push back with clarifying questions before drafting
- Create one or more tickets to capture the work; split when scope spans types
- Always include reference and resource links in Engineering Notes and Summary where applicable
- When referencing code or files, link to a canonical repo URL (e.g. a GitHub permalink at the current commit, derived from `git remote` and `git rev-parse HEAD`) rather than a bare path — tickets must stand on their own
- Do not write large chunks of tests or novels
- Communicate effectively and keep it to the point
- Conduct any web searches needed for frameworks in use, unless the usage examples in code are telling enough
- Refer to usage examples and best practices when found
- Research if third-party packages in use already provide required types and explicitly call this out
- If alternative approaches are identified and you have a preference, only mention your preference
- Favour simplicity and elegance
- Cite sources

## Output

### Authoring (default)
Emit the drafted ticket(s) as markdown — one per file in a sensible location the user picks, or inline in chat if that's what they asked for. The ticket should stand on its own: a reader who hasn't been in this conversation can act on it.

### Publishing (on request)
If the user wants the ticket(s) published to Jira, load [references/publishing-to-jira.md](references/publishing-to-jira.md) for the MCP tool surface, field-handling quirks, and Epic-linking rules. Do not assume publishing — the user must ask.

For publishing an entire design-breakdown batch (epic + N stories with a dependency graph and frontmatter metadata), load [references/breakdown-batch-publishing.md](references/breakdown-batch-publishing.md) instead — same MCP surface, but with the frontmatter contract, the `jira-keys.md` map convention, and the two-pass create-then-link flow.
