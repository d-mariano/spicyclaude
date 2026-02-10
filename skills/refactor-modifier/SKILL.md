---
name: refactor-modifier
description: "Composable modifier that adds legacy analysis, migration strategy, behavior preservation, and cleanup planning to either the greenfield or feature-integration design workflow. Apply when the task involves replacing, restructuring, or rewriting significant existing code."
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
disable-model-invocation: true
---

# Refactor / Rewrite Modifier

This is NOT a standalone workflow. It adds sections to the greenfield-design or feature-integration workflow when the task involves significant restructuring, replacement, or rewriting of existing code.

## When to Apply

Apply if any of these are true:
- Replacing an existing component with a fundamentally different implementation
- Moving responsibilities between existing components
- Old and new code must coexist during a migration period
- The data model changes require backfilling or dual-writing
- Consolidating multiple existing patterns into a new one
- Existing tests need significant rewriting, not just updating

If you're just adding new code with minor cleanup, use feature-integration without this modifier.

## Phase 1 Addition: Legacy Analysis

**Add after the environment survey (greenfield) or codebase reconnaissance (integration).**

### Current State Assessment
- **What exists today**: Read the actual code of the component(s) being replaced. Describe real behavior, not surface summaries.
- **Why it's being replaced**: Specific problems — performance, maintainability, correctness, scalability. Be concrete with evidence from the code.
- **What it gets right**: What the current implementation handles well that must be preserved. This is critical — refactors that lose working behavior are bugs.
- **Hidden responsibilities**: Non-obvious things the current code does. Side effects, implicit ordering, undocumented behavior other components depend on. Read the callers, not just the implementation.
- **Data state**: Data accumulated under the current implementation. Shape, volume, quality. Known inconsistencies or tech debt in stored data.

### Dependency Audit
- **Who calls this code?** Every caller/consumer with file paths. Use Grep.
- **Who does this code call?** Every downstream dependency.
- **What tests exercise this code?** Test files and quality assessment (behavior tests vs. implementation tests).
- **What monitoring exists?** Dashboards, alerts, SLOs tied to the current implementation.

### Migration Constraints
- Can we do a hard cutover or must old and new coexist?
- Is there a data migration? Volume? Online or downtime required?
- Are there external consumers (APIs, webhooks, other teams) needing coordination?
- What's the blast radius of getting this wrong? (data loss, downtime, broken integrations — be specific)

## Phase 2 Addition: Migration Strategy

**Add after constraint locking.**

### Strategy Selection
Choose and justify one:

**A) Big Bang** — Remove old, deploy new in one release.
- Only when: blast radius is low, no data migration, comprehensive tests, rollback is a revert
- Risk: high — everything fails at once

**B) Strangler Fig** — New code alongside old, traffic/responsibility shifted gradually per capability.
- Requires: routing mechanism (feature flags, gateway, adapter layer)
- Best when: system is too large or risky to replace at once

**C) Branch by Abstraction** — Introduce interface over existing code, build new implementation behind same interface, swap via config.
- Requires: existing code can be wrapped in an interface without a massive refactor first
- Best when: code structure allows a clean seam

**D) Parallel Run** — Both execute simultaneously, results compared, new takes over after confidence.
- Requires: operation is idempotent or read-only, output comparison possible
- Best when: correctness is critical, subtle regressions unacceptable

### Coexistence Plan
- How do old and new coexist during migration?
- Where is the seam? (routing layer, abstraction interface, feature flag)
- How long does coexistence last? What determines when old code is safe to remove?
- If migration stops midway, is the system in a valid state?

### Data Migration Plan
- What data moves, transforms, or gets backfilled?
- Incremental (batch by batch) or atomic?
- How to handle data written to old schema during migration window (dual-write, catch-up job)
- Validation strategy — how to verify migrated data is correct
- Rollback plan for the data migration (often the hardest part)

### Cutover Criteria
- Metrics proving new implementation works correctly
- Minimum soak time before trusting new code
- Who approves final cutover
- Rollback plan post-cutover (is it possible, or a one-way door?)

## Phase 3 Addition: Design Sections

**Add to the design document.**

### Behavior Preservation Map

This is a contract with the existing system. Every row must reference a test.

| Existing Behavior | Covered By (New Design) | Verified By (Test) | Notes |
|---|---|---|---|
| Order total with tax | `OrderCalculator.calculateTotal()` | `order-calculator.test.ts: "applies regional tax"` | Logic unchanged, extracted |
| Retry on payment fail (3x) | `PaymentService.processWithRetry()` | `payment-service.test.ts: "retries on timeout"` | Was implicit in catch, now explicit |

If a behavior is intentionally dropped, note it and justify it.

### Transition Architecture
If using Strangler Fig, Branch by Abstraction, or Parallel Run:
- Architecture diagram during the transition (not just the final state)
- Both old and new paths visible, routing/switching mechanism highlighted
- Which capabilities are on old vs. new at each phase

### Cleanup Plan
The refactor isn't done when new code works. It's done when old code is removed.
- What gets deleted and when
- Feature flags / routing rules to remove
- Dead code, unused dependencies, orphaned migrations
- Owner and phase for each cleanup task

## Phase 4 Addition: Review Checks

**Add to the design-reviewer subagent prompt:**

```
Additionally check these refactor-specific concerns:
- Is every row in the Behavior Preservation Map actually covered? Read the referenced tests — do they test the claimed behavior or just the implementation?
- Does the data migration plan account for data written during the migration window?
- During the transition, can old and new code conflict? (both writing to same table, both handling same event, both responding to same API call)
- Is the cleanup plan a real commitment in the phase plan with done conditions, or a "we'll get to it later"?
- Is the rollback plan tested or theoretical? Can you actually roll back the data migration?
- Is the stated blast radius honest? What's the worst case at the worst possible moment?
```

## Tips

- **The Behavior Preservation Map is the single most important artifact.** Write it BEFORE designing anything new.
- **"We'll clean up later" is a lie.** Put cleanup in the phase plan with done conditions.
- **Data migrations are the hard part.** Spend disproportionate time on this section.
- **Parallel runs are underused.** If output can be compared, run both and diff.
- **A refactor that also adds features is two projects pretending to be one.** Separate them.
