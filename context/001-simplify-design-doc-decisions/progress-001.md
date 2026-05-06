# Progress 001 — Simplify the design-doc skill's decision system

## Plan reference
`context/001-simplify-design-doc-decisions/plan-001.md`

## Relevant Files
- `skills/design-doc/SKILL.md` — rewritten in place (295 → 218 lines, -26%)

## Tasks

- [x] 1.0 Rewrite `skills/design-doc/SKILL.md`
  - [x] 1.1 Update frontmatter `description` (drop Decision Register mention; keep `name`, `when_to_use`, `allowed-tools`, `disable-model-invocation`, `argument-hint` unchanged)
  - [x] 1.2 Reword Critical Rule 8 to refer only to `design.md` (Rules 1–7, 9, 10 reworded only where they referenced the register)
  - [x] 1.3 Delete the entire `## The Decision Register` subsection
  - [x] 1.4 Reword `## Surfacing Decisions to the User`: question text uses topic names in plain English, not `D###` IDs; replaced "update the Decision Register row" with "fill in the relevant section of design.md"
  - [x] 1.5 Reword `## Push-Back Protocol`: targets are prior sections of design.md, the PRD, or the inputs
  - [x] 1.6 Replaced 5-phase workflow with 3-step workflow (Setup, Walk Sections, Final Pass)
  - [x] 1.7 Updated `## Document Format`: forbids inline `[D###]` references explicitly, adds `## Key Decisions` section before Open Questions, simplifies Open Questions table to `Question | Working Assumption | Resolve By`
  - [x] 1.8 Mermaid guardrails preserved verbatim (Critical Rule 10, lines 42–46)
- [x] 2.0 Verify the rewrite
  - [x] 2.1 Re-read SKILL.md against the verification checklist (all criteria met)
  - [x] 2.2 `wc -l` confirms 218 lines (target was 120–140; actual is higher because Document Format spec is preserved in full — that's the substance of the skill)
  - [x] 2.3 `git status` confirms only `skills/design-doc/SKILL.md` modified plus `context/` for planning artifacts
  - [ ] 2.4 (Skipped — optional sanity-run on a fabricated PRD; per CLAUDE.md "do not add scope")

## Verification results

- **Section structure check** (`grep '^#'`): exactly 3 workflow steps; Document Format contains all 9 standard sections plus Key Decisions and Open Questions
- **Register reference scan** (`grep -E 'Decision Register|decisions\.md|D[0-9]{3}|gate \(|Source field'`): zero matches
- **Mermaid guardrails check** (read lines 40–46): Critical Rule 10 preserved verbatim from original
- **Critical Rules sanity check**: 10 rules present (lines 31–46), no-silent-assumptions rule (Rule 1) intact, AskUserQuestion-only rule (Rule 9) intact

## Notes

- Markdown skill rewrite, no test suite. TDD/python-development/terraform-development skills not applicable.
- Final size 218 lines vs. plan estimate of ~120–140. The Document Format embedded template (lines 110–218) is preserved in full because it is the substance of the spec — trimming it would lose value. The reduction came from removing the Decision Register subsection, the seeding/coherence workflow steps, and condensing scattered prose.
- One commit covers the SKILL.md rewrite plus the planning artifacts in `context/001-simplify-design-doc-decisions/`.
- Existing artifact at `docs/design/job-processing-service/` left untouched as a historical record of the prior format.
