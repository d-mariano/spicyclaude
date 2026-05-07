---
name: design-doc
description: "Create a technical design document from a PRD interactively. Walks design.md section-by-section, surfacing every choice via AskUserQuestion. Decisions live where they apply — no parallel register, no inline ID tags. Strict no-assumptions rule — unknowns become Open Questions with working assumptions, not silent defaults."
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

1. **No silent assumptions.** Every choice the user has not made must be either (a) sourced from PRD/research/artifacts, (b) raised via `AskUserQuestion` and decided in the relevant section, or (c) recorded as deferred with a working assumption the user explicitly accepts. Never invent a default and proceed.
2. **Recommendations come from given context only.** Don't draw on training-data preferences. If a decision needs an option set and the inputs don't suggest any, that's an unknown — flag it, don't invent options.
3. **Push back when something is unclear, contradictory, or risky.** If a user choice conflicts with an earlier section, contradicts the PRD, or seems insane given the inputs, surface the conflict before recording.
4. **Defer is valid only with a working assumption.** A defer with no assumption is invalid; mark such questions blocking instead.
5. **Stay at alignment altitude.** Describe what the system is — components, contracts, data models, relationships. Code bodies, file-by-file responsibilities, build steps, and S/M/L estimates are out of scope.
6. **Name things concretely.** Every type, interface, function, and file must have a real name. "SomeService", "DataProcessor", "handleData" are banned.
7. **The design file must stand alone.** Anyone reading it cold must understand the system without the conversation.
8. **Save artifacts incrementally.** Build `docs/design/<task-slug>/design.md` section-by-section as choices resolve. If the directory already has files, ask via `AskUserQuestion`: resume, restart (overwrite — confirm), or pick a new slug. Never silently overwrite.
9. **`AskUserQuestion` is the only sanctioned channel for design decisions.** Plain-text "which would you prefer?" prompts are not allowed for any decision that lands in `design.md`. Conversational follow-ups (e.g., when the user says "discuss further") and free-form interjections are fine.
10. **Mermaid sequence-diagram guardrails.** Strict renderers (4.4+) tokenize arrow message text and break on `,` and `;`:
    - Arrow messages (`->>`, `-->>`, `->`, `-->`) must be short verb phrases — no `,`, `;`, multi-statement SQL, or JSON shapes.
    - Push column lists, payload shapes, and SQL into `Note over X,Y:` blocks.
    - Use `·`, `→`, or `<br/>` as separators inside notes — never commas.
    - Wrap `graph` / `flowchart` / `erDiagram` node labels in `"..."` when they contain anything beyond plain alphanumerics.
    - **Setting `fill:` requires also setting `color:` and `stroke:`.** A fill alone overrides only the background; text and border stay at theme defaults and lose contrast under the opposite theme. Example: `style NewService fill:#fff9c4,color:#1a1a1a,stroke:#666`.

## Surfacing Decisions to the User

Use `AskUserQuestion` whenever a decision needs the user's input. Rules:

- **Batch related questions** — up to 4 per call.
- **Provide 2-4 options per question.** Each option needs a one-line description of what choosing it implies.
- **Mark research-recommended options** with "(research-rec)" in the label when research had a recommendation.
- **Mark your recommendation** with "(Recommended)" only when you have a clear, evidence-backed lean from the inputs — not absence of contrary signal. When you do mark Recommended, the option's description **must include the strongest single argument against it**. Format: `"<implication> · Counter: <strongest objection>"`. If no real counter exists, the alternatives are probably weak — rework the option set.
- **State which goal(s) the decision serves.** The question text must reference the PRD goal, NFR, use case, or related prior decisions in plain English (topic names, not codes). Example: `"Which tenant isolation mechanism? Addresses the PRD §6.4 high-priority NFR; bears on the throughput targets and the chosen architecture."` Keeps the user oriented to *why* the question matters.
- **Flag scope creep.** If any option (or research recommendation) addresses a non-goal (PRD §3) or out-of-scope item, mark it with "(addresses non-goal: <ref>)" in the label. The user must consciously accept scope creep.
- **Always offer a defer path** when the workflow can proceed with a working assumption. Phrase: `"Defer — proceed with: <concrete assumption>"`. If the design genuinely cannot proceed without the answer, mark the question blocking and don't offer defer.
- **Do not write open-ended prose questions.** If the answer space is open-ended, still propose 2-3 plausible options grounded in inputs plus a defer path; the user can override via "Other".

After every `AskUserQuestion` answer, fill in the relevant section of `design.md` with the chosen value. Add a one-line rationale next to the value where the rationale isn't obvious from the value itself. If the user deferred, also append a row to the Open Questions section.

## Push-Back Protocol

When something doesn't make sense, surface it before recording. Push-back uses `AskUserQuestion` like all other decision channels. Targets: prior sections of `design.md`, the PRD, or the inputs themselves.

- **Contradicts an earlier section** — `"Your choice <X> conflicts with the <section>: <prior decision>. Which should govern?"` Options: keep prior, replace prior, both update (specify how).
- **Contradicts the PRD** — `"Your choice <X> conflicts with PRD §Y, which says <Z>. Confirm overriding the PRD?"` Options: stick with PRD, override (recorded as deviation), revise PRD before proceeding.
- **No support in inputs** — `"Your choice <X> isn't supported by the PRD or research. To record it, we need either (a) research that backs it, or (b) acceptance that this is a user-original choice."` Options: defer pending research, accept as user-original (with rationale), pick a different option grounded in inputs.
- **Insanely scoped or risky** — name the risk, cite the input that suggests it's risky, ask whether to proceed, scope down, or revisit.

---

## Workflow

Single interactive flow. Decisions surface as each section requires them. Pause for user input only via `AskUserQuestion`.

### Step 0: Setup

1. **Determine task slug.** If argument supplied, use it. Otherwise infer from PRD title or ask via `AskUserQuestion` with 2-3 candidate slugs derived from input filenames or content.
2. **Check for existing artifacts.** Glob `docs/design/<task-slug>/`. If files exist, ask via `AskUserQuestion`: resume (read existing `design.md` and continue from the next unwritten section), restart (confirm overwrite), or pick a new slug.
3. **Load inputs.**
   - If user provided paths: Read each in full.
   - If inputs are in context: use the conversation; don't re-read.
   - If no PRD is identifiable: confirm spike mode via `AskUserQuestion`.

### Step 1: Walk Sections

Build `docs/design/<task-slug>/design.md` section-by-section, in the order listed in the [Document Format](#document-format) section below.

For each section:

1. **Identify the decisions the section requires.** Pull from the PRD and artifacts first (those are decided). Pull from research where it offers a recommendation or option set. What's left needs the user.
2. **Surface unresolved decisions via `AskUserQuestion`** (batched up to 4 per call), grounded in inputs only. Apply the push-back protocol when needed.
3. **Write the section to `design.md`** using the value chosen plus a one-line rationale where the rationale isn't obvious. If the user deferred (chose `"Defer — proceed with: <X>"`), use `<X>` as the working assumption in the section AND append a row to the Open Questions table at the bottom of `design.md`.
4. **Move on.** Do not revisit a section unless push-back surfaces a contradiction.

The Architecture Overview is the first section with material decisions. Resolve the architectural choice in flow — it's the load-bearing decision everything else depends on, but it doesn't need its own ceremonial phase.

### Step 2: Final Pass

1. **Read `design.md` end-to-end.** Check for contradictions across sections that batched section-by-section work can produce. Examples: feature X is in v1 in section A but deferred in section B; component picks technology T while another section requires not-T; the Walking Skeleton claims a property the Component Outlines don't deliver. For each contradiction, raise an `AskUserQuestion` to reconcile.
2. **Populate the Key Decisions section** at the end of `design.md` (above Open Questions). One bulleted line per choice the user made via `AskUserQuestion`. Do not list values that came directly from the PRD — those are already cited where they appear.
3. **Confirm the Open Questions section** captures every deferral with a concrete working assumption (Critical Rule 4).
4. **Update the document header** with final Status (`Ready for Review`) and date.
5. **Present the summary**: path to `design.md`, diagram count (`"1 overview + N data flow + (optional ER) + N sub-component = K diagrams"`), and the Key Decisions and Open Questions sections inline for quick review.

---

## Document Format

`docs/design/<task-slug>/design.md` follows this exact structure. **Do not include inline decision IDs (no `[D###]` tags or similar) in any section.** Decisions are recorded by the value they produce; rationale lives next to the value where useful, plus a one-line summary in Key Decisions.

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
<One H3 per top-level component. Each H4 below is required.>

#### Responsibility
<One sentence.>

#### Technology
<Specific framework, library, or tool.>

#### Key Abstractions
<The 2-5 most important types/classes/modules with type signatures or interface definitions — the contract surface, not the implementation.>

#### Public Contract
<How other components interact with this one:
- Function/method signatures with full type annotations
- HTTP endpoints (method, path, request/response/error shapes)
- Event schemas (name, payload type)
- gRPC/GraphQL definitions if applicable>

#### Sub Components
<Only populate if the component has multiple obvious sub-modules. Otherwise omit this H4.>

#### Diagram
<Only populate if Sub Components is populated. Show internal modules / layers / responsibilities and the contracts re-exposed back to the overview. Otherwise omit this H4.>

## Data Flow
<For each primary use case from the PRD:
- Mermaid sequence or flow diagram
- Happy path with all components involved
- At least one error/failure path per flow
- Mark async boundaries and data transformations.>

## Data Model
<- Type definitions for each entity (the shape, not the storage schema)
- Relationships shown explicitly (1:1, 1:N, M:N)
- Mermaid ER diagram if 3+ entities with relationships
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
<Include only if applicable (skip with a one-line note if not):
- Error handling strategy (propagation, type hierarchy, user-facing vs. internal)
- Auth (where enforced, how identity flows)
- Logging & observability (format, trace propagation, key metrics)
- Configuration (loading, env overrides, secrets)>

## Walking Skeleton Requirements
<The thinnest possible end-to-end slice through the system — expressed as requirements, not implementation:
- Use case it covers (one of the primary use cases from the PRD)
- What it must prove about the architecture
- The success assertion (the observable condition that means the slice works)>

This becomes Phase 1 of implementation.

## Implementation Phases
<Ordered phases serving as both a dependency map and epic/story candidates. Each phase:
- Name
- Deliverable (what exists when this phase is done)
- Dependencies (which prior phases must be complete, and *why architecturally*)
- Done condition (the observable condition that means the phase is complete)

Phase 1 is always the Walking Skeleton. Include a Mermaid Gantt chart — primary purpose is showing dependency relationships and natural slicing, not durations.

Excluded (planning territory): complexity estimates (S/M/L), per-phase risks, time/effort estimates, owner assignments, ticket numbers.>

## Key Decisions
<Flat bulleted list — one line per choice the user made via AskUserQuestion during the walk. Format:
- **<topic 2-4 words>**: <choice>. <one-sentence rationale>.

Do NOT list values that came directly from the PRD — those are already cited where they appear in the relevant section.>

## Open Questions & Deferred Decisions
| Question | Working Assumption | Resolve By |

<One row per deferred item. Every row must have a concrete working assumption — defer with no assumption is invalid (Critical Rule 4).>
````
