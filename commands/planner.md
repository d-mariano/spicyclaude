---
allowed-tools: Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch
argument-hint: [prd] [research]
description: Prepare a plan that implements the PRD or subcomponent that is informed by recent research.
---
You are a world class software engineer.

We are going to work on $1.

Make a detailed plan to accomplish this, based on $2.

Prioritize for rapid iteration and MVP development. Do NOT add scope.

---

## Phase 1 — Pre-flight survey (do this BEFORE drafting the plan)

Most planning bugs come from skipping this step. Read the relevant code and write a "Pre-flight findings" section that answers:

- **Call-site survey.** For each existing call site of code you're changing or extending: how does it currently behave on each axis you're changing? List heterogeneity explicitly. When extending a pattern across N call sites, the assumption that they're homogeneous is usually wrong — find the 1-of-N that breaks the pattern.
- **Existing-test impact.** For each existing test that touches state your changes affect (globals, singletons, fixtures, autouse): predict which break and how to fix them. Fixtures you add or modify will collide with existing tests that depend on the old fixture's behavior — name them.
- **Same-file sibling-test enumeration.** For every test file you're modifying, list ALL tests in the file in one of three buckets: CHANGED, UNCHANGED-but-named (so the implementer doesn't second-guess), UNCHANGED-irrelevant (don't enumerate). The cold-read implementer opens the file diff and wonders whether the tests you *didn't* touch should also have changed — the "do not touch these" list must be explicit, not implied.
- **Stale-reference grep.** For any symbol being renamed or removed, run `grep -rn <old-name>` across the whole project and triage every hit. Imports and call sites change automatically with the rename; comments, docstrings, log messages, error strings, and test names rot silently.
- **Sibling-ticket coupling.** For each sibling ticket this work blocks or unblocks: (a) name the API surface they depend on; confirm your surface meets their needs — if you can't confirm, flag as a pre-merge check with whoever owns the sibling; (b) **deployment-window risk** — what's the user-visible state of the system between this PR merging and the sibling landing? "It works" is a complete answer; so is "telemetry drops for tool X — acceptable pre-launch." Silence here is the bug.

Keep these findings as a top-level "Pre-flight findings" section in the final plan — they document the assumptions the rest of the plan is built on.

---

## Phase 2 — Drafting the plan

- **Overview.** 2-3 sentences: what you're doing and why now.
- **Key decisions table.** Each row: decision + choice + one-line rationale. Surface deliberate divergences from the ticket/PRD AC here so reviewers see them upfront, not buried in a diff.
- **Pre-flight findings** (from Phase 1).
- **AC trace table.** For PRD/ticket-driven work, cross-walk every AC item to where it's satisfied (file, test, or deferred ticket). No AC items left unaccounted for. Divergences from AC text go in the Key decisions table; this table just confirms coverage.
- **Files to change.** Group as NEW / MODIFIED / DELETED / NOT-modified-but-considered. For each: file path + concrete diff intent.
- **New functions and classes.** Write the **full signature with parameter types and return type**, not a description. If you can't write the signature, you don't understand the function yet. Add a 1-2 sentence docstring after each.
- **Test impact in three buckets:**
  - **ADD**: new tests, name + the observable behavior change that would cause the test to fail. "Locks regression: function does not call billing client" is a behavior. "Function records event when called" is a tautology and a sign the test shouldn't exist — see the Tautology anti-pattern in `test-driven-development/testing-principles.md`.
  - **MODIFY**: existing tests changing, what changes, why.
  - **DELETE**: existing tests being removed, what replaced them.
- **CLAUDE.md reinforcement.** Cite specific rules from project + global CLAUDE.md that constrain this work (clarity, simplicity, reuse, third-party usage).
- **Commit granularity.** State the number of commits and the boundary rationale. Mechanically-identical changes across N files often belong in one commit, not N.
- **Follow-up tickets to file.** One bullet per ticket: name, scope, why deferred. Don't let "later" be silent.
- **Stakeholder decisions needed before merge.** One bullet per decision: what's pending, who decides, default if no answer arrives.
- **Risks / things to surface in PR description.** What reviewers need to know when this lands.
- **Tasks section** (format below).

---

## Phase 3 — Footgun checklist

Scan these gotchas; for each that applies, document how the plan addresses it.

- **Module-import-time side effects.** Singletons, registries populated at bottom of module — what happens on re-import or under `pytest-randomly`?
- **Mutable global state in tests.** Fixtures, `monkeypatch`, isolation under `pytest-xdist` / `pytest-randomly` / re-ordering.
- **Type-narrowing edge cases.** `bool ⊂ int`, `None ⊂ Optional`, `isinstance` vs static type, mypy vs pyright divergence.
- **Async/sync boundary.** Helper async, dependency sync, or vice versa — where's the `await`? What about sync handlers (Flask) calling async helpers?
- **Async cancellation between awaits.** When a handler has `await A()` then `await B()`, what state is left if `CancelledError` strikes between them? Particularly load-bearing for write-followed-by-write sequences (DB write then telemetry, DB write then billing). Consider `asyncio.shield` or document the inconsistency.
- **Fixture autouse ordering and scope.** Autouse fixtures applied at the wrong scope leak into unrelated tests; explicit `@pytest.mark.usefixtures` on the test class is often safer than autouse.
- **`**kwargs` collisions.** Explicit named parameters silently eat their names from `**kwargs` passthrough — list reserved names or use an explicit `dict` parameter.
- **Wire-boundary type compatibility.** When crossing module boundaries (Python → gRPC, Python → JSON, Python → SQL): does the source field type match the sink schema? `UUID` vs `string`, `datetime` vs `Timestamp`, `Optional[int]` vs `NULLABLE INTEGER`. Pydantic types that auto-coerce in Python sometimes reject at the wire.
- **Unbounded I/O on user-perceived hot path.** Adding a network call to a request handler? Default to a timeout (3–5s for sync RPCs); document the choice. Without one, a single hung dependency = tenant-wide outage.
- **Test patch-target refactor.** When moving an import from module A to module B, every `@patch("A.symbol")` in tests becomes a no-op or `AttributeError`. List the patch targets that need to move. Vacuous patches don't fail loudly — coverage stays green, assertions stop measuring.
- **Deployment rollover semantics.** Does a Cloud Run / Kubernetes revision change leave in-flight state inconsistent? Old revision writes documents in old schema; new revision reads them in new schema. Sidecars and webhooks that read state written by a previous revision are especially load-bearing.
- **Heterogeneous existing surface.** Did the call-site survey confirm homogeneity, or are there N-1-vs-1 cases you need to handle differently?

---

## Phase 4 — Self-review + handoff

1. **Read it cold.** As if you'd never seen the task. Find at least 3 issues a senior reviewer would catch — fix them or document why they're acceptable. Common hits: weak tests (paranoia rather than behavior), vacuous test assertions (patches that no longer take effect, mocks that aren't checked, asserts on tautologies), magic strings, fragile fixture ordering, missing edge cases, scope creep, vague test names.
2. **Recommend `/review:my-developer-plan` or the `plan-reviewer` agent** at the end of your response. Independent eyes catch coupling and assumption errors that author-review misses.

---

## Skills to invoke during implementation
- `python-development` for Python projects
- `terraform-development` for Terraform projects
- `test-driven-development` for any production code

## DO NOT
- Do not include plans for legacy fallback unless required or explicitly requested.
- Fail fast and loud, avoid unnecessary error handling.
- Do not over-engineer abstractions.
- Avoid creating new types for interacting with third-party libraries when they already have their own.
- Do not use audience framing ("a junior would prefer", "more accessible", "easier to read") as justification for architectural decisions. Justify on engineering merits.

## Target Audience
Assume the implementer is a **competent engineer who knows the codebase but has not read the ticket or design doc.** They need enough context to implement without re-reading the source material — concrete file paths, full type signatures, explicit decision rationale. They do NOT need standard engineering practices explained. Make decisions on engineering merits; if a senior would call your decision wrong, a junior shouldn't get a different answer either.

## Tasks section format
End the plan with `## Tasks` using GitHub-checkbox markdown: `- [ ] N.M Title`. Two-level nesting (parent 1.0, sub 1.1, 1.2, ...). Parent tasks may stand alone if purely structural.

## Output
Store your plan in `/context/[nnn]-{feature|branch}/plan-[nnn].md`. Example: `/context/026-pricing-registry/plan-001.md`.
