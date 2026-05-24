---
name: breaking-down-design-docs
description: Breaks a technical design document into an epic (or several epics) and actionable user stories with acceptance criteria, dependencies, and explicit out-of-scope items. Use this whenever a user shares a design doc, RFC, technical spec, PRD, ADR, or implementation proposal and wants it turned into work items — tickets, Jira issues, Linear tickets, stories, sprint plans, or a "plan of attack". Trigger even when the user phrases it loosely, such as "help me plan this", "how should we build this", "split this up", or "what are the tickets". Always asks clarifying questions before proposing a split and pushes back on ambiguity, hidden assumptions, oversized stories, and impossible dependencies rather than producing busy-work tickets.
---

# Breaking down design docs

The default failure mode of this task is producing a tidy-looking list of tickets that hides ambiguity. Resist that. It is better to surface three real questions than to invent answers and ship a clean-looking breakdown built on guesses.

**Early exit:** if the doc is a problem statement without a proposed solution, don't fake a breakdown. Say so and offer to break the *discovery* work down into spikes instead.

## The workflow has a hard gate

Three phases. **Do not skip from Phase 2 to Phase 3 without explicit user confirmation.** That gate is the whole point of this skill — it gives the user a chance to redirect the breakdown before you've spent effort expanding stories that will be thrown away.

Copy this checklist into your response and check items off as you go:

```
Breakdown progress:
- [ ] Phase 1: Read doc, ground in repo context, surface clarifying questions
- [ ] Phase 1 GATE: User has answered the must-answer questions (or said "skip, your call")
- [ ] Phase 2: Propose epic structure + story titles (one line each) + pushback
- [ ] Phase 2 GATE: User has confirmed or revised the split
- [ ] Phase 3: Expand each confirmed story to full markdown
- [ ] Phase 3: (Optional) Push to Jira if `acli` is available and user opted in
```

---

## Phase 1: Read and ground

If the user has only mentioned a design doc without sharing it, ask for the path, URL, or pasted content before proceeding. Otherwise, read the doc carefully. Then, **before** drafting anything:

**Ground the breakdown in repo reality (Claude Code only).** A breakdown disconnected from the codebase is fiction. Spend a few tool calls doing things like:
- Look at the repo's top-level structure and `README.md` to understand what's already there.
- Search for any module, service, or file the design names. If the design says "extend the `BillingService`", confirm `BillingService` actually exists and skim it.
- Check existing tests near the touched code — they reveal real contracts and edge cases the doc may omit.
- If the design references an external API or library, check whether it's already a dependency.

This is the single highest-leverage thing this skill does. Skipping it produces stories like "update the FooService to support bar" when no FooService exists.

**Extract the spine of the doc.** Internally note:
- **Goal**: what user/business outcome does this unlock?
- **Scope**: what's explicitly in and out?
- **Components touched**: which subsystems, services, files, or external systems?
- **Dependencies**: what relies on what? Capture this as a graph, not a list. Most stories can run in parallel; the interesting information is which ones genuinely block which others.
- **Open questions the doc itself names** (these become clarifying questions for the user).
- **Smells**: see "Pushback heuristics" below.

**Ask clarifying questions.** Not generic ones — specific, decision-blocking ones. Aim for **1–4 questions**. Zero is suspicious (the doc is rarely that clear); more than four is usually a sign the doc is too immature to break down and you should say so. See the guidance below on what makes a question worth asking.

Wait for the user's answers (or for them to say "use your judgment") before moving to Phase 2.

### What a good clarifying question looks like

A clarifying question is worth asking only if the answer would change the breakdown. Two tests:

1. **Would the story list look different depending on the answer?** If both answers produce the same stories, don't ask.
2. **Can you answer it yourself from the doc or the repo?** If yes, do that instead.

Useful question categories — pick from these rather than asking generic "what's your goal":

- **Scope boundary**: "The doc mentions caching but doesn't say if the cache invalidation strategy is part of this work or follow-up. Which?"
- **Non-functional requirements that drive design**: "Is this expected to handle the current ~50 req/s, or are we sizing for the projected 5k req/s? That changes whether we need the queue."
- **Existing system contract**: "The doc assumes `UserService.getById` is idempotent. I checked the code and it isn't — should we fix that as part of this work or work around it?"
- **Stakeholder/ordering**: "Does the migration story need to land before the new endpoint, or can they ship in parallel behind a flag?"
- **Definition of done**: "Is 'observability' satisfied by structured logs, or do you want metrics + dashboards too?"

### What pushback looks like in Phase 1

Pushback is not refusal. It's surfacing a concern, naming it, and proposing how to handle it. Examples:

> "The design assumes we already have a feature flag system, but I don't see one in the repo. Three options: (a) add 'introduce feature flags' as a prerequisite epic, (b) ship behind an env var for v1, (c) you tell me there's one I missed. Which?"

> "Sections 3 and 5 contradict each other on whether the API is sync or async. I'll need that resolved before I can break this down — async vs sync changes the story list materially."

> "This reads more like a problem statement than a design — there's no proposed solution yet, just goals. I can either break down the goals as discovery stories (spikes), or we can hold off until the design proposes an approach. Preference?"

---

## Phase 2: Propose the split

Now decide the shape, present it, and **stop**.

### Epic vs. multi-epic decision

Default to **one epic**. Reach for multiple epics only when at least one of these is true:

- The work spans clearly **separable value streams** that could be released independently (e.g., "new admin UI" + "billing pipeline rework" — same doc, different value).
- Different **stakeholders or teams** own different chunks.
- The timeline is long enough (multiple quarters) that grouping under one epic loses meaning.
- One chunk is a **prerequisite** that delivers standalone value (e.g., "introduce feature flag system" before "ship gated features").

If you're tempted by multiple epics just because the doc is long, that's not a good enough reason — long doc, one epic, many stories is fine.

### Sizing stories

A good story is roughly **1–3 days of focused work for one engineer** (M on the scale below), has a single coherent goal, and can be demoed independently. S (≤1 day) is fine in moderation but usually folds into a neighbour. L (3–5 days) is a soft smell — it's allowed when the work genuinely doesn't split, but ask yourself whether it should be two stories before settling on L. Rough heuristics for "this is too big":

- **Acceptance criteria > 7 items**: probably two stories.
- **Title contains "and"**: suspect compound. "Add caching and update docs" → two stories.
- **Touches > 2 major subsystems**: consider splitting along the subsystem seam.
- **Mixes build + migrate** ("build new flow and migrate old data"): almost always split.
- **First AC is "investigate / spike / decide"**: that's a spike story on its own; the build story comes after.

### What to output in Phase 2

Keep it lean — titles and one-line summaries, not full stories yet. Format:

```markdown
## Proposed breakdown

**Epic: <name>** — <one-sentence goal>

Stories:
1. **<Story title>** — <one line: what it delivers>
2. **<Story title>** — <one line: what it delivers>
...

Execution plan (waves of work that can run in parallel):
- **Wave 1** (no prerequisites): 01, 02, 03
- **Wave 2** (after 01): 04, 05
- **Wave 3** (after 04 + 05): 06

Critical path: 01 → 04 → 06. Everything else has slack.

*(Skip the execution plan section if there are ≤4 stories or they all sit in a single wave — the story list already conveys it. Include it whenever there's non-trivial parallelism worth surfacing.)*

## Concerns / pushback
- <thing that worries me about this design or breakdown>
- <thing I had to assume; flag it>

## Open questions still outstanding
- <anything the user hasn't answered yet that you proceeded on a best-guess for>

## Confirm or revise?
Reply with confirmation, edits ("merge 2 and 3", "split 4 into two"), or "go" / "looks good" and I'll expand each story to full detail.
```

**Then stop.** Do not start expanding. The gate exists because expansion is the expensive part — both in tokens and in the user's reviewing time.

### Pushback heuristics (use these in Phase 2)

Surface any of these that apply. Don't editorialise; just name them.

- **Cyclic dependencies**: Story B needs Story A, Story A needs Story B. Impossible to sequence — flag and propose how to break the cycle.
- **Phantom systems**: The design references a service/API/library that doesn't exist in the repo and isn't called out as new work.
- **Vague acceptance**: The doc says things like "should be performant", "user-friendly", "secure". These aren't acceptance criteria. Either pin them down with the user or call them out as needing definition.
- **Hidden migrations**: Any design that changes a schema, an API contract, or a message format almost always implies a migration story. If the doc doesn't mention one, add it and flag.
- **Missing rollback story**: For risky changes (data migrations, auth, payments), there should be a way to undo. If the design has no rollback plan, surface it.
- **No observability story**: New code paths with no logging/metrics plan are a smell.
- **Untestable AC**: An acceptance criterion you can't write a test for is a criterion you can't verify. Flag.
- **Design assumes Claude knows business context** that isn't in the doc or the repo. Ask, don't invent.
- **False serialisation**: stories listed in order but with no real dependencies between them. If 01, 02, and 03 touch independent files and nothing in 02 relies on 01 having shipped, say so — these can run in parallel and probably should.

---

## Phase 3: Expand confirmed stories

Only enter this phase after the user has confirmed (or revised) the Phase 2 outline.

### Where the files go

In Claude Code, default to a `breakdown/` directory at the repo root (create it if missing):

```
breakdown/
├── epic.md              # or epic-<slug>.md, one file per epic
├── 01-<story-slug>.md
├── 02-<story-slug>.md
└── ...
```

Number stories in a sensible topological order (`01-`, `02-`, …) so the directory listing roughly reads as a plan — but the numbers are only for sort-order, not a mandate to ship serially. The real dependency information lives in each story's `Blocks on` / `Coordinates with` fields, and the epic's execution plan summarises which stories can run in parallel. If the user prefers a single combined file or a different location, honour that — ask once if unclear.

### Epic template

```markdown
# Epic: <name>

## Goal
<One paragraph. What outcome does this enable, for whom, and why now?>

## Scope
**In scope:**
- <bullet>

**Out of scope:**
- <bullet — be specific; "future work" is not a scope boundary>

## Success criteria
- <Observable, measurable signal that this epic is done. Not "users are happy" — something like "p95 latency for endpoint X under 200ms" or "admin can complete flow Y end-to-end without dev intervention".>

## Stories
1. [<title>](./01-<slug>.md)
2. [<title>](./02-<slug>.md)
...

## Execution plan
Carry over the wave structure from Phase 2. Each wave lists stories that can be picked up in parallel.

- **Wave 1**: 01, 02, 03
- **Wave 2** (after 01): 04, 05
- **Wave 3** (after 04 + 05): 06

Critical path: 01 → 04 → 06.

## Risks & open questions
- <risk or question that survived Phase 1>

## Links
- Design doc: <path or URL>
- Related ADRs, prior epics, etc.
```

### Story template

```markdown
# <NN>. <Story title>

**Epic:** <epic name>
**Size:** S | M | L  (rough: S ≤ 1 day, M ≈ 1–3 days, L ≈ 3–5 days — anything bigger should have been split)
**Blocks on:** <story numbers that must be *merged* before this can start, or "none">
**Coordinates with:** <story numbers that touch overlapping code or contracts — can be done in parallel but pickers should talk, or "none">

## Context
<2–4 sentences. Why this story exists, what it unlocks. Link to the relevant section of the design doc.>

## Acceptance criteria
Written so each item is independently testable — this section *is* the test plan. Prefer Given/When/Then when behaviour-oriented; bullet list when structural. If an item can't be turned into a test, it doesn't belong here.

- [ ] <criterion>
- [ ] <criterion>
- [ ] <criterion>

## Technical notes
- <file/module to change, e.g. `services/billing/charge.py`>
- <library or API to use, with version if it matters>
- <gotcha worth flagging — e.g., "the existing `retry_with_backoff` helper does not handle 429s; check before reusing">

## Out of scope
- <thing a reader might assume is part of this story but isn't>

## Definition of done
Release-process checks only — *what it does* belongs in acceptance criteria, not here. Use whichever apply:

- [ ] Merged to main (behind <flag name> / not behind a flag)
- [ ] Deployed to <env>
- [ ] Docs updated (<which docs>)
- [ ] Metrics / dashboards in place
- [ ] Migration applied in <env>
- [ ] Stakeholder notified

## Open questions
- <anything still unresolved; if none, delete this section>
```

A few notes on filling the template:

- **"As a <role>, I want <thing>, so that <reason>"** is optional. It's useful for product-facing stories and noise for "rename this internal interface". Use it where it earns its keep.
- **Technical notes should reference real things in the repo** — file paths, function names, existing patterns. This is where Phase 1 grounding pays off. If you don't have a specific note to make, leave the section out rather than padding it.
- **Acceptance criteria do the heavy lifting.** If everything else were stripped, good AC would still tell an engineer what to build. Spend the effort here.

### Final pass before handing back

Once the files are written, do a quick sanity pass:

- Read the AC for each story. Could you write a test for every item? If not, sharpen or flag.
- Check `Blocks on` forms a DAG, not a cycle. (`Coordinates with` is symmetric and doesn't need to.)
- Check the execution plan matches reality: if A blocks on B, A should not appear in an earlier wave than B.
- Sanity-check the critical path. If it's only one or two stories, most of the work is parallel — good. If it's a long chain with little parallelism, surface that — it may indicate over-coupling worth splitting differently.
- Check the union of all story scopes covers the epic scope — and that nothing is in two stories at once.
- Re-state any concerns from Phase 2 that the user didn't address, so they don't get lost.

Then present the files to the user with a one-line summary of what landed where.

---

## Optional: push to Jira

If the user wants tickets in Jira, see [references/jira-integration.md](references/jira-integration.md) for the detection and push workflow using the official Atlassian CLI (`acli`). Do not attempt this unless the user asks — creating tickets is a side effect that's hard to undo. The check is one command: `command -v acli`.
