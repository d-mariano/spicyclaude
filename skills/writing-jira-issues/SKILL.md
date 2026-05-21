---
name: writing-jira-issues
description: Creates and updates Jira issues across types (Epic, Spike, Story, Task, Bug). Use when creating, updating, or tracking work in Jira.
---

# Jira Issue Creation

Pick the issue type that fits the work, then read the sub-file for the template and type-specific guidance before creating.

## Issue Types
- **Epic** — multi-sprint features, typically born from a PRD. Use on request. See [epic.md](epic.md)
- **Spike** — research or PoC work that may produce more issues. See [spike.md](spike.md)
- **Story** — user-facing features and behaviour changes. See [story.md](story.md)
- **Task** — technical or operational work. See [task.md](task.md)
- **Bug** — defects. See [bug.md](bug.md)

## Definitions
- **Acceptance Criteria**: observable behaviour or deliverables. Testable from the outside.
- **Engineering Notes**: how-to. Libraries, patterns, code pointers, citations.
- **Issue Links** (blocks / is blocked by / relates to) and **Epic parent** are Jira fields, not body content. Set them via `additional_fields` on `createJiraIssue`; if create drops them, follow up with `editJiraIssue`.
- Never create subtasks. Use issue links instead.

## Steps
- ALWAYS use the template from the matching sub-file
- If there are any gaps in the details, push back with clarifying questions before creating
- Create one or more issues to capture the work; split when scope spans types
- Always attach created Stories, Spikes, Tasks, or Bugs to an Epic unless instructed otherwise
- If you are unsure which Epic to attach to, ask which Epic
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
- Output any issues created with their keys and links
