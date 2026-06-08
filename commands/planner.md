---
allowed-tools: AskUserQuestion, Glob, Grep, Read, Edit, TodoWrite, Write, WebFetch, WebSearch, Skill, Bash
argument-hint: [prd] [research]
description: Prepare a plan that implements the PRD or subcomponent that is informed by recent research.
---
You are a world class software engineer.

We are going to work on $1.

Make a detailed plan to accomplish this, based on $2.

Prioritize for rapid iteration and MVP development. Do NOT add scope.

---

## Phase 0 — Load skills

Before pre-flight, load the skills that will shape the plan.

**Available implementation skills** (the catalog the per-task `**Skills:**` field draws from):
- `test-driven-development` — for any production code
- `python-development` — for Python projects
- `terraform-development` — for Terraform projects

**Steps:**
1. **Always: `Skill(test-driven-development)`.** The plan's Test Impact section and tautology-detection logic depend on it (Phase 2 cites `test-driven-development/testing-principles.md` directly).
2. **Detect language now and load the matching skill:** `ls pyproject.toml *.tf 2>/dev/null` — if `pyproject.toml` is present, `Skill(python-development)`; if `*.tf` files are present, `Skill(terraform-development)`.
3. **Annotate every parent task's `**Skills:**` field** with the skills the implementer must load (subset of the catalog above). This is the contract `/execute` reads — a missing field will cause execute to fail loud.

---

## Phase 1 — Pre-flight survey (do this BEFORE drafting the plan)

Most planning bugs come from skipping this step. Read the relevant code and write a "Pre-flight findings" section that answers:

- **Call-site survey.** For each existing call site of code you're changing or extending: how does it currently behave on each axis you're changing? List heterogeneity explicitly. When extending a pattern across N call sites, the assumption that they're homogeneous is usually wrong — find the 1-of-N that breaks the pattern.
- **Existing-test impact.** For each existing test that touches state your changes affect (globals, singletons, fixtures, autouse): predict which break and how to fix them. Fixtures you add or modify will collide with existing tests that depend on the old fixture's behavior — name them.
- **Same-file sibling-test enumeration.** For every test file you're modifying, list ALL tests in the file in one of three buckets: CHANGED, UNCHANGED-but-named (so the implementer doesn't second-guess), UNCHANGED-irrelevant (don't enumerate). The cold-read implementer opens the file diff and wonders whether the tests you *didn't* touch should also have changed — the "do not touch these" list must be explicit, not implied.
- **Stale-reference grep.** For any symbol being renamed or removed, run `grep -rn <old-name>` across the whole project and triage every hit. Imports and call sites change automatically with the rename; comments, docstrings, log messages, error strings, and test names rot silently.
- **Sibling-ticket coupling.** For each sibling ticket this work blocks or unblocks: (a) name the API surface they depend on; confirm your surface meets their needs — if you can't confirm, flag as a pre-merge check with whoever owns the sibling; (b) **deployment-window risk** — what's the user-visible state of the system between this PR merging and the sibling landing? "It works" is a complete answer; so is "telemetry drops for tool X — acceptable pre-launch." Silence here is the bug.

Keep these findings as a top-level "Pre-flight findings" section in the final plan — they document the assumptions the rest of the plan is built on.

### Surfacing open questions before drafting

PRD/AC ambiguity, scope boundaries, and contradictory-source forks belong **upstream in research** — by the time the user reaches the planner, those should already be resolved. If you find unresolved upstream ambiguity here, that's a research-phase gap; flag it as such rather than re-litigating it now ("Recommend re-running `/research` to resolve: <list>; or commit to working assumptions and proceed").

After pre-flight is complete and before drafting Phase 2, surface every fork that **the pre-flight itself uncovered** in a **single batched `AskUserQuestion` call** (up to 4 questions per call; chain calls only if more remain). These are code-grounded discoveries the user couldn't have answered upstream because no one had read the code yet. Trigger on:

- **Call-site heterogeneity** — pre-flight found N-1-vs-1 cases and the right unification strategy isn't obvious.
- **Test-collision unification** — fixture/global-state changes will break existing tests and the right consolidation isn't obvious.
- **Sibling-ticket API surface mismatch** — pre-flight reveals the surface you'd build doesn't match what a sibling ticket needs.
- **Stale-reference triage** — `grep -rn <old-name>` returned hits in non-code surfaces (comments, log messages, error strings) where the right action varies per hit.
- **Pre-flight surfaced a stakeholder decision** — code reading reveals a constraint the PRD didn't anticipate.

Do NOT use `AskUserQuestion` for low-stakes choices the model can reasonably commit to and document.

Rules:

- **Provide 2-4 options per question.** Each option needs a one-line description.
- **Every option's description includes a counter.** Format: `"<implication> · Counter: <trade-off or objection>"`. If an option has no real counter, the option set needs rework.
- **Mark your recommendation** with "(Recommended)" only when you have a clear, evidence-backed lean from the inputs or pre-flight — not absence of contrary signal. The recommended option gets the strongest counter — the primary reason the user might reject it. **Place the recommended option first** in the options array.
- **`header` is hard-capped at 12 characters.** Pick a short tag ("Call sites", "Fixtures", "Refs"); don't write a sentence.
- **State why the question matters** in the question text — which pre-flight finding, sibling-ticket dependency, or test collision rides on it.
- **Always offer a defer path** unless the plan genuinely cannot proceed. Phrase: `"Defer — file under Stakeholder decisions needed before merge"`.
- **Options come from inputs only.** Don't draw on training-data preferences when proposing option sets. If inputs don't suggest any, that's an unknown — flag it, don't invent options.
- **Use `multiSelect: true`** when the choices are not mutually exclusive — e.g., "Which footgun categories apply?", "Which AC items need stakeholder clarification?", "Which existing tests will need updating?". Default `false` for picking-one decisions.
- **Do NOT add an "Other" option.** The tool surfaces a free-text input automatically; adding "Other" wastes one of the 4 option slots.
- **Use the `preview` field for concrete-shape choices** (single-select only). When the user is comparing artifacts — proposed function signatures, directory layout variants, sample test-name patterns, commit-message structures, file-grouping schemes — put an ASCII mockup or code snippet in each option's `preview` so the UI renders a side-by-side comparison. Skip preview for preference questions where label + description suffice. Previews are not supported for `multiSelect: true`.

Fold answers directly into the plan as you draft Phase 2. Any deferred questions land verbatim in the **Stakeholder decisions needed before merge** section.

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

1. **Read it cold.** As if you'd never seen the task. Find at least 3 issues a senior reviewer would catch — fix them or document why they're acceptable. Common hits: weak tests (paranoia rather than behavior), vacuous test assertions (patches that no longer take effect, mocks that aren't checked, asserts on tautologies), magic strings, fragile fixture ordering, missing edge cases, scope creep, vague test names, RGR opt-outs that don't actually qualify as config/type/rename, parent tasks missing Skills/Files/Depends-on metadata, AC gaps that weren't surfaced via Coverage Gap Handling.
2. **Recommend `/review:my-developer-plan` or the `plan-reviewer` agent** at the end of your response. Independent eyes catch coupling and assumption errors that author-review misses.

---

## DO NOT
- Do not include plans for legacy fallback unless required or explicitly requested.
- Fail fast and loud, avoid unnecessary error handling.
- Do not over-engineer abstractions.
- Avoid creating new types for interacting with third-party libraries when they already have their own.
- Do not use audience framing ("a junior would prefer", "more accessible", "easier to read") as justification for architectural decisions. Justify on engineering merits.

## Target Audience
Assume the implementer is a **competent engineer who knows the codebase but has not read the ticket or design doc.** They need enough context to implement without re-reading the source material — concrete file paths, full type signatures, explicit decision rationale. They do NOT need standard engineering practices explained. Make decisions on engineering merits; if a senior would call your decision wrong, a junior shouldn't get a different answer either.

## Tasks section format

End the plan with `## Tasks` using GitHub-checkbox markdown. Two-level nesting (parent 1.0, sub 1.1, 1.2, ...). `execute.md` walks subtasks sequentially and marks `[x]` as it goes — the format is the protocol.

### Per-task metadata (required)

Each parent task carries three fields so `execute.md` can load the right context without re-discovering it per task:

- **Skills**: which skills the implementer loads (subset of the catalog listed in Phase 0)
- **Files**: which files this task touches (matches the Files-to-change section)
- **Depends on**: parent task numbers this one waits for, or "None"

### Task granularity

Each subtask (1.1, 1.2, ...) should be:
- Completable in 15-30 minutes
- One RED/GREEN cycle
- Independently testable
- Atomic — can be committed alone

If a subtask doesn't fit those constraints, split it. If you can't write the GREEN signature yet, you haven't planned the task — go back to "New functions and classes."

### RED / GREEN / REFACTOR structure (default)

Every parent task with behavior change uses this structure. RED comes first because the test names are the planning artifact — they're how you prove the GREEN subtask is doing the right thing.

```markdown
- [ ] **1.0 Parent Task Title**
  - **Skills**: python-development, test-driven-development
  - **Files**: src/path/to/file.py, tests/path/to/test_file.py
  - **Depends on**: None
  - [ ] 1.1 RED: Write failing tests for {behavior}
    - `test_name` — the observable behavior change that would cause the test to fail (same rule as the Test Impact ADD bucket; tautologies are a smell)
  - [ ] 1.2 GREEN: Implement `func_name(self, arg: Type) -> ReturnType`
    - Implementation details — full signature lives in "New functions and classes"
  - [ ] 1.3 REFACTOR: Clean up (if needed) — omit the subtask if there's no clear cleanup
```

### TDD opt-out (narrow)

Mirroring the TDD skill's own exclusions: config-only changes, type-only definitions, and pure renames with no behavior change have no RED phase. The parent task documents the reason in place of the RED subtask:

```markdown
- [ ] **4.0 Rename `LegacyUser` → `User`**
  - **Skills**: python-development
  - **Files**: src/user/models.py, ...
  - **Depends on**: None
  - **No RED — pure rename, behavior unchanged; existing tests gate the change.**
  - [ ] 4.1 Rename and update imports
  - [ ] 4.2 Triage stale references from pre-flight grep
```

Use this sparingly. If you're tempted to opt out because the behavior is "obvious", you owe a RED test — the test is what proves your reading of "obvious" matches the code.

### Purely structural parents

Parents that exist only to group sub-tasks (no code, no tests of their own — e.g., "1.0 Documentation updates") may have sub-tasks without RED/GREEN/REFACTOR. State this explicitly: `**Structural parent — no test phase**`.

---

## Coverage Gap Handling

If the AC trace table — or your reading of the PRD/research — reveals AC items, behaviors, or surface areas the plan does not cover, **stop and confirm before finalizing**. Silent gaps are how scope cuts become bugs.

1. List every gap in a `## Coverage Gaps` section: item, type (AC / behavior / endpoint / component), and whether you suspect it's deferred-on-purpose or genuinely missed.
2. Use `AskUserQuestion` to confirm each gap is intentional. Apply the same question-quality rules from Phase 1 (counter format, "(Recommended)" only with evidence-backed lean, defer path, no "Other"). Reasonable options usually include:
   - **Defer to follow-up ticket** — out of scope this iteration · Counter: needs an explicit follow-up bullet
   - **Add to this plan** — expand scope · Counter: pushes ship date / breaks MVP discipline
   - **Already covered elsewhere** — point to where · Counter: requires the user to name the location
3. Fold answers in: confirmed deferrals go into "Follow-up tickets to file"; confirmed additions get new tasks; "already covered" gets a citation in the AC trace table.
4. Only then finalize the plan.

If no gaps surface from the AC trace, no confirmation step is needed — proceed directly.

---

## Output
Store your plan in `/context/[nnn]-{feature|branch}/plan-[nnn].md`. Example: `/context/026-pricing-registry/plan-001.md`.
