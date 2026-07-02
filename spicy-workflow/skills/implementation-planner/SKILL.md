---
name: implementation-planner
description: "Converts a technical design document into a phased, executable implementation plan with coverage analysis. Reads design docs cold, preserves phase structure, produces tasks sized for a single context window. Use after /spicy-experimental:design, /spicy-experimental:design-greenfield, or /spicy-experimental:design-integrate has produced a design document."
disable-model-invocation: true
---

# Implementation Planner

You are converting a finished technical design document into an executable implementation plan. The design tells you WHAT to build. Your job is to figure out the exact ORDER and STEPS to build it safely.

## Before You Start

If this is your first plan in this session or you're uncertain about depth/format, read the abbreviated example at `${CLAUDE_PLUGIN_ROOT}/skills/implementation-planner/examples/notification-system-plan.md` to calibrate. Otherwise, proceed directly — the section instructions below are sufficient.

## Critical Rules

1. **Read the design document before planning anything.** Every task must trace back to the design. Do not invent work that isn't in the design.
2. **Preserve the design's phase structure.** The design has implementation phases for a reason — each represents a safe, deployable increment. Your plan nests tasks inside those phases, it doesn't flatten them.
3. **Each task must be executable cold.** After `/clear`, an agent reading only the plan and the referenced files must know exactly what to do. "Wire things up" is not a task. "Register `WebhookService` in `src/app.ts` by adding `app.use('/api/v1/webhooks', webhookRouter)` after the existing order routes" is a task.
4. **TDD is the default, not the mandate.** Logic-heavy tasks get RED/GREEN/REFACTOR. Migrations, config, wiring, and infrastructure get task-appropriate verification. Never force a RED phase onto a database migration.
5. **Flag risk, don't hide it.** Tasks touching shared code, production data, or tightly-coupled components get a ⚠️ risk flag with a one-line explanation.

## Inputs

You will receive a path to a design document. This is typically:
- `docs/design/<task-slug>/design.md` (from the design workflow)
- Or any standalone technical design document

You may also receive:
- `docs/design/<task-slug>/phase-1-*.md` and `phase-2-*.md` (intermediate phase outputs from the design workflow — useful for context on decisions and constraints)
- A path to an existing codebase (for integration designs)

## Process

### 1. Load and Analyze the Design

Read the design document thoroughly. Extract:

- **Goal**: What are we building and why?
- **Phases**: The implementation phases defined in the design (see format below)
- **Components**: Every component in the architecture diagram
- **Contracts**: Every public API, type definition, event schema
- **Data model**: Every entity and relationship
- **Files**: The directory structure and every file to create or modify
- **Dependencies**: What depends on what (between components, between phases)

**Phase extraction:** Design documents store phases in a table with these columns:

| Column | Maps to |
|--------|---------|
| Phase | Phase number in your plan |
| Name | Phase heading |
| Delivers | Summary of what tasks must produce |
| Depends On | Prerequisites (prior phases, external setup) |
| Size | Size rating (S/M/L) |
| Done When | The done condition — your plan must satisfy this |
| Rollback | (integration designs only) How to revert this phase |

The design may also include **phase-specific risks** in prose below the table. Carry these forward into your risk assessment (Step 3) — the design author identified them for a reason.

The Walking Skeleton section above the table gives additional context for Phase 1: what's real, what's stubbed, what it proves, and the concrete test.

If the design references existing codebase files (integration designs), read the relevant files to understand current patterns.

### 2. Break Phases into Tasks

For each implementation phase defined in the design:

**a) Identify the work units.** Each component, contract, entity, or wiring step that belongs in this phase becomes a parent task.

**b) Choose verification approach per task:**

| Work Type | Verification | Subtask Structure |
|-----------|-------------|-------------------|
| Business logic, services, utilities | TDD | RED → GREEN → REFACTOR |
| Data model, entities, types | TDD | RED (validation tests) → GREEN |
| API endpoints, routes | TDD | RED (request/response tests) → GREEN → REFACTOR |
| Database migrations | Migration test | Write migration → Run → Verify schema → Verify rollback |
| Configuration, env vars | Smoke test | Add config → Verify loads → Verify defaults |
| DI wiring, route mounting | Integration test | Wire → Write integration test → Verify |
| Infrastructure (CI, Docker) | Manual/script | Set up → Run → Verify output |
| Frontend components | TDD + visual | RED → GREEN → Visual verification |

**c) Size each task for a single context window.** A parent task and all its subtasks should be completable in one session before `/clear`. If a component is too large, split it into multiple parent tasks within the same phase.

**d) Assign skills (optional).** If the project uses a skill system (e.g., `test-driven-development`, `python-development`), add a `**Skills**` field to each parent task listing which skills the executor should load. Every implementation task should include the language skill and `test-driven-development` when using TDD verification. Omit the field entirely if the project doesn't use skills.

**e) Order by dependencies within the phase.** Foundation before features. Data model before services. Services before API layer.

### 3. Flag Risks

For each task, assess:

- Does it modify existing shared code? → ⚠️ **Shared code**: [what and who depends on it]
- Does it touch production data? → ⚠️ **Data risk**: [what could go wrong]
- Is the requirement ambiguous? → ⚠️ **Ambiguity**: [what's unclear and the assumption being made]
- Is there tight coupling? → ⚠️ **Coupling**: [what's coupled and why it's risky]
- Is it the first time using a technology? → ⚠️ **New tech**: [what and level of team familiarity]

Most tasks should have NO risk flags. If everything is flagged, nothing is flagged.

### 4. Coverage Analysis

**This is mandatory.** Map tasks back to the design to verify completeness.

**Component Coverage**: For every component in the design's architecture diagram:
- Which task(s) implement it?
- If not covered: is it intentionally deferred or missing?

**Contract Coverage**: For every public API, type, interface in the design:
- Which task's RED phase tests it?
- If not tested: flag it

**File Coverage**: For every file in the design's directory structure:
- Which task creates or modifies it?
- If not covered: flag it

**Phase Done Condition Coverage**: For every done condition in the design's phases:
- Which task(s) satisfy it?
- If no task maps to a done condition: the plan is wrong

If gaps exist, list them and ask the user to confirm they're intentional deferrals before finalizing the plan.

### 5. Mark Safe Stopping Points

At each phase boundary, note:
- ✅ **Safe to `/clear` and resume** — all state is in the plan file
- ✅ **Safe to deploy** — the system is in a valid state (if applicable)
- What was proven by completing this phase (from the design's done conditions)

**Important:** Phase checkpoints are not the *only* valid `/clear` points. You can `/clear` after any completed parent task — the plan file tracks all progress via checkboxes. Phase checkpoints mark where the design's done conditions are satisfied and the system is in a known-good deployable state.

## Output Format

Write to `docs/design/<task-slug>/plan.md` (or the user's preferred path):

````markdown
# Implementation Plan: {Feature Name}

**Design**: {path to design document}
**Date**: {YYYY-MM-DD}

## Overview

{2-3 sentences: what we're building, total phase count, total task count}

## Skills Required *(omit if project doesn't use skills)*

- `{language-skill}` — {language} patterns and conventions
- `test-driven-development` — TDD cycle for all logic tasks

---

## Phase 1: {Phase Name from Design}

> **Done when**: {exact done condition from design's phase table}
> **Size**: {S/M/L from design}

Use the design's exact phrasing for done conditions — do not paraphrase. This ensures coverage analysis can trace plan tasks back to design conditions without interpretation.

### Dependencies
- {External setup, prior phase, etc. — list "None" for Phase 1 if only external deps}

### Tasks

- [ ] **1.1 {Component/Work Unit Name}**
  - **Files**: `path/to/file.ext`, `path/to/test.ext`
  - **Depends on**: None
  - **Verification**: TDD
  - **Skills**: {language-skill}, test-driven-development *(omit if project doesn't use skills)*
  - [ ] 1.1.1 RED: Write failing tests for {specific behavior}
    - `test_name_describing_behavior` — {what it proves}
    - `test_another_behavior` — {what it proves}
  - [ ] 1.1.2 GREEN: Implement {specific behavior}
    - {Concrete implementation step}
    - {Concrete implementation step}
  - [ ] 1.1.3 REFACTOR: {Specific improvement, or "Skip — implementation is straightforward"}

- [ ] **1.2 {Migration/Config/Wiring Task}**
  - **Files**: `path/to/migration.sql`
  - **Depends on**: None
  - **Verification**: Migration test
  - [ ] 1.2.1 Write migration: {specific schema change}
  - [ ] 1.2.2 Run migration, verify schema matches design
  - [ ] 1.2.3 Test rollback — verify clean revert

- [ ] **1.3 {Risky Task}**
  - **Files**: `path/to/shared/file.ext`
  - **Depends on**: 1.1
  - **Verification**: TDD + integration
  - ⚠️ **Shared code**: `utils/auth.ts` is imported by 8 other modules
  - [ ] 1.3.1 RED: Write failing tests for {behavior}
    - `test_name` — {what it proves}
  - [ ] 1.3.2 GREEN: Implement changes to shared module
  - [ ] 1.3.3 Run full test suite — verify no regressions

**Phase 1 checkpoint** ✅
- Safe to `/clear` — all progress tracked in this file
- {What's proven / deployable after this phase}
- Rollback: {from design's Rollback column, if integration design; omit for greenfield}

---

## Phase 2: {Phase Name from Design}
...

---

## Coverage Analysis

### Component Coverage

| Component (from design) | Task(s) | Status |
|------------------------|---------|--------|
| {ComponentA} | {task_id} | ✅ Covered |
| {ComponentB} | {task_id} | ✅ Covered |
| {ComponentC} | None | ❌ Missing |

### Contract Coverage

| Contract | Tested In | Status |
|----------|-----------|--------|
| `{Interface.method()}` | {task_id} RED | ✅ Covered |
| `{METHOD /endpoint}` | {task_id} RED | ✅ Covered |

### File Coverage

| File (from design) | Task | Status |
|-------------------|------|--------|
| `{path/to/file.ext}` | {task_id} | ✅ Covered |

### Gaps

| Item | Type | Notes |
|------|------|-------|
| {item or "None"} | {Component/Contract/File} | {explanation} |

---

## Execution Notes

### How to Use This Plan

Execute phases in order. Within each phase, execute tasks in order (dependencies are already resolved by ordering).

**With an iterate command:**
```
/spicy-workflow:execute docs/design/<task-slug>/plan.md
```

**Manually:**
```
# Start Phase 1
# After each parent task: mark subtasks [x], then parent [x]
# At phase checkpoint: /clear and resume with this file
```

### Verification Commands

```
{Language-appropriate test/lint/typecheck commands from the design}
```
````

## After the Plan

**STOP.** Present the plan file path to the user. Ask them to review before running the automated plan review.

---

## Plan Review

**Do not review the plan yourself.** Use the Task tool to delegate to the `plan-reviewer` agent. This ensures the review happens in a forked context with fresh eyes — no anchoring to the reasoning that produced the plan.

Task prompt:

```
Review the implementation plan at <plan_path> against the design document at <design_path>. Check: coverage (does every design component have tasks?), ordering (are dependencies satisfied?), executability (could an agent pick up any task cold and know what to do?), risk awareness (are dangerous tasks flagged?), and phase integrity (do phase boundaries represent safe stopping points?). Produce a numbered issue list by severity and a revised plan with Critical and Major issues fixed. Save to the same path.
```

After the reviewer completes, present the review summary and final file path to the user.
