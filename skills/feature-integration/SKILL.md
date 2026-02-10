---
name: feature-integration
description: "Multi-phase technical design workflow for adding features to existing codebases. Covers codebase reconnaissance, change strategy, delta-focused integration design, and automated review. Use when extending a system that already exists with established patterns."
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Task
disable-model-invocation: true
---

# Feature Integration Workflow

You are executing a multi-phase technical design workflow for adding a feature to an existing codebase. The hard problem is understanding what exists well enough to extend it without breaking it.

## Critical Rules

1. **Pause after every phase.** Present your output, then ask the user to review before proceeding.
2. **Read the actual code.** Do not trust assumptions. Use Grep, Glob, Read, and Bash to explore the codebase. Read config files, key services, existing tests, and similar features.
3. **Frame everything as deltas.** This is NOT a greenfield design. For existing components, describe what changes, not what they are. For new components, describe them fully but note which existing pattern they follow.
4. **Follow existing conventions.** Match the naming, structure, and patterns of the codebase even if you'd do it differently. Consistency beats local perfection.
5. **The output file must stand alone.** A downstream planner or engineer should be able to read it cold.

## Phase 1: Codebase Reconnaissance

**Goal**: Develop deep understanding of the existing system's structure, patterns, and the specific areas the feature will touch. Do NOT design anything yet.

Start by actually reading the codebase:
- Run `find . -maxdepth 3 -type f | head -150` and `tree -L 2 -d` to map structure
- Read package manifests (package.json, go.mod, pyproject.toml, Cargo.toml, *.csproj, etc.)
- Read existing architecture docs if present (ARCHITECTURE.md, docs/, README.md)
- Read 2-3 features similar in shape to what we're building

Produce a reconnaissance report:

### 1. Codebase Profile
- Language(s), framework(s), package manager
- Architecture pattern (layered, hexagonal, event-driven, monolith, microservices)
- How a typical feature is structured (trace one end-to-end with file paths)
- Test conventions (framework, organization, coverage impression)
- Configuration approach (env vars, config files, feature flags)
- Dependency injection / composition approach

### 2. Impact Map
Every part of the system the feature will touch:
- **Files to modify**: specific paths + one-line description of what changes
- **Files to create**: specific paths, following existing naming/location conventions
- **Dependency chain**: if file A changes, what depends on A?
- **Database changes**: new tables, altered columns, new indexes, migrations
- **API surface changes**: new endpoints, modified shapes, breaking changes
- **Configuration changes**: new env vars, feature flags, config keys

### 3. Patterns to Follow
From the similar features you read, extract:
- How a new module/feature is structured (with file path examples)
- How dependencies are injected/composed
- How errors are handled and propagated
- How validation is done and where
- How auth is enforced
- How tests are written for similar features
- Cite specific files as references.

### 4. Constraints & Landmines
- **Tight coupling risks**: parts that will resist the change (god objects, circular deps, shared mutable state)
- **Test gaps**: are the areas we're touching well-tested? Should we backfill first?
- **Migration concerns**: data migrations needed? Migration framework in place?
- **Backward compatibility**: API versioning, feature flags, schema coexistence needed?
- **Performance hotspots**: are we modifying a critical path?

### 5. Unknowns & Gaps
- Ambiguities in the task specification
- Code behavior you don't fully understand (flag specific files/functions)
- Assumptions about how the existing system works
- For each: default assumption + question for developer/stakeholder

**STOP. Present the report. Ask the user to validate the impact map, confirm the patterns, and answer unknowns.**

---

## Phase 2: Change Strategy & Constraint Locking

**Goal**: Define how the change will be made — the strategy for getting there safely.

Incorporate the user's corrections and produce:

### 1. Change Approach
Choose and justify one of:
- **Additive**: new code alongside existing, minimal modifications. Feature-flagged if needed.
- **Modificative**: direct changes to existing components. Required when changing existing behavior.
- **Strangler**: new implementation gradually replaces old. Used when existing code is too tangled.

Explain why this approach over the others.

### 2. Locked Constraints
- Conventions to follow (from Phase 1 patterns)
- Files to modify (updated with corrections)
- Files to create (same)
- Backward compatibility requirements
- Migration requirements
- Feature flag strategy (if applicable)

### 3. Pre-Work Required
Anything that must happen BEFORE the feature work:
- Test backfills for under-tested areas we're modifying
- Refactoring to decouple components we need to extend
- Database migrations that should land separately
- Dependency updates

If none, state: "None — the codebase is ready for this change."

### 4. Risk Mitigation
For each landmine from Phase 1:
- How to avoid triggering it
- How to detect and recover if triggered
- Rollback plan if the feature causes production issues

### 5. Challenge the User's Answers
Push back on corrections or decisions that are inconsistent or risky. Last cheap point to change direction.

**STOP. Present the strategy. Ask the user to confirm before proceeding to design.**

---

## Phase 3: Integration Design

**Goal**: Produce the design document, framed entirely as changes to the existing system.

Write the design to `docs/design/<task-slug>.md` (or user's preferred path).

### 1. Goal
3-5 sentences: what this feature adds, why it's needed, what success looks like from user and engineering perspectives.

### 2. Context Diagram
Mermaid diagram showing where the feature sits in the existing system:
- Existing components this feature touches (gray/muted)
- New components this feature adds (highlighted)
- Modified interactions (labeled "new" or "modified")
- Only the relevant portion of the system — not the whole thing

### 3. Change Map
Precise specification of every change:

**Modified Files**
| File | What Changes | Why |

**New Files**
| File | Purpose | Follows Pattern Of |

**Database Changes**
| Migration | Description | Reversible? |

**Configuration Changes**
| Key | Type | Default | Purpose |

### 4. Data Flow
For each new or modified flow:
- Mermaid sequence diagram through existing AND new components
- Clearly mark new vs. existing steps
- Show error/failure path
- If modifying an existing flow, show BEFORE and AFTER

### 5. New Component Details
For each new file/class/module:
- **Responsibility**: one sentence
- **Follows pattern of**: reference existing component it mirrors (with file path)
- **Public API**: full type signatures
- **Entities & Data Models**: new types with fields. For modifications to existing entities, show only the delta.
- **Dependencies**: what existing components it imports/consumes
- **How it's wired in**: DI registration, import chain, route definition, middleware — whatever the codebase convention is

### 6. Modified Component Details
For each existing component being changed:
- **Current behavior**: one sentence (relevant to the change)
- **New behavior**: one sentence
- **API changes**: before/after for non-trivial changes
- **Backward compatible?**: yes/no, and if no, what breaks and how it's handled

### 7. Migration Plan (if applicable)
- Steps in order
- Can it run with old code still deployed? (zero-downtime)
- Rollback migration
- Data backfill needed?

### 8. Implementation Phases
Ordered phases with integration-specific principles:
- **Phase 1 is always pre-work** (test backfills, refactoring, migrations from Phase 2)
- **Each phase is a safe, deployable increment** — minimize blast radius
- **Feature flags gate user-facing changes**
Each phase: name, deliverable, dependencies, complexity (S/M/L), done condition, rollback plan

Include a Mermaid Gantt chart.

### 9. Test Plan
- Existing tests that need updating (specific files)
- New unit tests for new components
- New integration tests for modified flows
- Edge case tests for error paths
- End-to-end verification approach
- Regression strategy (how to verify nothing broke)

### 10. Open Questions & Deferred Decisions
| Question | Why Deferred | Resolve By | Working Assumption |

**STOP. Present the design file path. Ask the user to review before the automated self-review.**

---

## Phase 4: Design Review

Delegate to the `design-reviewer` subagent:

```
Review the technical design document at <file_path>. This is a feature integration design for an existing codebase. In addition to standard review checks (structural integrity, contract consistency, feasibility, testability, error handling, naming), also verify:
- Does every "Follows pattern of" reference actually match the pattern in the referenced file? Read the referenced files to check.
- Are all modified files accounted for in the test plan?
- Is the migration reversible as claimed?
- Does the feature flag strategy allow disabling without orphaned data or broken state?
- Are the wiring instructions complete for the existing framework?

Produce a numbered issue list by severity (Critical/Major/Minor), then a revised document with Critical and Major issues fixed. Save to the same path.
```

Present the review summary and final file path to the user.
