---
allowed-tools: Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: [topic]
description: Explore code and the web to build context on a PRD or topic for in-conversation discussion — no file output. Use when the user wants to quickly scope or discuss something without persisting a research doc (use /research for that).
---

Do not write any code right now. We are going to discuss working on $ARGUMENTS.

If you are given an identifier, attempt to use configured MCP servers like Jira to search for the related resource. If you are given a PRD, read it.

You are going to read through related code and conduct any web searches.

Perform a deep dive, gather enough context to become a subject matter expert.

## Considerations
- Conduct web searches on frameworks, protocols, APIs, or standards in use — unless usage examples in code are telling enough
- Research if third-party packages in use already provide required types and explicitly call this out
