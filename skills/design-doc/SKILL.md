---
name: design-doc
description: "Create a technical design document from a PRD interactively. Walks tdd-[nnn].md section-by-section, then a contracts-[nnn].md companion for field-level wire shapes — surfacing every choice via AskUserQuestion."
when_to_use: "User wants a technical design, TDD, system architecture, or design doc — or to turn a PRD into a design. Examples: 'design this system', 'create a TDD', 'write a design doc for X', 'architect this service', 'system design for the PRD', 'turn this PRD into a design'."
allowed-tools: Read Write Edit Glob AskUserQuestion
disable-model-invocation: true
argument-hint: "[task-slug]"
---

# Design Document Workflow

Produce a technical design document interactively from a PRD, supporting research, and optional technical artifacts. The output is an alignment artifact: it gets humans (and AI) agreeing on the shape of the system before code is written.

This workflow does not invent requirements. It synthesizes design from the inputs the user supplies, raises every choice that isn't already specified, and never makes silent assumptions on the user's behalf.

## Inputs

In priority order:

1. **PRD** (required) — problem statement, use cases, constraints, committed requirements. **Authoritative**: its decisions are baked in and not re-litigated.
2. **Research** (recommended) — prior art, technology comparisons, recommendations, alternatives. **Informational**: recommendations and alternatives feed `AskUserQuestion` options; user owns the decision.
3. **Technical artifacts** (optional) — code-as-design files: abstractions, contracts, type definitions, data models. Treat as **decided** for whatever they specify; cite them like a PRD section.

### Input modes

- **In context** — PRD/research/artifacts are already in the conversation. Use what's there; don't re-read.
- **On disk** — user supplied paths. Read each one in full.

If you can't tell which mode applies, ask via `AskUserQuestion`. If no PRD exists in either form, confirm via `AskUserQuestion` whether to proceed in **spike mode** (every requirement-shaped value becomes an Open Question with a working assumption instead of a concrete commitment — for exploration, not committed design).

## Critical Rules

1. **Don't fabricate.** Every value in the design must trace back to an input or to a user decision.
   - **No silent assumptions.** Every choice the user has not made must be either (a) sourced from PRD/research/artifacts, (b) raised via `AskUserQuestion` and decided in the relevant section, or (c) recorded as deferred with a working assumption the user explicitly accepts.
   - **Options come from given context only.** Don't draw on training-data preferences. If a decision needs an option set and the inputs don't suggest any, that's an unknown — flag it, don't invent options.
   - **Defer requires a working assumption.** A defer with no assumption is invalid; mark such questions blocking instead.
2. **Push back when something is unclear, contradictory, or risky.** If a user choice conflicts with an earlier section, contradicts the PRD, or seems insane given the inputs, surface the conflict before recording.
3. **Stay at alignment altitude.** Describe what the system is — components, contracts, data models, relationships. Code bodies, file-by-file responsibilities, build steps, and S/M/L estimates are out of scope.
4. **Name things concretely.** Every type, interface, function, and file must have a real name. "SomeService", "DataProcessor", "handleData" are banned.
5. **The design file must stand alone.** Anyone reading it cold must understand the system without the conversation.
6. **Save artifacts incrementally, never silently overwrite.** Build `/context/[nnn]-<slug>/tdd-[nnn].md` section-by-section as choices resolve. Workflow Step 0 covers what to do when files already exist.
7. **`AskUserQuestion` is the only sanctioned channel for design decisions.** Plain-text "which would you prefer?" prompts are not allowed for any decision that lands in `tdd-[nnn].md` or `contracts-[nnn].md`. Conversational follow-ups (e.g., when the user says "discuss further") and free-form interjections are fine.

## Mermaid rendering notes

- **Component & ER diagrams:** wrap `graph` / `flowchart` / `erDiagram` node labels in `"..."` when they contain anything beyond plain alphanumerics.
- **Style declarations:** setting `fill:` requires also setting `color:` and `stroke:`. A fill alone overrides only the background; text and border stay at theme defaults and lose contrast under the opposite theme. Example: `style NewService fill:#fff9c4,color:#1a1a1a,stroke:#666`.
- **Sequence diagrams (escape hatch only — Data Flow is text-by-default):** strict renderers (4.4+) tokenize arrow message text and break on `,` and `;`. Arrow messages must be short verb phrases — push payload shapes into `Note over X,Y:` blocks, and use `·`, `→`, or `<br/>` as separators inside notes (never commas).

## Surfacing Decisions to the User

Use `AskUserQuestion` whenever a decision needs the user's input. Rules:

- **Batch related questions** — up to 4 per call.
- **Provide 2-4 options per question.** Each option needs a one-line description of what choosing it implies.
- **Every option's description includes a counter.** Format: `"<implication> · Counter: <trade-off or objection>"`. Non-recommended options state the key cost or risk of that path. If an option has no real counter, it's either the obvious choice (why offer alternatives?) or the option set needs rework.
- **Mark research-recommended options** with "(research-rec)" in the label when research had a recommendation.
- **Mark your recommendation** with "(Recommended)" only when you have a clear, evidence-backed lean from the inputs — not absence of contrary signal. The recommended option gets the strongest counter — the primary reason the user might reject it. **Place the recommended option first** in the options array.
- **`header` is hard-capped at 12 characters.** Pick a short tag ("Auth method", "Storage", "Wire fmt"); don't write a sentence.
- **State which goal(s) the decision serves.** The question text must reference the PRD goal, NFR, use case, or related prior decisions in plain English (topic names, not codes). Example: `"Which tenant isolation mechanism? Addresses the PRD §6.4 high-priority NFR; bears on the throughput targets and the chosen architecture."` Keeps the user oriented to *why* the question matters.
- **Flag scope creep.** If any option (or research recommendation) addresses a non-goal (PRD §3) or out-of-scope item, mark it with "(addresses non-goal: <ref>)" in the label. The user must consciously accept scope creep.
- **Always offer a defer path** when the workflow can proceed with a working assumption. Phrase: `"Defer — proceed with: <concrete assumption>"`. If the design genuinely cannot proceed without the answer, mark the question blocking and don't offer defer.
- **Do not write open-ended prose questions.** If the answer space is open-ended, still propose 2-3 plausible options grounded in inputs plus a defer path; the tool surfaces a free-text input automatically.
- **Do NOT add an "Other" option.** The tool surfaces a free-text input automatically; adding "Other" wastes one of the 4 option slots.
- **Use `multiSelect: true`** when the choices are not mutually exclusive — e.g., "Which cross-cutting concerns apply?", "Which entities are PII-bearing?", "Which wire surfaces need this convention?". Default `false` for picking-one decisions.
- **Use the `preview` field for concrete-shape choices** (single-select only). When the user is comparing visual artifacts — directory layout variants, IDL shape alternatives, error-envelope JSON examples, sample request/response bodies — put an ASCII mockup or code snippet in each option's `preview` so the UI renders a side-by-side comparison. Skip preview for preference questions where label + description suffice. Previews are not supported for `multiSelect: true`.

After every `AskUserQuestion` answer, fill in the relevant section of the TDD with the chosen value. Add a one-line rationale next to the value where the rationale isn't obvious from the value itself. If the user deferred, also append a row to the Open Questions section.

## Push-Back Protocol

When something doesn't make sense, surface it before recording. Push-back uses `AskUserQuestion` like all other decision channels. Targets: prior sections of the TDD, the PRD, or the inputs themselves.

- **Contradicts an earlier section** — `"Your choice <X> conflicts with the <section>: <prior decision>. Which should govern?"` Options: keep prior, replace prior, both update (specify how).
- **Contradicts the PRD** — `"Your choice <X> conflicts with PRD §Y, which says <Z>. Confirm overriding the PRD?"` Options: stick with PRD, override (recorded as deviation), revise PRD before proceeding.
- **No support in inputs** — `"Your choice <X> isn't supported by the PRD or research. To record it, we need either (a) research that backs it, or (b) acceptance that this is a user-original choice."` Options: defer pending research, accept as user-original (with rationale), pick a different option grounded in inputs.
- **Insanely scoped or risky** — name the risk, cite the input that suggests it's risky, ask whether to proceed, scope down, or revisit.

---

## Workflow

Single interactive flow. Decisions surface as each section requires them. Pause for user input only via `AskUserQuestion`.

### Step 0: Setup

1. **Determine task slug.** If argument supplied, use it. Otherwise infer from PRD title or ask via `AskUserQuestion` with 2-3 candidate slugs derived from input filenames or content.
2. **Resolve feature folder.** Glob `/context/*-<slug>/` for an existing folder matching the slug.
   - **No match**: assign the next feature index by globbing `/context/[0-9][0-9][0-9]-*` and taking `max([nnn]) + 1`, zero-padded to 3 digits. Folder is `/context/[nnn]-<slug>/`. Create on first write.
   - **Single match**: reuse that folder.
   - **Multiple matches**: ask via `AskUserQuestion` which to use, including a "create new" option.
3. **Determine TDD index.** Glob `/context/[nnn]-<slug>/tdd-*.md`. The new design writes to `tdd-[next].md` where `[next] = max(existing) + 1`, zero-padded to 3 digits; first design is `tdd-001.md`. Existing TDDs are never overwritten — a new design always increments. The companion `contracts-[next].md` uses the matching index.
4. **Check for interrupted draft.** If the highest-numbered `tdd-[nnn].md` is incomplete (Status not `Ready for Review`, or required sections missing), ask via `AskUserQuestion`: **resume** that file from the next unwritten section, or **start fresh** at `tdd-[nnn+1].md`.
5. **Load inputs.**
   - If user provided paths: Read each in full.
   - If inputs are in context: use the conversation; don't re-read.
   - If no PRD is identifiable: confirm spike mode via `AskUserQuestion`. Spike mode uses the same `tdd-[nnn].md` path with `Status: Spike` in the header.

### Step 1: Walk Sections

Build `/context/[nnn]-<slug>/tdd-[nnn].md` section-by-section, in the order listed in the [Document Format](#document-format) section below.

For each section:

1. **Identify the decisions the section requires.** Pull from the PRD and artifacts first (those are decided). Pull from research where it offers a recommendation or option set. What's left needs the user.
2. **Surface unresolved decisions via `AskUserQuestion`** (batched up to 4 per call), grounded in inputs only. Apply the push-back protocol when needed.
3. **Write the section to the TDD** using the value chosen plus a one-line rationale where the rationale isn't obvious. If the user deferred (chose `"Defer — proceed with: <X>"`), use `<X>` as the working assumption in the section AND append a row to the Open Questions table at the bottom of the TDD.
4. **Move on.** Do not revisit a section unless push-back surfaces a contradiction.

The Architecture Overview is the first section with material decisions. Resolve the architectural choice in flow — it's the load-bearing decision everything else depends on, but it doesn't need its own ceremonial phase.

#### Diagram-shape decision (Architecture Overview)

When the inputs do not pin down a diagram shape, surface the choice via `AskUserQuestion` as part of the first batched call for Architecture Overview (do not make it a standalone interrupt). Diagram shape is a meta-decision about how the system is *communicated*; readers will internalize whichever frame you pick.

Use the `preview` field with ASCII mermaid mockups so the user sees the candidates side-by-side. Single-select. Candidates come from the inputs — typical option sets:

- **Layered** (e.g., API → Service → Data) — when the system has clear horizontal layers and data flows top-to-bottom.
- **Hexagonal / Ports-and-Adapters** — when the system has a stable core with multiple inbound/outbound adapters.
- **Event-driven / Pipeline** — when the system is dominated by async message flow.
- **Hub-and-spoke** — when one component coordinates many peripheral services.

Skip the question when the PRD, research, or artifacts already pin the shape (e.g., research recommends event-driven and the PRD's throughput target requires it).

#### Component naming decision

When ≥2 new component names land in a single Architecture Overview pass and they are not pinned by inputs (PRD didn't name them, no existing artifact defines them), batch a single `AskUserQuestion` call proposing 2-3 candidate names per component with a one-line rationale each. Names are sticky — they show up in code, tickets, runbooks, conversations — so this is worth asking even though it adds an interrupt.

When only one new component name is unpinned, the model may name it and note the choice in Key Decisions without asking. When all component names are pinned by inputs, skip.

### Step 2: Contracts Walk

Build `/context/[nnn]-<slug>/contracts-[nnn].md` — a companion file carrying field-level wire shapes (IDL, request/response bodies, error envelopes, document schemas, configuration). The TDD stays at alignment altitude per Critical Rule 3; the contracts file is where the field-level detail lives.

**Skip path.** Begin Step 2 by asking via `AskUserQuestion` whether contracts are needed. Skip when the design only edits an existing surface (no new IDL, no new endpoints, no new event payloads), or when the work is scoped to UI-only changes against a stable API. When skipping, jump straight to Step 3.

When walking:

1. **Wire conventions first.** Surface the cross-cutting decisions that govern every subsequent contract section as a single batched `AskUserQuestion` call. Derive which conventions are needed from the wire surfaces present in the TDD's Architecture Overview and Public Contract bullets — do not pre-enumerate.
2. **Walk each contract surface** named in the TDD's Public Contract bullets, one section per surface. For each, identify decisions the design and inputs don't pin down, batch them via `AskUserQuestion` (≤4 per call), then write the section.
3. **Push-back protocol still applies.** Contradictions with the TDD surface here often — writing field shapes forces architectural questions the alignment altitude lets you skate past. When a contract issue reveals a design issue, raise it via `AskUserQuestion` and fix at the design layer first; then pin the contract.
4. **No invented fields.** Every field comes from PRD, the TDD, decisions register, or `AskUserQuestion`. If it can't be sourced, ask.
5. **One naming convention per wire surface.** Mixed casing within a single surface is a bug.

Output file header:

```
# <Title> — Contracts
**Version:** 1.0 | **Date**: YYYY-MM-DD | **Status**: Draft

> Companion to [`tdd-[nnn].md`](./tdd-[nnn].md). Decision provenance in [`decisions.md`](./decisions.md) (if used).
```

### Step 3: Final Pass

1. **Read the TDD and contracts file end-to-end.** Check for contradictions across sections AND across the two files (counts, names, references must agree). Examples: feature X is in v1 in TDD section A but deferred in section B; component picks technology T while another section requires not-T; the Walking Skeleton claims a property the Component Outlines don't deliver; an RPC method count in the TDD's Public Contract disagrees with the IDL in the contracts file. For each contradiction, raise an `AskUserQuestion` to reconcile.
2. **Populate the Key Decisions section** at the end of the TDD (above Open Questions). One bulleted line per choice the user made via `AskUserQuestion`. Do not list values that came directly from the PRD — those are already cited where they appear. Include contract-level decisions (wire conventions, IDL shape choices, error semantics) alongside design-level ones.
3. **Confirm the Open Questions section** captures every deferral with a concrete working assumption (Critical Rule 1).
4. **Update both file headers** with final Status (`Ready for Review`) and date.
5. **Present the summary**: paths to the TDD and contracts file (if written), a brief diagram inventory, and the Key Decisions and Open Questions sections inline for quick review.

---

## Document Format

`/context/[nnn]-<slug>/tdd-[nnn].md` follows this exact structure. Decisions are recorded by the value they produce; rationale lives next to the value where useful, plus a one-line summary in Key Decisions.

````markdown
# <Title>
**Version:** 1.0 | **Date**: YYYY-MM-DD | **Status**: Draft | Ready for Review

## Goal
<3-5 sentences: what this system does, what problem it solves, what "done" looks like. Cite the PRD for the problem statement. If the PRD is only in context (no §), confirm phrasing via AskUserQuestion.>

## Architecture Overview
<Single Mermaid component diagram showing system-level relationships:
- Each top-level component as a node with one-line responsibility
- Communication patterns labeled (sync/async, protocol, data format)
- Data stores and owning components
- External integrations
- Subgraphs for layers / bounded contexts
- Internals of complex components are NOT in this diagram — they get their own sub-component diagram in the per-component section below.>

This is the alignment-critical view. If a reader can't grasp the system from this one diagram + the Goal, the architecture is too complex or the diagram is wrong.

### [Component Name]
<One H3 per top-level component. Required H4s: Responsibility, Technology, Key Abstractions, Public Contract. Optional: Internal Structure.>

#### Responsibility
<One sentence.>

#### Technology
<Specific framework, library, or tool.>

#### Key Abstractions
<The 2-5 most important types/classes/modules — name + one-line role each. Full type signatures go in the contracts file, not here.>

#### Public Contract
<Bullet the contract style and the cross-component contracts that matter for coupling. Field-level shapes go in the contracts file, not here.
- **Inbound:** <protocol, surface area in one phrase>
- **Outbound:** <protocol, named contracts + consumers>
- **Invariants:** <design-level guarantees only>>

#### Internal Structure
<Only populate if the component has multiple obvious sub-modules. Name them with a one-line role each, and include a Mermaid sub-diagram if the relationships aren't obvious from the names. Omit this H4 otherwise.>

## Data Flow
<For each primary use case from the PRD, write ordered text steps. Each flow needs a happy path plus at least one named failure mode. Mark async boundaries inline (e.g., "→ async via <queue>") and call out data transformations. Reserve Mermaid sequence diagrams for genuinely complex parallel/async flows where text gets tangled.

### Use case: <name from PRD>
**Happy path:**
1. <Component> <action> → <next component>
2. ...

**Failure: <named failure mode>**
1. ...>

## Data Model
<- Entities with the fields that carry architectural weight: PRD-named fields, PII / compliance-sensitive fields, foreign keys, and fields that drive storage choices (large blobs, encrypted columns) or access patterns (indexed / queried). Skip incidental fields (`created_at`, surrogate IDs, descriptive strings) — those are planning territory.
- Relationships shown explicitly (1:1, 1:N, M:N).
- Mermaid ER diagram if 3+ entities with relationships.
- Note which component owns each entity.>

## Directory Structure
<Top-level project structure showing modules / layers / bounded contexts, with one-line annotations on each:>

```
project-root/
├── src/
│   ├── module/            # purpose
│   └── another-module/    # purpose
```

<Show one level deep, occasionally two. Do not enumerate individual files. Justify the structure: framework conventions, domain boundaries, or layer separation.>

## Cross-Cutting Concerns
<One line per concern stating the decision, not the design space. Skip with a one-line note if not applicable.
- **Errors:** <where caught, how propagated, user-facing vs. internal split>
- **Auth:** <where enforced, how identity flows>
- **Observability:** <log format, trace propagation, key metrics>
- **Config:** <load order, env overrides, secrets handling>>

## Walking Skeleton Requirements
<The thinnest possible end-to-end slice through the system — expressed as requirements, not implementation:
- Use case it covers (one of the primary use cases from the PRD)
- What it must prove about the architecture
- The success assertion (the observable condition that means the slice works)

**Surface the slice via `AskUserQuestion`.** Multiple valid slices typically exist (auth-only path, single happy-path use case, read-only slice, write-only slice). The slice the user picks becomes Phase 1 of implementation, so this is a load-bearing choice — do not pick silently. Propose 2-4 candidates derived from the PRD's primary use cases. Each option's description states what the slice proves about the architecture (the value) and what it leaves untested (the counter).>

This becomes Phase 1 of implementation.

## Implementation Phases
<Ordered phases serving as both a dependency map and epic/story candidates. Each phase:
- Name
- Deliverable (what exists when this phase is done)
- Dependencies (which prior phases must be complete, and *why architecturally*)
- Done condition (the observable condition that means the phase is complete)

Phase 1 is always the Walking Skeleton.

**Surface the phase-split strategy via `AskUserQuestion` with `preview`** before drafting phases. Different teams have strong preferences and the resulting phase lists differ materially. Single-select. Candidate strategies:

- **Vertical slices** — each phase delivers one end-to-end use case fully working.
- **Horizontal layers** — each phase delivers one layer (data → service → API) across all use cases.
- **Hybrid** — Walking Skeleton (vertical) → core infrastructure (horizontal) → feature slices (vertical).

Each option's `preview` shows the resulting phase list as a short ASCII outline so the user can compare shapes. Skip when the PRD or research pins the strategy.

Excluded (planning territory): complexity estimates (S/M/L), per-phase risks, time/effort estimates, owner assignments, ticket numbers.>

## Key Decisions
<Flat bulleted list — one line per choice the user made via AskUserQuestion during the walk. Format:
- **<topic 2-4 words>**: <choice>. <one-sentence rationale>.

Do NOT list values that came directly from the PRD — those are already cited where they appear in the relevant section.>

## Open Questions & Deferred Decisions
| Question | Working Assumption | Resolve By |

<One row per deferred item. Every row must have a concrete working assumption — defer with no assumption is invalid (Critical Rule 1).>
````
