# Final Report Format

Format for `/context/[nnn]-<slug>/feasibility-[nnn].md`. Read this when writing the final report in Step 4 of the workflow. Use the structure below exactly — Findings sections are present whether populated or not; Required Design Changes and Recommended Follow-ups are omitted entirely when empty.

````markdown
# <TDD Title> — Feasibility Study
**Version:** 1.0 | **Date**: YYYY-MM-DD | **Status**: Draft | Ready for Review

> Cold-read review of [`tdd-[nnn].md`](./tdd-[nnn].md)<and [`contracts-[nnn].md`](./contracts-[nnn].md) if present>.

## Verdict
**<one of: Feasible | Feasible with mitigations | Feasible pending empirical validation | Not feasible as designed | Inconclusive>**

<2-4 sentences: why this verdict, what it means for next steps, what the user is committing to by accepting it.>

## Scope
- **Reviewed**: tdd-[nnn].md (vX.Y), contracts-[nnn].md (vX.Y) <if read>, PRD <if read>, research <list of files if read>
- **Dimensions covered**: <from Step 1 selection>
- **Research depth**: <Quick | Standard | Deep>
- **Method**: Cold-read (`feasibility-cold-read`) + main-agent findings walk
- **Explicitly excluded**: <anything scoped out, with reason>

## Findings

### Show-stoppers
<Per finding:
#### <Concrete title>
- **Source**: TDD §<section> / contracts §<section>
- **Claim under scrutiny**: <verbatim or paraphrase>
- **Evidence**: <what research found, with URL(s) and date(s)>
- **PRD impact**: <which committed requirement or NFR is compromised, and how>
- **Disposition**: Requires redesign. <Which TDD/contracts section must change, and what must be true after the change.>>

### High Risks
<Same. Disposition: Accept as risk (with rationale) | Mitigation: <named> | Validate empirically (spike: <name>) | Requires redesign.>

### Medium Risks
<Same, terser. Include only Mediums where the user gave explicit disposition.>

### Low Risks / Notes
<Bulleted, one line each. Format: **<topic>**: <observation>. <source>.>

## Verified Claims
<Brief table of load-bearing claims confirmed by the cold-read research:
| Claim | TDD ref | Source | Notes |
Future readers know what was checked, not just what failed.>

## Inconclusive
<Claims research could not settle. Per item: source, what would settle it (named spike + success criterion), why it matters.>

## Required Design Changes
<Only populated if Verdict is "Not feasible as designed" or if a High finding's disposition was "Requires redesign". One bullet per change.
- **<TDD/contracts section>**: <what must change>. <Which Show-stopper or finding drives the change.>
Skip section entirely if no design changes are required.>

## Recommended Follow-ups
<Spikes, prototypes, benchmarks the user committed to. One bullet each:
- **<Spike name>**: <what to validate>. <Success criterion.> <Which finding this resolves.>
Skip section entirely if none.>

## Decisions Made During the Walk
<Flat bulleted list of the dispositions taken via AskUserQuestion. Format:
- **<finding title>**: <disposition chosen>. <rationale if not obvious>.
Includes interpretation resolutions from Step 3.1 alongside disposition choices.>
````
