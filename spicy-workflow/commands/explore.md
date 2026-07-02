---
allowed-tools: AskUserQuestion, Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: "[topic]"
description: Explore code and the web to build context on a PRD or topic for in-conversation discussion — no file output. Use when the user wants to quickly scope or discuss something without persisting a research doc (use /spicy-workflow:research for that).
---

Do not write any code right now. We are going to discuss working on $ARGUMENTS.

If you are given an identifier, attempt to use configured MCP servers like Jira to search for the related resource. If you are given a PRD, read it.

You are going to read through related code and conduct any web searches.

Perform a deep dive, gather enough context to become a subject matter expert.

## Considerations
- Conduct web searches on frameworks, protocols, APIs, or standards in use — unless usage examples in code are telling enough
- Research if third-party packages in use already provide required types and explicitly call this out

## Surfacing Open Questions

When you hit a meaningful fork you cannot resolve from inputs — ambiguous scope, two equally-promising directions to dig into, contradictory sources — raise it via `AskUserQuestion` instead of silently picking. Do NOT use `AskUserQuestion` for low-stakes choices the model can reasonably commit to and document. Explore is no-output, so these questions are purely conversational steering.

Rules:

- **Batch related questions** — up to 4 per call.
- **Provide 2-4 options per question.** Each option needs a one-line description.
- **Every option's description includes a counter.** Format: `"<implication> · Counter: <trade-off or objection>"`. If an option has no real counter, the option set needs rework.
- **Mark your recommendation** with "(Recommended)" only when you have a clear, evidence-backed lean from inputs — not absence of contrary signal. The recommended option gets the strongest counter — the primary reason the user might reject it. **Place the recommended option first** in the options array.
- **`header` is hard-capped at 12 characters.** Pick a short tag ("Scope", "Direction", "Subsystem"); don't write a sentence.
- **State why the question matters** in the question text — which goal, constraint, or downstream decision rides on the answer.
- **Always offer a defer path** unless exploration genuinely cannot proceed. Phrase: `"Defer — note in conversation, proceed both directions"`. Deferred forks have no doc to land in; carry them in conversational context only.
- **Options come from inputs only.** Don't draw on training-data preferences when proposing option sets. If inputs don't suggest any, that's an unknown — flag it, don't invent options.
- **Use `multiSelect: true`** when the choices are not mutually exclusive — e.g., "Which subsystems should I scope into the discussion?", "Which angles do you want covered?". Default `false` for picking-one decisions.
- **Do NOT add an "Other" option.** The tool surfaces a free-text input automatically; adding "Other" wastes one of the 4 option slots.
