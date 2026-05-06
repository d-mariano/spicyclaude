---
name: design-doc
description: "Create a technical design document from a PRD interactively. Synthesizes PRD, research, and optional technical artifacts into design.md at docs/design/<task-slug>/, plus a parallel Decision Register that records the source for every choice (PRD, research, artifact, or user gate). Strict no-assumptions rule — unknowns become Open rows, not silent defaults. AskUserQuestion-driven; no web research."
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
2. **Research** (recommended) — prior art, technology comparisons, recommendations, alternatives. **Informational**: recommendations and alternatives feed `AskUserQuestion` options; user owns the decision via a gate.
3. **Technical artifacts** (optional) — code-as-design files: abstractions, contracts, type definitions, data models. Treat as **decided** for whatever they specify; cite them like a PRD section.

### Input modes

- **In context** — PRD/research/artifacts are already in the conversation. Use what's there; don't re-read.
- **On disk** — user supplied paths. Read each one in full.

If you can't tell which mode applies, ask via `AskUserQuestion`. If no PRD exists in either form, confirm via `AskUserQuestion` whether to proceed in **spike mode** (every requirement-shaped row becomes Open instead of Decided — for exploration, not committed design).

## Critical Rules

1. **No silent assumptions.** Every choice the user has not made must be either (a) sourced from PRD/research/artifacts, (b) raised via `AskUserQuestion` and Decided, or (c) recorded as Deferred with a working assumption the user explicitly accepts. Never invent a default and proceed.
2. **Recommendations come from given context only.** Don't draw on training-data preferences. If a decision needs an option set and the inputs don't suggest any, that's an unknown — flag it, don't invent options.
3. **Push back when something is unclear, contradictory, or risky.** If a user choice conflicts with a prior register row, contradicts the PRD, or seems insane given the inputs, surface the conflict before recording.
4. **Defer is valid only with a working assumption.** A defer with no assumption is invalid; mark such questions blocking instead.
5. **Stay at alignment altitude.** Describe what the system is — components, contracts, data models, relationships. Code bodies, file-by-file responsibilities, build steps, and S/M/L estimates are out of scope.
6. **Name things concretely.** Every type, interface, function, and file must have a real name. "SomeService", "DataProcessor", "handleData" are banned.
7. **The design file must stand alone.** Anyone reading it cold must understand the system without the conversation.
8. **Save artifacts incrementally.** Decision Register at `docs/design/<task-slug>/decisions.md` from the moment it's seeded. Design document at `docs/design/<task-slug>/design.md` built incrementally as sections resolve. If the directory already has files, ask via `AskUserQuestion`: resume, restart (overwrite — confirm), or pick a new slug. Never silently overwrite.
9. **`AskUserQuestion` is the only sanctioned channel for register decisions.** Plain-text "which would you prefer?" prompts are not allowed for any decision that lands in the register. Conversational follow-ups (e.g., when the user says "discuss further") and free-form interjections are fine.
10. **Mermaid sequence-diagram guardrails.** Strict renderers (4.4+) tokenize arrow message text and break on `,` and `;`:
    - Arrow messages (`->>`, `-->>`, `->`, `-->`) must be short verb phrases — no `,`, `;`, multi-statement SQL, or JSON shapes.
    - Push column lists, payload shapes, and SQL into `Note over X,Y:` blocks.
    - Use `·`, `→`, or `<br/>` as separators inside notes — never commas.
    - Wrap `graph` / `flowchart` / `erDiagram` node labels in `"..."` when they contain anything beyond plain alphanumerics.

## The Decision Register

Maintain `docs/design/<task-slug>/decisions.md` from setup onward. Single source of truth for what got decided, by whom, why, and **where the decision came from**. Append-only — once a row is logged, only Status, Resolution, and Resolved fields may change (Open → Decided or Open → Deferred).

Format:

```markdown
| ID | Topic | Status | Resolution | Rationale | Source | Raised | Resolved |
|----|-------|--------|------------|-----------|--------|--------|----------|
| D001 | Throughput target | Decided | 10k jobs/sec at launch | Stakeholder commitment | PRD §3.1 | seed | seed |
| D002 | Architecture | Decided | Event-driven (option B) | Matches throughput target; team has Kafka experience | gate (research-rec) | seed | step-2 |
| D003 | Auth provider | Decided | Cognito | AWS shop alignment; user picked over research's Auth0 rec | gate (user-override) | seed | step-3 |
| D004 | Multi-region | Deferred | working assumption: single region (us-east-1) | Revisit at 100k DAU | gate (user-original) | seed | step-3 |
| D005 | Webhook retries | Open | — | — | — | step-3 | — |
```

### Status values

- **Decided** — Resolution holds the chosen value.
- **Deferred** — user explicitly chose to defer; Resolution starts with `working assumption:`.
- **Open** — raised but unresolved. **Cannot proceed past the coherence pass with any Open rows.**

### Source values

Every row must have one. No "Assumed" status — if you don't know and the user hasn't picked, the row stays Open until forced to resolve.

- **`PRD §X`** — PRD specifies the value directly.
- **`PRD §X (ambiguous)`** — PRD references the topic but doesn't specify a concrete value (e.g., "high availability" with no number, "fast" with no target). Logged Open until clarified via gate; on resolution, source becomes `gate (PRD-clarification)` if user picks a value derived from PRD intent, or one of the other `gate (...)` flavors otherwise.
- **`artifact <path> §X`** — Existing technical artifact specifies the value.
- **`gate (research-rec)`** — user accepted the option research recommended.
- **`gate (user-override)`** — user picked an alternative listed in research, or chose differently than research recommended.
- **`gate (claude-synthesis)`** — research had relevant analysis but no explicit recommendation; Claude proposed options from the analysis; user picked.
- **`gate (user-original)`** — neither PRD nor research addressed this; user chose from Claude-proposed options grounded in inputs.

The Raised and Resolved columns reference the workflow step that surfaced or closed the row (e.g., `seed`, `step-2`, `step-3-component-X`).

## Surfacing Decisions to the User

Use `AskUserQuestion` whenever a decision needs the user's input. Rules:

- **Batch related questions** — up to 4 per call.
- **Provide 2-4 options per question.** Each option needs a one-line description of what choosing it implies.
- **Mark research-recommended options** with "(research-rec)" in the label when research had a recommendation.
- **Mark your recommendation** with "(Recommended)" only when you have a clear, evidence-backed lean from the inputs — not absence of contrary signal. When you do mark Recommended, the option's description **must include the strongest single argument against it**. Format: `"<implication> · Counter: <strongest objection>"`. If no real counter exists, the alternatives are probably weak — rework the option set.
- **State which goal(s) the decision serves.** The question text must reference the PRD goal, NFR, use case, and/or related Decision Register IDs. Example: `"Which tenant isolation mechanism? Addresses D016 / PRD §6.4 (high-priority NFR); also bears on D002, D003 (throughput targets)."` Keeps the user oriented to *why* the question matters.
- **Flag scope creep.** If any option (or research recommendation) addresses a non-goal (PRD §3) or out-of-scope item, mark it with "(addresses non-goal: <ref>)" in the label. The user must consciously accept scope creep.
- **Always offer a defer path** when the workflow can proceed with a working assumption. Phrase: `"Defer — proceed with: <concrete assumption>"`. If the design genuinely cannot proceed without the answer, mark the question blocking and don't offer defer.
- **Do not write open-ended prose questions.** If the answer space is open-ended, still propose 2-3 plausible options grounded in inputs plus a defer path; the user can override via "Other".

After every `AskUserQuestion` answer, update the Decision Register row in the same turn — including the Source field.

## Push-Back Protocol

When something doesn't make sense, surface it before recording. Push-back uses `AskUserQuestion` like all other decision channels.

- **Contradicts the register** — `"Your choice <X> conflicts with D00<N>: <prior decision>. Which should govern?"` Options: keep prior, replace prior, both update (specify how).
- **Contradicts the PRD** — `"Your choice <X> conflicts with PRD §Y, which says <Z>. Confirm overriding the PRD?"` Options: stick with PRD, override (logged as deviation), revise PRD before proceeding.
- **No support in inputs** — `"Your choice <X> isn't supported by the PRD or research. To record it, we need either (a) research that backs it, or (b) acceptance that this is a user-original choice."` Options: defer pending research, accept as user-original (with rationale), pick a different option grounded in inputs.
- **Insanely scoped or risky** — name the risk, cite the input that suggests it's risky, ask whether to proceed, scope down, or revisit.

---

## Workflow

Single interactive flow. Decisions surface as each section requires them. Pause for user input only via `AskUserQuestion`.

### Step 0: Setup

1. **Determine task slug.** If argument supplied, use it. Otherwise infer from PRD title or ask via `AskUserQuestion` with 2-3 candidate slugs derived from input filenames or content.
2. **Check for existing artifacts.** Glob `docs/design/<task-slug>/`. If files exist, ask via `AskUserQuestion`: resume (read existing decisions.md and design.md, continue from where they left off), restart (confirm overwrite), or pick a new slug.
3. **Load inputs.**
   - If user provided paths: Read each in full.
   - If inputs are in context: use the conversation; don't re-read.
   - If no PRD is identifiable: confirm spike mode via `AskUserQuestion`.

### Step 1: Seed the Decision Register

Create `docs/design/<task-slug>/decisions.md` with the table header.

Walk the inputs and seed rows:

- For every concrete requirement, NFR, or decision in the PRD → **Decided** row, source `PRD §X`. Includes use cases, NFRs with specific values, explicit architecture/technology choices, constraints (compliance, deployment, integration).
- For every PRD passage that names a topic but no concrete value (e.g., "high availability", "fast", "scalable") → **Open** row, source `PRD §X (ambiguous)`.
- For every recommendation or alternative-set in research → **Open** row. In Rationale, summarize what research recommended and what alternatives it considered.
- For every artifact-specified contract, type, or data model → **Decided** row, source `artifact <path> §X`.

After seeding, present the register and note any:

- **Value conflicts.** PRD says X for a topic where research suggested Y. Row stays Decided with source `PRD §X`; include a one-line callout: `"Research suggested X for <topic>, PRD says Y — confirm PRD is current."`
- **Scope creep from research.** Research recommendations touching PRD §3 (Non-Goals) or out-of-scope items get a callout: `"Research recommends <Y>, which addresses non-goal <Z> (PRD §3). PRD wins by default — confirm or revisit the non-goal."`

These are status updates, not decisions yet — the register reflects PRD priority. The user can override at a subsequent gate.

### Step 2: Resolve the Architecture Decision

The architectural choice is load-bearing; everything downstream depends on it. Resolve before walking components.

If the PRD already specifies the architecture (uncommon), confirm it's correctly captured as a Decided row and skip to Step 3.

Otherwise:

1. **Identify the architectural option set.** Pull from research if it enumerated options. If research analyzed but didn't enumerate, synthesize options from the analysis. If neither PRD nor research addressed architecture, propose 2-3 plausible options grounded only in the PRD's NFRs and use cases. Never invent options that don't trace to inputs.
2. **Form a recommendation.** State it in 2-3 sentences referencing specific NFRs and findings. If research recommended something, note whether your recommendation matches.
3. **Surface the choice via `AskUserQuestion`.** Question text references the goals/NFRs the architecture serves. Options: each architectural option as `"Option <N>: <name>"` with one-line tradeoff, mark research-rec, mark Recommended with counter, flag scope creep, include a `"Discuss further — drill into option <N>"` path. Do **not** include defer — Step 3 cannot proceed without an architecture.
4. **If user picks "Discuss further"**: answer the follow-up in conversation, then re-issue `AskUserQuestion`.
5. **Lock the choice.** Update the architecture row: Status → Decided, Resolution → chosen option, Rationale → user's reasoning (verbatim if explained), Source → appropriate `gate (...)` flavor.

### Step 3: Walk the Design Document

Build `docs/design/<task-slug>/design.md` incrementally.

1. **Write the skeleton.** Use Write to create design.md with the document header and section placeholders: `<!-- TBD: section name -->` for each section. Sections are listed in the [Document Format](#document-format) section below.
2. **For each section in order:**
   a. Identify the decisions the section requires.
   b. Check the register. If a row already covers a decision (Decided or Deferred), use it.
   c. Surface unresolved decisions via `AskUserQuestion` (batched up to 4 per call), grounded in inputs only. Update the register after each answer.
   d. Apply the push-back protocol when needed.
   e. Use Edit to replace the section's placeholder marker with the resolved content.

### Step 4: Coherence Pass

Read the full Decision Register and check for **internal contradictions** that batched resolution can produce. Examples:

- Row A says "feature X is in v1"; Row B says "feature X is deferred."
- Row A picks technology T; Row B picks an option that requires not-T.
- Row A says "tenants do Y themselves"; Row B describes the system doing Y for tenants.
- A Decided row references a topic that another Decided row says is out of scope.

Produce a one-paragraph coherence report. For each contradiction, raise an `AskUserQuestion` to reconcile (which row wins, or both update). If no contradictions, state explicitly: `"Coherence verified: N decided rows reviewed pairwise; no contradictions."`

Verify zero Open rows. New unknowns surfaced during this pass must be resolved via `AskUserQuestion` before continuing.

### Step 5: Assemble & Save

1. **Append the Open Questions & Deferred Decisions section** to design.md, mirroring the register's Deferred rows. If a row in this section doesn't trace to a register entry with a Source, you skipped a gate — go back.
2. **Update the document header** with final Status (`Ready for Review`) and date.
3. **Present the summary**:
   - Path to `design.md` and `decisions.md`.
   - Diagram count: `"1 overview + N data flow + (optional ER) + N sub-component = K diagrams"`
   - Decision Register stats: `"X Decided (N from PRD, M from gate, K from artifact), Y Deferred."`
   - The Deferred rows, with Resolve By milestones tied to implementation phases.

---

## Document Format

`docs/design/<task-slug>/design.md` follows this exact structure:

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

## Open Questions & Deferred Decisions
| ID | Question | Working Assumption | Source | Resolve By |

<Mirrors the Decision Register's Deferred rows. If a row here doesn't trace to a register entry with a Source, a gate was skipped — go back.>
````
