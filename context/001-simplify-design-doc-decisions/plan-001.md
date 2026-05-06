# Plan 001 — Simplify the design-doc skill's decision system

## Context

`skills/design-doc/SKILL.md` (295 lines) currently maintains a parallel "Decision Register" file (`decisions.md`) with numerically-ID'd rows (`D001`, `D002`, …) that downstream design-doc artifacts reference inline. In practice (see `docs/design/job-processing-service/design.md`), this produces prose like:

> `payload <= 256 KB [D018] · max_attempts default 5 cap 50 [D028 · D033]`

Those `[D###]` tags are noise to humans — they break reading flow, require cross-referencing a second file, and serve machine traceability over decision-maker comprehension.

User direction (locked in conversation):

- Ditch the Decision Register entirely (no `decisions.md`, no inline `[D###]`, no Source taxonomy)
- Build `design.md` section-by-section (no skeleton-with-`<!-- TBD -->` scaffolding)
- Optional Key Decisions summary at the end of `design.md`
- Open Questions section stays (with simplified columns)
- Workflow shrinks to 3 steps
- Scope is `skills/design-doc/SKILL.md` only — disregard `greenfield-design` and `feature-integration`

Intended outcome: a smaller, more usable design skill where the design doc is the only artifact, decisions appear where they apply, and the workflow's rigor (no silent assumptions, push-back, AskUserQuestion-only gates, working assumptions for deferrals) is preserved without the parallel-ledger ceremony.

## Blast radius

The design-doc skill is **standalone**:

- No slash command routes to it. `/design`, `/design-greenfield`, `/design-integrate` route to other skills.
- No agent invokes it.
- `settings.json` does not reference it.
- Frontmatter sets `disable-model-invocation: true` — Claude does not auto-invoke; the user explicitly invokes via the Skill tool.

Other files that mention `decisions.md` / `Decision Register` / `D###`:

- `docs/design/job-processing-service/*` — sample output of a prior run; left untouched as a historical artifact.
- `skills/greenfield-design/PROTOTYPE.md` — inactive prototype; explicitly out of scope.

Conclusion: rewriting `skills/design-doc/SKILL.md` has zero downstream impact.

## What changes

### File modified

- `skills/design-doc/SKILL.md` — rewritten in place

### Skills NOT applicable to this work

- `test-driven-development`, `python-development`, `terraform-development` — this is a markdown skill file, not production code. There is no test suite. Verification is by reading the rewritten SKILL.md against the checklist in the Verification section, plus an optional sanity-run.

## What survives the rewrite (with cosmetic rewords)

- **Frontmatter** — `name`, `when_to_use`, `allowed-tools`, `disable-model-invocation`, `argument-hint`. Only `description` changes (drops "Decision Register" mention).
- **Critical Rules 1–7, 9, 10** — registry-independent. Rule 8 reworded to refer only to `design.md` (not `decisions.md`).
- **Surfacing Decisions to the User** — `AskUserQuestion` conventions (batch up to 4, 2-4 options, mark Recommended with counter, defer paths, scope-creep flag) survive. One change: question text references topics in plain English, not register IDs.
- **Push-Back Protocol** — same protocol shape. Reword "Contradicts the register" → "Contradicts a prior section."
- **Document Format** — same section list (Goal, Architecture Overview, per-component sections, Data Flow, Data Model, Directory Structure, Cross-Cutting Concerns, Walking Skeleton Requirements, Implementation Phases, Open Questions). Two additions: explicit prohibition on inline `[D###]` references, and a new Key Decisions section at the end.
- **Mermaid guardrails** — preserved verbatim.

## What gets removed

- The entire `## The Decision Register` subsection (~50 lines)
- Status taxonomy (Decided / Deferred / Open)
- Source taxonomy (`PRD §X`, `PRD §X (ambiguous)`, `gate (research-rec)`, `gate (user-override)`, `gate (claude-synthesis)`, `gate (user-original)`)
- Workflow Step 1 ("Seed the Decision Register")
- Workflow Step 4 ("Coherence Pass" — replaced by an end-to-end re-read of `design.md`)
- "After every AskUserQuestion answer, update the Decision Register row in the same turn — including the Source field" coupling
- Phase tracking columns (Raised, Resolved)
- Critical Rule 8's reference to `decisions.md`
- The example Decision Register table
- The `ID` and `Source` columns from the Open Questions table

## What gets added

### New 3-step workflow

- **Step 0 — Setup**: determine task slug (from arg, PRD title, or `AskUserQuestion`), check `docs/design/<task-slug>/` for existing artifacts, prompt resume/restart/new-slug if files exist (`AskUserQuestion`), read inputs (PRD required or explicit spike-mode opt-in; research recommended; technical artifacts optional).
- **Step 1 — Walk sections in order**: for each section in the Document Format, identify decisions the section requires, surface unresolved decisions via `AskUserQuestion` (batched up to 4), apply push-back protocol when needed, write the section to `design.md` immediately. Architecture (section 2) is the first section with material decisions and resolves the architectural choice in flow.
- **Step 2 — Final pass**: read `design.md` end-to-end for contradictions; populate the Key Decisions summary section at the end; mark `Status: Ready for Review` in the header.

### New Key Decisions section in Document Format spec

- Flat bulleted list, one line per decision the user made via `AskUserQuestion`
- Format: `- **<topic 2-4 words>**: <choice>. <one-sentence rationale>.`
- PRD-given values that needed no decision are NOT listed (they're already cited in the relevant section's prose)
- No grouping, no tables, no Source field

### Reworded Open Questions section

Columns reduce to: `Question | Working Assumption | Resolve By` (drops `ID` and `Source`).

## Code snippets to guide the rewrite

New frontmatter `description`:

```yaml
description: "Create a technical design document from a PRD interactively. Walks design.md section-by-section, surfacing every choice via AskUserQuestion. Decisions live where they apply — no parallel register, no inline ID tags. Strict no-assumptions rule — unknowns become Open Questions with working assumptions, not silent defaults."
```

New Critical Rule 8 (save incrementally):

> 8. **Save artifacts incrementally.** Build `docs/design/<task-slug>/design.md` section-by-section as choices resolve. If the directory already has files, ask via `AskUserQuestion`: resume, restart (overwrite — confirm), or pick a new slug. Never silently overwrite.

Push-back protocol opener:

> When something doesn't make sense, surface it before recording. Push-back uses `AskUserQuestion` like all other decision channels. Targets: prior sections of `design.md`, the PRD, or the inputs themselves.

Question-text rule (replaces the "register IDs" mandate):

> **State which goal(s) the decision serves.** The question text must reference the PRD goal, NFR, use case, or related prior decisions in plain English (topic names, not codes). Example: `"Which tenant isolation mechanism? Addresses PRD §6.4 high-priority NFR; bears on the throughput targets and the architecture choice."`

Example Key Decisions section (illustrative — for the rewrite spec):

```markdown
## Key Decisions
- **Architecture**: Postgres-backed queue with worker pool. Throughput target sits within Postgres capability; SQL queryability serves status/replay use cases directly.
- **Worker model**: Tenant-provided workers connecting via mTLS. Avoids sandboxing complexity; aligns with org auth standard.
- **Payload cap**: 256 KB inline; tenants reference larger blobs via S3. Comfortable for Postgres row sizing.
```

## Junior-developer execution notes

- **Read the current `skills/design-doc/SKILL.md` end-to-end before editing.** It's 295 lines. Knowing what's there prevents accidentally deleting registry-independent rules.
- **Edit in place — no new files.** Do not create `decisions.md` examples, per-decision files, or anything in `docs/design/`.
- **Do NOT touch `docs/design/job-processing-service/`** — historical artifact.
- **Do NOT touch `skills/greenfield-design/` or `skills/feature-integration/`** — out of scope per user.
- **Frontmatter `disable-model-invocation: true` stays** — this skill is user-invoked only.
- After the rewrite, expect ~120–140 lines (down from 295).
- Prefer one Write rewrite over many small Edits if the changes are this widespread — it's easier to review the diff against the source than to follow a chain of 15 Edit operations.

## CLAUDE.md adherence

- **Delete more than you add** — net removal of ~150 lines.
- **KISS** — three-step workflow vs. five-phase scaffolded one.
- **No backwards compatibility** — old `decisions.md` files in `docs/design/job-processing-service/` are not migrated; they remain as historical artifacts. New runs simply don't produce a register.
- **One class per file / docblocks** — N/A (markdown).
- **No post-rationalizing rule violations** — the rewrite removes scaffolding, it does not loosen any rigor rule (no-silent-assumptions, push-back, defer-with-assumption all stay).

## Verification

After the rewrite, the implementer should:

1. **Re-read SKILL.md top-to-bottom against this checklist:**
   - No mention of `decisions.md`, `Decision Register`, `D###`, Source taxonomy, Status taxonomy, Phase tracking
   - Workflow has exactly 3 steps (Setup, Walk Sections, Final Pass)
   - Document Format lists the standard sections plus Key Decisions and the simplified Open Questions
   - Critical Rules 1–10 are present (with rewords) and the no-silent-assumptions rule (Rule 1) is intact
   - `AskUserQuestion` is still the only sanctioned channel for register-going decisions (now: section-going decisions)
   - Mermaid guardrails preserved verbatim

2. **Sanity-run the workflow on a small PRD** (real or fabricated 1-page PRD). Verify:
   - No `decisions.md` is created
   - `design.md` contains zero `[D###]` tags
   - Key Decisions section at the end summarizes the choices the user made via `AskUserQuestion`
   - Open Questions section captures any deferred items with working assumptions

3. **Diff line count.** Run `wc -l skills/design-doc/SKILL.md` before and after — expect ~120–140 lines after, down from 295.

4. **Confirm scope discipline.** `git status` should show only one modified file: `skills/design-doc/SKILL.md`. No new files, no edits to `docs/design/`, no edits to other skills.

## Tasks

- [ ] 1.0 Rewrite `skills/design-doc/SKILL.md`
  - [ ] 1.1 Update frontmatter `description` to drop Decision Register mention; keep `name`, `when_to_use`, `allowed-tools`, `disable-model-invocation`, `argument-hint` unchanged
  - [ ] 1.2 Reword Critical Rule 8 to refer only to `design.md` (not `decisions.md`); leave Rules 1–7, 9, 10 as-is in spirit (cosmetic rewords only where they reference the register)
  - [ ] 1.3 Delete the entire `## The Decision Register` subsection (header through the example table and Source values list)
  - [ ] 1.4 Reword the `## Surfacing Decisions to the User` section: question text uses topic names in plain English, not `D###` IDs; remove the "After every AskUserQuestion answer, update the Decision Register row" instruction (replace with "fill in the relevant section of design.md")
  - [ ] 1.5 Reword the `## Push-Back Protocol` section: targets become prior sections of `design.md`, the PRD, or the inputs — drop register-row references
  - [ ] 1.6 Replace the existing 5-phase workflow (Step 0 Setup, Step 1 Seed Register, Step 2 Architecture, Step 3 Walk, Step 4 Coherence, Step 5 Assemble) with the new 3-step workflow (Step 0 Setup, Step 1 Walk Sections, Step 2 Final Pass)
  - [ ] 1.7 Update the `## Document Format` spec: (a) explicitly forbid inline `[D###]` references in any section, (b) add a `## Key Decisions` section at the end (above Open Questions) with the bulleted-list format, (c) simplify the Open Questions table to `Question | Working Assumption | Resolve By` columns
  - [ ] 1.8 Confirm the Mermaid guardrails block is preserved verbatim (Rule 10)
- [ ] 2.0 Verify the rewrite
  - [ ] 2.1 Re-read SKILL.md top-to-bottom against the Verification checklist
  - [ ] 2.2 Run `wc -l skills/design-doc/SKILL.md` — expect ~120–140 lines
  - [ ] 2.3 Run `git status` and confirm only `skills/design-doc/SKILL.md` is modified
  - [ ] 2.4 (Optional) Sanity-run the workflow on a small fabricated PRD; confirm no `decisions.md` is produced and design.md contains no `[D###]` tags
