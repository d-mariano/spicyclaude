---
name: breaking-down-design-docs
description: Breaks a technical design document into an epic (or several epics) and actionable user stories with acceptance criteria, dependencies, and explicit out-of-scope items. Use this whenever a user shares a design doc, RFC, technical spec, PRD, ADR, or implementation proposal and wants it turned into work items — tickets, Jira issues, Linear tickets, stories, sprint plans, or a "plan of attack". Trigger even when the user phrases it loosely, such as "help me plan this", "how should we build this", "split this up", or "what are the tickets". Always asks clarifying questions before proposing a split and pushes back on ambiguity, hidden assumptions, oversized stories, and impossible dependencies rather than producing busy-work tickets.
allowed-tools: Read Write Edit Glob Bash AskUserQuestion
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

Pushback is not refusal. It's surfacing a concern, naming it, and proposing how to handle it.

**When pushback has discrete options, use `AskUserQuestion`.** Scope boundaries, missing systems, contradictions, and prerequisite decisions all have a finite option set — route them through `AskUserQuestion` so the user sees structured choices with trade-offs. Every option's description includes a counter: `"<implication> · Counter: <trade-off or objection>"`. Mark one "(Recommended)" when evidence clearly favors it; that option gets the strongest counter.

Examples of pushback that should go through `AskUserQuestion`:
- The design assumes a system that doesn't exist in the repo — options: add as prerequisite epic, work around it, or the user points you to it.
- The design contradicts itself on a decision that changes the story list — options: which reading governs.
- The doc is a problem statement, not a design — options: break down as discovery spikes, or hold off.

**Open-ended clarifications stay conversational.** Questions like "is this expected to handle 50 req/s or 5k?" or "does the migration need to land before the new endpoint?" are better asked in plain text — the answer space is too open for structured options.

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

### Pick the right ticket type per item

A **Story** is any item with an identifiable consumer — an end user, an API caller, a downstream service, or a future engineer writing against a new contract. If you can write an AC in the shape "When `<consumer>` does `<X>`, they observe `<Y>`", it's a Story. Most items in a technical design breakdown are Stories, because most items introduce or change a contract surface (a gRPC method, a REST endpoint, a webhook route, a Pub/Sub topic schema, a per-tool extension point) and have at least one calling service as the consumer.

A **Task** has no externally observable consumer surface: Terraform infrastructure, internal refactors with identical request/response shape (worker-class flips, framework upgrades), shared internal helpers used only by sibling stories in the same service, build/CI tweaks, pure deletion.

A **Spike** is research with a binary outcome (graduate / pivot / abandon), not deliverable work. Use **Bug** for defects, **Epic** for the epic you're rolling up to.

Defaulting every item to "Task" because it lacks an end-user surface is the wrong reflex — it loses the contract-observation framing that makes the ACs externally verifiable. When unsure, ask: "Can I write an AC starting with 'When `<some consumer>` does X, they observe Y'?" If yes, Story. If no, Task.

### Ticket structure

Use the per-type template from `~/.claude/skills/writing-tickets/` — `task.md`, `story.md`, `spike.md`, `bug.md`, `epic.md`. Each file has the canonical section structure (`# Summary`, `# Acceptance Criteria`, `# Out of Scope`, `# Engineering Notes`), the per-type Refinement Check, and worked examples. Read the file for each type you'll emit before drafting.

Add **on top** of that template a YAML frontmatter block carrying the breakdown-specific metadata. Then the publishable body — first H1 is the ticket title, no `NN.` prefix (sort-order lives in the filename, not the title):

```markdown
---
breakdown_id: "<NN>"
type: story            # epic | story | task | spike | bug
size: M                # S ≤ 1 day, M ≈ 1–3 days, L ≈ 3–5 days — anything bigger should have been split
blocks_on: ["01"]      # breakdown_ids that must be MERGED before this can start; [] if none
coordinates_with: ["03", "06"]  # breakdown_ids that touch overlapping code/contracts; [] if none
---
# <Ticket title>

# Summary
…
```

Everything below the frontmatter follows the per-type template as-is. Do not rename, reorder, or invent breakdown-specific variants.

**Frontmatter rules:**
- `breakdown_id` is the leading `NN[a-z]?` from the filename (e.g. `"06b"` for `06b-worker-safety-stack.md`). Quote it — bare `01` parses inconsistently across YAML libraries.
- `type` is lowercase. Maps directly to issue type at publish time.
- `size` is breakdown-time sizing only — never published as a Jira field; teams use their own estimation surfaces.
- `blocks_on` / `coordinates_with` reference other stories by `breakdown_id`. The epic is implicit (every child has the epic as parent) — never list it. Use `[]` for empty, not omission.
- The first `# H1` after the frontmatter is the publishable summary — write it as you want it to appear in the ticket tracker, no leading number.

**Body rules:**
- Self-contained. Don't write "see story 06b above" — that reference doesn't resolve in Jira / GitHub Issues / Linear. After the first publish, reference siblings by their tracker key (looked up in `jira-keys.md`) if needed.
- No prose duplication of frontmatter (e.g. don't restate "this story is blocked by 01" in the body — the frontmatter says so, the publisher will create the link).

### Run the per-type Refinement Check before declaring Phase 3 done

Each per-type file defines its own check (Story's is the most prescriptive; Task is lighter). Run the matching check per ticket. Don't skip — this is the moment that catches "I shipped 21 engineer-perspective ACs and called them user stories".

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

The epic file is the only one without a `breakdown_id` (nothing references it — children link via the publisher's `parent` field, not via `blocks_on`).

```markdown
---
type: epic
---
# <Epic name>

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

### Final pass before handing back

Once the files are written, do a quick sanity pass:

- **Run the per-type Refinement Check per ticket** (Story's is the most prescriptive; Task is lighter). This is the moment that catches "I shipped 21 engineer-perspective ACs and called them user stories".
- Read the AC for each ticket. Could you write a test for every item? If not, sharpen or flag.
- Check `Blocks on` forms a DAG, not a cycle. (`Coordinates with` is symmetric and doesn't need to.)
- Check the execution plan matches reality: if A blocks on B, A should not appear in an earlier wave than B.
- Sanity-check the critical path. If it's only one or two tickets, most of the work is parallel — good. If it's a long chain with little parallelism, surface that — it may indicate over-coupling worth splitting differently.
- Check the union of all ticket scopes covers the epic scope — and that nothing is in two tickets at once.
- Re-state any concerns from Phase 2 that the user didn't address, so they don't get lost.

Then present the files to the user with a one-line summary of what landed where.

---

## Optional: push to Jira

If the user wants tickets in Jira, there are two paths — both consume this skill's frontmatter contract and both write the same `jira-keys.md` map:

- **MCP batch flow (recommended default)** — [`~/.claude/skills/writing-tickets/references/breakdown-batch-publishing.md`](../writing-tickets/references/breakdown-batch-publishing.md). Use when the Atlassian MCP is authenticated; richer error handling, no shell dependency.
- **`acli` CLI flow** — [`references/jira-integration.md`](references/jira-integration.md). Use when the MCP isn't available, when the user prefers a scriptable flow, or in environments where MCP isn't reachable but `acli` is.

Both run a two-pass create-then-link cycle: Pass 1 creates the epic + children and captures keys to `jira-keys.md`; Pass 2 applies `Blocks` (from `blocks_on`) and `Relates` (from `coordinates_with`) links using the captured map.

Do not push to any tracker unless the user asks — creating tickets is a side effect that's hard to undo.
