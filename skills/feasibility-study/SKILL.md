---
name: feasibility-study
description: "Pressure-test a technical design document for feasibility via a cold-read subagent — spawn a fresh-context reviewer to extract claims and verify them via web research, then walk the user through every material finding for disposition. The cold read is structural: a subagent that didn't help build the design can't defend it. Produces feasibility-[nnn].md as a companion to the TDD. Willing to deliver a Not-Feasible verdict; willing to escalate back to design-doc when redesign is needed."
when_to_use: "User wants to validate that a technical design will actually work, do a design review, run a feasibility study, pressure-test a TDD, get a cold read on the design, or check whether an architecture's NFR targets are achievable with the chosen tech. Examples: 'review the TDD', 'is this design feasible', 'pressure-test this architecture', 'feasibility study for X', 'will this actually work at the target scale', 'do a design review', 'sanity-check the design', 'get a cold read', 'is the chosen stack going to handle this'."
allowed-tools: Read Write Edit Glob AskUserQuestion Task WebSearch WebFetch
disable-model-invocation: true
argument-hint: "[task-slug]"
---

# Feasibility Study Workflow

Pressure-test a technical design document via a cold-read subagent. The design walk operates at alignment altitude on choices the user makes from available research — but research may have been incomplete, and choices made at alignment altitude don't always survive contact with field-level reality. This workflow is the "does this actually hold up?" check.

**The cold read is structural.** Claim extraction and research happen in a fresh-context subagent that did not help build the design. A subagent reading the artifacts cold can't defend what it didn't help make, can't fall back on conversational context to fill in gaps in the TDD, and has no rapport with the user that would soften an adversarial finding. This turns Critical Rule 4 ("don't re-litigate sound decisions") from discipline into mechanism — the subagent only sees what the artifacts captured, which is the right pressure on design-doc to make artifacts stand alone.

This workflow does not redesign. The subagent produces a findings draft; the main agent walks the user through it via `AskUserQuestion` to dispose of every material finding (accept the risk, propose a mitigation grounded in evidence, validate empirically, or escalate back to the design-doc skill for redesign). Output: `/context/[nnn]-<slug>/feasibility-[nnn].md`.

## Inputs

In priority order:

1. **TDD** (required) — `/context/[nnn]-<slug>/tdd-[nnn].md`. The artifact under review. Everything checked traces back to a claim or omission in this file.
2. **Contracts file** (recommended if present) — `/context/[nnn]-<slug>/contracts-[nnn].md`. Field-level wire shapes that may invalidate design-level claims.
3. **PRD** (recommended) — provides the NFR targets, constraints, and committed requirements the design must satisfy. Without it, feasibility becomes internal-consistency-only.
4. **Research** (recommended) — the research that informed the design. Knowing what's already been validated prevents re-litigating settled questions and points the deep research at the unvalidated gaps.

If only the TDD is available, proceed but flag in the report that PRD-grounded verification was out of reach.

## Severity Tiers

Every finding gets exactly one tier. Definitions are binding — don't tier on vibes.

- **Show-stopper** — Evidence indicates the design as written cannot satisfy a committed PRD requirement, NFR target, or constraint. Requires redesign; cannot be accepted as a risk. *Example: design targets 50k writes/sec on a single Postgres primary; benchmarks indicate ceiling ~10k writes/sec at the workload shape implied.*
- **High** — Evidence indicates significant probability of failure or major operational burden. Acceptable only with an explicit mitigation grounded in research or an explicit, documented risk acceptance. *Example: chosen library's last release was 3 years ago and a known issue affects the use case.*
- **Medium** — Real concern with evidence behind it, but the design can absorb it. Acceptable with acknowledgment in Open Questions or follow-ups. *Example: integration partner's webhook delivery SLA is looser than the PRD's responsiveness target implies.*
- **Low / Note** — Minor concern, idiomatic improvement, or future-watch item. Recorded but does not require disposition.

## Verdict Spectrum

The Verdict section of the report uses exactly one of these:

- **Feasible** — No show-stoppers; high/medium findings (if any) have user-confirmed dispositions; research-confirmed claims cover the load-bearing dependencies.
- **Feasible with mitigations** — As above, but explicit mitigations are required for one or more high findings. Mitigations listed with the findings.
- **Feasible pending empirical validation** — Critical claims are inconclusive after research; named spikes/prototypes are required before committing.
- **Not feasible as designed** — At least one show-stopper. Required design changes listed. Skill stops; escalates to design-doc.
- **Inconclusive** — Research could not settle critical questions and the user opted not to commit to spikes. The report names what would need to be true for a verdict.

This skill is willing to deliver Not-Feasible. Do not soften show-stoppers into high findings to avoid an uncomfortable verdict.

## Critical Rules

1. **Evidence over opinion.** Every finding cites a real source: primary docs, published benchmarks, RFC, post-mortem, issue tracker, the TDD itself. "In my experience" is not a source. "This might be slow" is not a finding. If a concern can't be sourced, it doesn't appear in the report. *Applies to both subagent (when filing findings) and main agent (when adjudicating dispositions).*
2. **No invented mitigations.** Mitigations come from research, the existing design, or established patterns named in inputs. Don't fabricate a library, technique, or "just do X" that the inputs and research don't support. If no real mitigation exists, the finding stands unmitigated.
3. **`AskUserQuestion` is the only sanctioned channel for material decisions.** Same channel discipline as design-doc. Disposition of every Show-stopper, High, and explicitly-accepted Medium goes through `AskUserQuestion`. Plain-text "I'm worried about Y" prompts don't count.
4. **Don't re-litigate sound decisions.** The subagent only sees the artifacts; the main agent must not re-introduce conversational context to soften findings either. A finding requires *new* evidence the design walk didn't have — not "I would have chosen differently." Discomfort with a choice is not a finding.
5. **Stay at design and contract altitude.** Critique architectural claims and contract-level commitments. Don't drift into code-style critique or hypothetical implementation bugs — that's review territory.
6. **Identify, don't redesign.** When a finding requires a design change, name what must change and which TDD/contracts section owns it. Stop there; the user re-invokes the design-doc workflow to apply the change.
7. **Honest uncertainty.** "Research couldn't reach a verdict" is a valid output, named explicitly. Don't bluff a conclusion to look decisive.
8. **The subagent boundary is one-way.** The subagent runs to completion and returns a draft. It cannot ask the user questions. Any ambiguity it cannot resolve from the artifacts is recorded in the draft's *Interpretations to Resolve* section for the main agent to walk via `AskUserQuestion` before dispositions begin.

## Claim Extraction Targets

The subagent scans the TDD and contracts file for claims in these categories. Each extracted claim is tagged load-bearing (per the chosen depth) or incidental. Load-bearing claims get researched; incidentals are noted but not chased. *This section gets inlined into the subagent prompt verbatim — the subagent has no other source for it.*

- **Performance claims** — anything implying a rate, latency, throughput, concurrency, or scale figure. Includes PRD NFR targets restated in the TDD.
- **Technology claims** — every named library, framework, service, protocol, and version. Each is a claim that the chosen tech can do what the design needs it to.
- **Integration claims** — every external system contract: behavior, SLA, error semantics, rate limits, auth flow, delivery guarantees.
- **Architectural claims** — patterns named in the design ("eventually consistent", "horizontally scalable", "exactly-once delivery", "stateless workers") that imply guarantees research can check.
- **Data claims** — claims about storage capacity, access patterns, indexing strategies, consistency models, retention.
- **Operational claims** — claims about observability, deployment, failure handling, recovery, runbooks.
- **Omissions** — beyond explicit claims, scan for things research suggests *should* have been addressed: missing failure modes for named integrations, absent backpressure handling on async boundaries, no mention of a known operational pitfall of the chosen tech. Omissions become findings at the appropriate tier with the source cited.

## Research Discipline

Applies to the cold-read subagent. The main agent may run ad-hoc verification searches during the findings walk if a user pushes back, but the bulk of research happens in the subagent.

- **Research only the load-bearing claims by default.** Load-bearing = tied to a committed PRD requirement, a named technology version, an NFR target, or a non-trivial external dependency. Adjust depth per the user's Step 1 selection.
- **Productive queries are specific.** "Library X version Y rate limit" beats "is library X fast." "Stripe webhook delivery SLA" beats "is Stripe reliable." Quote version numbers when present in the TDD.
- **Prefer primary sources.** Vendor docs, RFCs, official changelogs, the project's own GitHub issues, peer-reviewed benchmarks. Blog posts and forum threads are corroboration, not authority. Cite dates — a 2019 benchmark of a 2024 release is junk.
- **Give up after 3-4 searches.** If the question can't be settled with focused queries, it's likely inherently empirical (workload-specific performance, integration-specific behavior). Flag as Inconclusive and recommend a spike.
- **Don't research what's already validated.** If the supplied research already settled a question, cite the research and move on.
- **Read the TDD and contracts in full before searching the web.** Sometimes the "claim" is already qualified elsewhere in the design — the cold-read subagent has no conversational shortcut, so re-reading is the only way to catch this.

## Surfacing Findings to the User

`AskUserQuestion` is the only sanctioned channel for material findings (Show-stopper, High, and any Medium the user must explicitly accept).

- **Batch by tier.** Walk Show-stoppers first, then Highs, then Mediums needing disposition. Up to 4 findings per call.
- **Each finding presents the same option shape**:
  - **Accept as risk** — *for High/Medium only; never for Show-stoppers.* Records explicit user acceptance with rationale in the report.
  - **Apply mitigation: <named mitigation>** — only offered if the subagent's draft surfaced a real mitigation. Mitigation is described concretely in the option label.
  - **Validate empirically (spike: <named spike>)** — for inconclusive items where a prototype would resolve it. The spike must have a concrete success criterion.
  - **Requires redesign** — escalates to design-doc. Required for any Show-stopper without a real mitigation or empirical path. The option label names which TDD/contracts section needs revisiting.
- **State the evidence in the question text, not just the label.** Format: `"<finding>. Evidence: <source + key fact>. PRD impact: <what's at risk>."` The user must see the evidence at the moment they choose.
- **Never invent option counts.** If only one real disposition exists (a true Show-stopper with no mitigation and no spike that would help), the question still goes through `AskUserQuestion` with the lone option plus "Defer — open discussion before recording" so the user explicitly acknowledges.

After every disposition, record it in the relevant Findings subsection and move on.

## Push-Back Protocol

Push-back operates at two distinct moments in this workflow:

- **Inside the subagent (interpretation flagging).** When the subagent's research seems to contradict a TDD claim but the claim could plausibly be misread, the subagent does NOT file a finding. It records the ambiguity in the draft's *Interpretations to Resolve* section with both candidate readings and the evidence for each. The main agent walks these first.
- **Inside the main agent (disposition contradictions).** When the user's disposition contradicts the evidence on file (e.g., "just accept it" on a Show-stopper with no real mitigation), the main agent re-asks via `AskUserQuestion`: `"This finding's evidence indicates <X>; accepting without mitigation means committing to <Y>. Confirm: accept anyway (record as user-original deviation), or revisit the disposition?"` Do not silently record an unsafe disposition.

Interpretation push-back is structural (the subagent can't pause for input). Disposition push-back is conversational (the main agent can). Both feed the audit trail.

## Cold-Read Subagent

The subagent is invoked via the `Task` tool with a self-contained prompt. The subagent reads only what the prompt names — it does not have access to the conversation. This is the point.

**Prompt template** (filled in by the main agent in Step 2; everything in `<...>` gets substituted, every `[...]` section gets *inlined verbatim* from this SKILL.md):

```
You are performing a COLD-READ feasibility study on a technical design.
You have not seen this design before. You have no conversational context.
Your only inputs are the files named below.

ARTIFACTS:
- TDD: <absolute path>
- Contracts: <absolute path or "none">
- PRD: <absolute path or "none">
- Prior research: <list of paths or "none">

SCOPE (from the user via the main agent):
- Dimensions to examine: <user's selection>
- Research depth: <Quick | Standard | Deep>
- Specific concerns to investigate: <user's text or "none">

YOUR TASK:
1. Read every artifact in full. Do not skim.
2. Extract claims per [Claim Extraction Targets, inlined below].
3. For load-bearing claims (per the chosen depth), verify via WebSearch / WebFetch per [Research Discipline, inlined below].
4. Synthesize findings with binding severity tiers per [Severity Tiers, inlined below].
5. Flag interpretation ambiguities you cannot resolve from the artifacts.
6. Write the draft to: <absolute path to .feasibility-[nnn]-draft.md>

HARD RULES (the report relies on these):
- Every finding cites a real source (primary docs, benchmarks, RFCs, the TDD itself). No vibes.
- Mitigations come from research or the design only — never invent one.
- Tier on the binding definitions, not your preferences. Show-stoppers are evidence-of-failure, not strong unease.
- If you cannot settle a claim after 3-4 focused searches, mark it Inconclusive and name what spike would settle it.
- You CANNOT ask the user anything. Ambiguities go in *Interpretations to Resolve*, not in findings.

[Claim Extraction Targets — inline copy from skill]
[Severity Tiers — inline copy from skill]
[Research Discipline — inline copy from skill]
[Findings draft format — inline copy from skill's Document Format section]
```

**Subagent tools**: Read, Glob, WebSearch, WebFetch, Write. No `AskUserQuestion` — the subagent cannot pause for user input by construction.

**On return**: the subagent finishes when the draft file is written. The main agent reads the draft and proceeds to Step 3.

---

## Workflow

### Step 0: Setup

1. **Determine task slug.** If argument supplied, use it. Otherwise glob `/context/*/tdd-*.md` and ask via `AskUserQuestion` which feature folder to review (show the slug from the folder name and the latest TDD index in each).
2. **Resolve feature folder.** Glob `/context/*-<slug>/`. Single match: reuse. Multiple: ask. No match: hard-stop — feasibility-study requires a TDD that already exists; suggest running design-doc first.
3. **Pick TDD version to review.** Glob `/context/[nnn]-<slug>/tdd-*.md`. If multiple, ask via `AskUserQuestion` which (default to highest index). The feasibility report uses the same index: `feasibility-[nnn].md`.
4. **Check for prior runs.**
   - If `feasibility-[nnn].md` exists and is `Ready for Review`: ask: replace, or write `feasibility-[nnn]-v2.md` as a re-review.
   - If `.feasibility-[nnn]-draft.md` exists (interrupted prior run): ask: resume the findings walk from this draft, or restart (re-spawn subagent).
5. **Identify adjacent inputs.** Glob the folder for `contracts-[nnn].md`, PRD candidates, and research files. Note which were found — this drives the Scope section of the report and the subagent's input list.

### Step 1: Scope and Depth

Single batched `AskUserQuestion` call:

1. **Dimensions to focus on** (multi-select) — derived from what the TDD actually contains. If the TDD has no external integrations, don't offer "integrations." Candidates: performance & scalability, external integrations, operational & deployment, security & compliance, cost, data model & access patterns, failure modes & recovery. Always offer "all critical dimensions" as a single option.
2. **Research depth** — Quick (verify only claims tied to committed PRD requirements), Standard (verify load-bearing claims per Research Discipline), Deep (verify every external dependency and named technology, including versions).
3. **Specific concerns to investigate** — open-text via Other on a question presenting any concerns the user voiced earlier in the conversation as pre-filled options. Skip if none.

Record the chosen scope. It feeds the subagent prompt in Step 2.

### Step 2: Spawn Cold-Read Subagent

1. **Build the subagent prompt** per the Cold-Read Subagent template above, substituting the resolved paths and the Step 1 scope. Include the full findings-draft format inline — the subagent has no other source for it.
2. **Invoke via the `Task` tool.** Brief the user: *"Spawning a cold-read subagent to extract claims and verify them. This will take a few minutes."* Do not narrate further while it runs.
3. **On completion**, confirm `.feasibility-[nnn]-draft.md` exists and is well-formed (has Findings, Verified Claims, Inconclusive, and Interpretations to Resolve sections). If malformed, re-spawn with a corrective addendum to the prompt naming the missing section.
4. **Read the draft into context.** The draft becomes the main agent's primary artifact for Step 3 — claim extraction and research are not redone. The main agent may read specific TDD/contracts sections on demand if the user asks "what does §X actually say?" during disposition, but does not re-extract claims or initiate new lines of research from the original artifacts. The point is to preserve the cold read's adversarial posture, not to wall the TDD off entirely.

### Step 3: Findings Walk

Order is fixed: interpretations first, then findings by tier.

1. **Resolve interpretations.** For each item in *Interpretations to Resolve*, present both candidate readings via `AskUserQuestion`. The user's choice either kills the candidate finding (claim was misread) or promotes it to the appropriate tier. Update the working copy of the draft as choices land.
2. **Walk Show-stoppers.** Every Show-stopper requires disposition. Apply Surfacing Findings rules. Required for any Show-stopper without a real mitigation or spike path: disposition is "Requires redesign" — proceed but flag that the final Verdict will be Not-feasible.
3. **Walk Highs.** Same protocol. Disposition options vary by what the draft surfaced.
4. **Walk Mediums needing explicit acceptance** (those where the draft's proposed disposition was *Accept as risk* with non-trivial implications). Mediums marked as informational pass through without disposition.
5. **Push back on contradictory dispositions** per the Push-Back Protocol. Do not record a disposition that contradicts the evidence on file.

Throughout: if the user asks for clarification or wants to verify a specific source, the main agent may run a focused WebSearch / WebFetch and present what it finds — but this is verification of the subagent's draft, not new research.

### Step 4: Final Report

1. **Determine the Verdict** from the disposed findings:
   - Any Show-stopper with disposition "Requires redesign" → **Not feasible as designed**.
   - High findings with mitigations applied, no unresolved Show-stoppers → **Feasible with mitigations**.
   - Any "validate empirically" dispositions on critical claims → **Feasible pending empirical validation**.
   - Critical claims still Inconclusive with no spike committed → **Inconclusive**.
   - Otherwise → **Feasible**.
2. **Write `/context/[nnn]-<slug>/feasibility-[nnn].md`** per the Document Format below. Pull verified claims and inconclusive items straight from the draft; pull findings with their user-confirmed dispositions.
3. **Delete `.feasibility-[nnn]-draft.md`** once the final report is written.
4. **Update the header** with final Status (`Ready for Review`) and date.
5. **Present the summary**: path to the feasibility file, the Verdict, and Findings counts per tier inline. If Verdict is Not-feasible, name the specific TDD/contracts sections the user should re-walk via design-doc.

---

## Document Format

### Findings draft (subagent output, ephemeral)

`/context/[nnn]-<slug>/.feasibility-[nnn]-draft.md`. Deleted after the final report is written.

````markdown
# <TDD Title> — Feasibility Draft (cold read)
**Generated**: YYYY-MM-DD by cold-read subagent
**Inputs read**: <list of files with paths>
**Scope**: <dimensions, depth, specific concerns from Step 1>

## Interpretations to Resolve
<One H3 per ambiguity. Format:
### <Short title>
- **TDD claim**: <verbatim or paraphrase + section ref>
- **Apparent contradiction**: <what research suggests, with source>
- **Candidate reading A**: <interpretation> → if true, this is <not a finding | a Medium | a High | a Show-stopper>
- **Candidate reading B**: <interpretation> → if true, this is <...>
Skip section entirely if none.>

## Findings

### Show-stoppers
<Per-finding format: title, source, claim, evidence (with URLs + dates), PRD impact, proposed disposition options the main agent should offer. NO disposition recorded yet.>

### High Risks
<Same.>

### Medium Risks (needing explicit acceptance)
<Same.>

### Medium / Low (informational)
<Bullets, no disposition needed.>

## Verified Claims
<Table: claim | TDD ref | source | notes.>

## Inconclusive
<Per item: claim, source, what would settle it (named spike + success criterion), why it matters.>

## Omissions Noted
<Things the TDD should have addressed but didn't — missing failure modes, absent backpressure handling, known operational pitfalls of the chosen tech. Each cites a source.>
````

### Final report

`/context/[nnn]-<slug>/feasibility-[nnn].md`.

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
- **Method**: Cold-read subagent + main-agent findings walk
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
