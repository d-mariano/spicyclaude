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
- **Sibling-ticket coupling.** For each sibling ticket this work blocks or unblocks: name the API surface they depend on; confirm your surface meets their needs. If you can't confirm, flag as a pre-merge check with whoever owns the sibling.

Keep these findings as a top-level "Pre-flight findings" section in the final plan — they document the assumptions the rest of the plan is built on.

---

## Phase 2 — Drafting the plan

Structure the plan with these sections in order:

- **Overview.** 2-3 sentences: what you're doing and why now.
- **Key decisions table.** Each row: decision + choice + one-line rationale. Surface deliberate divergences from the ticket/PRD AC here so reviewers see them upfront, not buried in a diff.
- **Pre-flight findings** (from Phase 1).
- **Files to change.** Group as NEW / MODIFIED / DELETED / NOT-modified-but-considered. For each: file path + concrete diff intent.
- **New functions and classes.** Write the **full signature with parameter types and return type**, not a description. If you can't write the signature, you don't understand the function yet. Add a 1-2 sentence docstring after each.
- **Test impact in three buckets:**
  - **ADD**: new tests, name + 5-10 words on behavior.
  - **MODIFY**: existing tests changing, what changes, why.
  - **DELETE**: existing tests being removed, what replaced them.
- **CLAUDE.md reinforcement.** Cite specific rules from project + global CLAUDE.md that constrain this work (clarity, simplicity, reuse, third-party usage).
- **Commit granularity.** State the number of commits and the boundary rationale. Mechanically-identical changes across N files often belong in one commit, not N.
- **Follow-up tickets to file.** One bullet per ticket: name, scope, why deferred. Don't let "later" be silent.
- **Stakeholder decisions needed before merge.** One bullet per decision: what's pending, who decides, default if no answer arrives.
- **Risks / things to surface in PR description.** What reviewers need to know when this lands.
- **Tasks section** (format below).

---

## Phase 3 — Footgun checklist (scan before declaring done)

Explicitly scan against these gotchas. For each that applies, document how the plan addresses it:

- **Module-import-time side effects.** Singletons, registries populated at bottom of module — what happens on re-import or under `pytest-randomly`?
- **Mutable global state in tests.** Fixtures, `monkeypatch`, isolation under `pytest-xdist` / `pytest-randomly` / re-ordering.
- **Type-narrowing edge cases.** `bool ⊂ int`, `None ⊂ Optional`, `isinstance` vs static type, mypy vs pyright divergence.
- **Async/sync boundary.** Helper async, dependency sync, or vice versa — where's the `await`? What about sync handlers (Flask) calling async helpers?
- **Fixture autouse ordering and scope.** Autouse fixtures applied at the wrong scope leak into unrelated tests; explicit `@pytest.mark.usefixtures` on the test class is often safer than autouse.
- **`**kwargs` collisions.** Explicit named parameters silently eat their names from `**kwargs` passthrough — list reserved names or use an explicit `dict` parameter.
- **Heterogeneous existing surface.** Did the call-site survey confirm homogeneity, or are there N-1-vs-1 cases you need to handle differently?

---

## Phase 4 — Self-review + handoff

After drafting, before reporting back:

1. **Read it cold.** As if you'd never seen the task. Find at least 3 issues a senior reviewer would catch — fix them or document why they're acceptable. Common hits: weak tests (paranoia rather than behavior), magic strings, fragile fixture ordering, missing edge cases, scope creep, vague test names.
2. **Recommend `/review:my-developer-plan` or the `plan-reviewer` agent** at the end of your response. Independent eyes catch coupling and assumption errors that author-review misses.

---

## Implementation
Use the python-development skill for Python projects.
Use the terraform-development skill for Terraform projects.

## Testing
Use the test-driven-development skill.

## DO NOT
- Do not include plans for legacy fallback unless required or explicitly requested.
- Fail fast and loud, avoid unnecessary error handling.
- Do not over-engineer abstractions.
- Avoid creating new types for interacting with third-party libraries when they already have their own.

## Target Audience
Assume the primary reader of the task list is a **junior developer** who will implement the feature with awareness of the existing codebase context. Concrete file paths, line numbers, and full type signatures beat generic descriptions every time.

## Tasks section format
The Tasks section must appear at the end of the file in this exact format:
```markdown
## Tasks
- [ ] 1.0 Parent Task Title
  - [ ] 1.1 [Sub-task description 1.1]
  - [ ] 1.2 [Sub-task description 1.2]
- [ ] 2.0 Parent Task Title
  - [ ] 2.1 [Sub-task description 2.1]
- [ ] 3.0 Parent Task Title (may not require sub-tasks if purely structural or configuration)
```

## Output
Store your plan in /context/[nnn]-{feature|branch}/plan-[nnn].md.

### Examples:
/context/001-implement-cool-service/plan-001.md
/context/001-implement-cool-service/plan-002.md
/context/002-next-neat-service/plan-001.md
