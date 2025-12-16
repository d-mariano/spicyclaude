---
allowed-tools: Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: [topic]
description: Explore relevant files and resources to gain enough context for a full understanding of the given PRD or topic.
---
Ultrathink.

You are a world class software engineer.

Do not write any code right now. We are going to discuss working on $1.

If you are given an identifier, attempt to use configured MCP servers like to search for the related resource. If you are given a PRD, read it.

You are going to read through related code and conduct any web searches.

Gather enough context, become a subject matter expert and prepare to discuss.

## Considerations
- Conduct any web searches that you may need on frameworks in use, unless the usage examples in code are telling enough
- Conduct any web searches on official protocols, APIs, or standards
- Research if third-party packages in use already provide required types and explicitly call this out
