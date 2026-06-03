---
allowed-tools: AskUserQuestion, Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch, mcp__atlassian__getJiraIssue
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

## Surfacing Open Questions

Research is the front-loaded chance to resolve ambiguity *while the user is still context-loaded on the PRD*. Every PRD/AC ambiguity that survives this phase becomes a planning-time interrupt later — by which point the user has moved on and has to re-context-load to answer. Push hard upstream.

### Mandatory pre-output question pass

Before writing the research doc, do a **dedicated sweep** for unresolved upstream ambiguity and surface every fork via `AskUserQuestion` (batched, up to 4 per call; chain calls if more remain). Trigger on:

- **PRD/AC ambiguity** — any AC clause open to two reasonable interpretations; any goal whose success metric is undefined; any persona/use-case the PRD names but doesn't bound.
- **Scope boundary** — anything plausibly in or out where the PRD doesn't decide; non-goals that the natural design path would still touch.
- **Contradictory sources** — PRD vs. cited research; two cited sources that disagree on a load-bearing fact.
- **Approach forks where the answer changes the recommended direction** — two equally-promising libraries/protocols/patterns where the choice gates which deep-dive is worth doing.
- **Cross-cutting prerequisites** — auth, tenancy, data residency, compliance constraints the PRD assumes but doesn't pin down.

Do NOT use `AskUserQuestion` for low-stakes navigation ("should I read the gRPC docs or the proto file first?") — pick and proceed.

### Rules

- **Provide 2-4 options per question.** Each option needs a one-line description.
- **Every option's description includes a counter.** Format: `"<implication> · Counter: <trade-off or objection>"`. If an option has no real counter, the option set needs rework.
- **Mark your recommendation** with "(Recommended)" only when you have a clear, evidence-backed lean from inputs — not absence of contrary signal. The recommended option gets the strongest counter — the primary reason the user might reject it. **Place the recommended option first** in the options array.
- **`header` is hard-capped at 12 characters.** Pick a short tag ("Scope", "AC interp", "Lib choice"); don't write a sentence.
- **State why the question matters** in the question text — which PRD goal, AC item, NFR, or downstream decision rides on the answer.
- **Always offer a defer path** unless the research genuinely cannot proceed without the answer. Phrase: `"Defer — record in Open Questions section of research doc"`.
- **Options come from inputs only.** Don't draw on training-data preferences when proposing option sets. If inputs don't suggest any, that's an unknown — flag it, don't invent options.
- **Use `multiSelect: true`** when the choices are not mutually exclusive — e.g., "Which AC items need clarification?", "Which related subsystems should I bring into scope?". Default `false` for picking-one decisions.
- **Do NOT add an "Other" option.** The tool surfaces a free-text input automatically; adding "Other" wastes one of the 4 option slots.

After every answer, fold the choice into the research and update the Open Questions section as needed. Deferred items must have a concrete working assumption — see the Open Questions table format below.

## Output
- Store your research in `/context/[nnn]-{feature|branch|question}/research-[nnn].md`, unless instructed otherwise
- End the research doc with an **Open Questions** section using this table:

  ```markdown
  ## Open Questions
  | Question | Working Assumption | Resolve By |
  ```

  One row per deferred fork. Every row must have a concrete working assumption — a deferral with no assumption is invalid.

### Examples:
- `/context/001-implement-cool-service/research-001.md`
- `/context/001-implement-cool-service/research-002.md`
- `/context/002-cool-service-addons/research-002.md`
- `/context/some/specified/path/research-001.md`
