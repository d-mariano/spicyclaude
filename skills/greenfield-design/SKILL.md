---
name: greenfield-design
description: "Multi-phase technical design workflow for building new systems from scratch. Covers landscape analysis, decision locking, full system design, and automated review. Use when there is no existing codebase or when building an entirely new service/application."
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Task
disable-model-invocation: true
---

# Greenfield Design Workflow

You are executing a multi-phase technical design workflow for a new system being built from scratch. The hard problem is making good architectural choices under maximum freedom.

## Critical Rules

1. **Pause after every phase.** Present your output, then ask the user to review, correct, and answer unknowns before proceeding.
2. **Do not skip the Unknowns section.** It is the most valuable output of Phase 1. A design that papers over ambiguity is worse than no design.
3. **Name things concretely.** Every type, interface, function, and file must have a real name. "SomeService", "DataProcessor", and "handleData" are banned.
4. **Skip sections that don't apply.** Not every system needs DTOs. Not every design needs cross-cutting concerns. When you skip a section, add one line explaining why.
5. **The output file must stand alone.** A downstream planner or engineer should be able to read it cold with no conversation context.

## Phase 1: Landscape & Tradeoff Analysis

**Goal**: Understand the problem space, survey solutions, evaluate architectural approaches. Arrive at Phase 2 with a justified direction, not a default one.

Produce a structured report covering:

### 1. Problem Framing
- Core problem in one sentence
- Users/consumers of this system (humans, services, or both)
- Top 3-5 primary use cases by importance
- Non-functional requirements (throughput, latency, availability, consistency, data volume, compliance)
- Expected scale at launch vs. 12 months (be specific: requests/sec, data volume, concurrent users)

### 2. Prior Art Survey
- Existing systems, libraries, or products solving similar problems
- Lessons from how they approached it
- Open-source solutions to build on vs. rebuild
- Established architectural patterns for this problem class (CQRS, event sourcing, saga, etc.)

### 3. Architectural Options
Present 2-3 fundamentally different approaches. For each:
- **Name + one-line summary**
- **Mermaid diagram**: high-level architecture
- **Strengths**: what this makes easy
- **Weaknesses**: what this makes hard
- **Best when**: conditions that favor this choice
- **Technology implications**: language, infra, data stores
- **Operational complexity**: what production looks like

Do NOT recommend one yet. Present them fairly.

### 4. Technology Candidates
For each major decision (language, framework, database, message broker, hosting):
- 2-3 realistic options with one-sentence tradeoff vs. alternatives
- Flag anything requiring the team to learn a new stack

### 5. Unknowns & Research Needed
- Missing information that would change the architectural choice
- Assumptions about scale, team size, timeline, constraints
- For each: default assumption if unanswered + question for stakeholder

**STOP. Present the report. Ask the user to choose an architectural direction, answer unknowns, and correct any mistakes.**

---

## Phase 2: Decision Locking & System Boundaries

**Goal**: Convert the Phase 1 analysis into hard commitments. After this phase, the direction is locked.

Incorporate the user's decisions and produce:

### 1. Architectural Decision Records
For each major decision (architecture, language, framework, database, hosting), produce:
- **Decision**: what was chosen
- **Context**: why this decision was needed
- **Rationale**: why this over alternatives (reference Phase 1 tradeoffs)
- **Consequences**: what's easier and what's harder
- **Revisit trigger**: future condition that should reopen this decision

### 2. System Boundary Definition
- Inside vs. outside the system
- External dependencies (APIs, services, databases, providers)
- What the system exposes (APIs, events, UIs, files)
- Mermaid system context diagram showing actors, the system, and external systems

### 3. Scope Boundaries
- Explicitly IN scope
- Explicitly OUT of scope
- Minimum Viable System — smallest version that delivers value

### 4. Non-Functional Commitments
Lock with specific, testable targets:
- Performance (e.g., p99 < 200ms)
- Availability (e.g., 99.9%)
- Data (store, consistency model, backup cadence)
- Security (auth, encryption, PII handling)
- Observability (logging, tracing, metrics)

### 5. Challenge the User's Decisions
If any choices are inconsistent, under-specified, or likely to cause problems, push back NOW. This is the last cheap point to change direction.

**STOP. Present the locked constraints. Ask the user to confirm before proceeding to design.**

---

## Phase 3: Full System Design

**Goal**: Produce the complete technical design document. Everything flows from Phase 2 decisions.

Write the design document to `docs/design/<task-slug>.md` (or the user's preferred path). The document must include:

### 1. Goal
3-5 sentences: what this system does, what problem it solves, what "done" looks like. Engineering goal, not product pitch.

### 2. Architecture Overview
Mermaid component diagram expanding the system context from Phase 2:
- All internal components with one-line responsibilities
- Communication patterns (label arrows: sync/async, protocol, data format)
- Data stores and owning components
- External integrations
- Use subgraphs for layers or bounded contexts

### 3. Data Flow
For each primary use case from Phase 1:
- Mermaid sequence or flow diagram
- Happy path with all components involved
- At least one error/failure path per flow
- Mark async boundaries and data transformations

### 4. Data Model
- Language-appropriate type definitions for all entities
- Relationships (1:1, 1:N, M:N) shown explicitly
- Mermaid ER diagram if 3+ entities with relationships
- Note which component owns each entity

### 5. Directory Structure
Full project structure with annotations:
```
project-root/
├── src/
│   ├── module/            # purpose
│   │   └── file.ext       # specific responsibility
```
Justify the structure: framework conventions, domain boundaries, or layer separation.

### 6. Component Details
For each component in the architecture diagram:

**[Component Name]**
- **Responsibility**: one sentence
- **Technology**: specific framework, library, or tool
- **Key Abstractions**: 2-5 most important types/classes/modules with signatures or type definitions
- **Public Contract**: how other components interact with this one:
  - Function/method signatures with full type annotations
  - HTTP endpoints (method, path, request/response/error shapes)
  - Event schemas (name, payload type)
  - gRPC/GraphQL definitions if applicable
- **Internal Design Notes**: non-obvious implementation decisions only. Skip if straightforward.

Adapt vocabulary to the ecosystem:
- OOP (C#, Java, TypeScript classes) → Interfaces, Abstract Classes, DTOs, DI bindings
- Functional/Module-based (Python, Go, Rust, Elixir) → Module exports, Type aliases, Protocols/Traits
- Frontend (React, Vue, Svelte) → Component tree, Props/State types, Hook contracts, Store shape
- Infrastructure (Terraform, CDK) → Resource definitions, Stack composition

### 7. Cross-Cutting Concerns
Include only if applicable (skip with a note if not):
- Error handling strategy (propagation, type hierarchy, user-facing vs. internal)
- Auth (where enforced, how identity flows)
- Logging & observability (format, trace propagation, key metrics)
- Configuration (loading, env overrides, secrets)

### 8. Walking Skeleton
The thinnest possible end-to-end slice through the entire system:
- Specific use case it covers
- What is real vs. stubbed
- What it proves about the architecture
- The test that validates it works

This becomes Phase 1 of implementation.

### 9. Implementation Phases
Ordered phases. Each phase:
- Descriptive name
- What it delivers
- Dependencies (prior phases, external setup)
- Complexity (S / M / L)
- Done condition — what is testable when complete
- Phase-specific risks

Phase 1 is always the Walking Skeleton. Include a Mermaid Gantt chart.

### 10. Open Questions & Deferred Decisions
| Question | Why Deferred | Resolve By | Working Assumption |

**STOP. Present the design file path. Ask the user to review before the automated self-review.**

---

## Phase 4: Design Review

Delegate to the `design-reviewer` subagent:

```
Review the technical design document at <file_path>. This is a greenfield system design. Evaluate it for structural integrity, contract consistency, feasibility, testability, error handling, naming quality, and security concerns. Produce a numbered issue list categorized by severity (Critical/Major/Minor), then produce a revised document with all Critical and Major issues fixed. Save the revised document to the same path.
```

Present the review summary and final file path to the user.
