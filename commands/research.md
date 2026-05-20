---
allowed-tools: Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch, mcp__atlassian__getJiraIssue
argument-hint: [topic]
description: Research a PRD, ticket, or topic by reading related code and the web before any implementation. Use when the user says 'research X', shares a PRD/Jira link, or asks to scope a feature.
---

Do not write any code right now. We are going to discuss working on $ARGUMENTS.

If you are given an identifier, attempt to use configured MCP servers like Jira to search for the related resource. If you are given a PRD, read it.

You are going to read through related code and conduct any web searches.

Perform a deep dive, gather enough context to become a subject matter expert.

## Considerations
- Conduct web searches on frameworks, protocols, APIs, or standards in use — unless usage examples in code are telling enough
- Always share usage examples and best practices when found
- Research if third-party packages in use already provide required types and explicitly call this out
- If alternative approaches are identified and you have identified a preference, only mention your preference
- Favour simplicity and elegance
- Always cite your sources

## Output
- Store your research in `/context/[nnn]-{feature|branch|question}/research-[nnn].md`, unless instructed otherwise

### Examples:
- `/context/001-implement-cool-service/research-001.md`
- `/context/001-implement-cool-service/research-002.md`
- `/context/002-cool-service-addons/research-002.md`
- `/context/some/specified/path/research-001.md`
