---
name: feasibility-study
description: "Pressure-tests a technical design document, runs research in a forked cold-read subagent, walks the user through findings, produces feasibility-[nnn].md. Use when reviewing a TDD, running a feasibility study, sanity-checking a design, or validating whether NFR targets are achievable with the chosen tech."
when_to_use: "Trigger phrases: 'review the TDD', 'is this design feasible', 'pressure-test this architecture', 'feasibility study for X', 'will this actually work at the target scale', 'do a design review', 'sanity-check the design', 'get a cold read', 'is the chosen stack going to handle this'."
disable-model-invocation: true
allowed-tools: Read Write Edit Glob AskUserQuestion Skill(feasibility-cold-read) WebSearch WebFetch
argument-hint: "[task-slug]"
---

# Feasibility Study Workflow

Pressure-test a technical design document. The design walk operates at alignment altitude on choices the user makes from available research — but research may have been incomplete, and choices made at alignment altitude don't always survive contact with field-level reality. This workflow is the "does this actually hold up?" check.

**The cold-read is structural.** Claim extraction and research happen in `feasibility-cold-read`, which runs in a forked context with no access to this conversation. A reviewer that hasn't seen the design built can't defend what it didn't help make, can't fall back on conversational context to fill gaps in the TDD, and has no rapport with the user that would soften an adversarial finding. This turns "don't re-litigate sound decisions" from discipline into mechanism — the cold-read only sees what the artifacts captured, which is the right pressure on design-doc to make artifacts stand alone.

This workflow does not redesign. The cold-read produces a findings draft; this skill walks the user through it via `AskUserQuestion` to dispose of every material finding (accept the risk, propose a mitigation grounded in evidence, validate empirically, or escalate back to the design-doc skill for redesign). Output: `/context/[nnn]-<slug>/feasibility-[nnn].md`.

## Inputs

In priority order:

1. **TDD** (required) — `/context/[nnn]-<slug>/tdd-[nnn].md`. The artifact under review.
2. **Contracts file** (recommended if present) — `/context/[nnn]-<slug>/contracts-[nnn].md`. Field-level wire shapes that may invalidate design-level claims.
3. **PRD** (recommended) — provides the NFR targets, constraints, and committed requirements the design must satisfy.
4. **Research** (recommended) — the research that informed the design.

The cold-read handles loading these. This wrapper just identifies the slug and passes scope.

## Severity Tiers

The cold-read assigns tiers; this skill adjudicates dispositions against them. Definitions are binding.

- **Show-stopper** — Evidence indicates the design as written cannot satisfy a committed PRD requirement, NFR target, or constraint. Requires redesign; cannot be accepted as a risk.
- **High** — Evidence indicates significant probability of failure or major operational burden. Acceptable only with an explicit mitigation grounded in research or an explicit, documented risk acceptance.
- **Medium** — Real concern with evidence behind it, but the design can absorb it. Acceptable with acknowledgment.
- **Low / Note** — Minor concern. Recorded but does not require disposition.

If the user's chosen disposition implies a downgrade ("just treat this Show-stopper as High"), refuse and surface via Push-Back Protocol.

## Verdict Spectrum

The Verdict section of the final report uses exactly one of these:

- **Feasible** — No Show-stoppers; High/Medium findings have user-confirmed dispositions; research-confirmed claims cover the load-bearing dependencies.
- **Feasible with mitigations** — As above, but explicit mitigations are required for one or more High findings. Mitigations listed with the findings.
- **Feasible pending empirical validation** — Critical claims are inconclusive after research; named spikes/prototypes are required before committing.
- **Not feasible as designed** — At least one Show-stopper. Required design changes listed. Skill stops; escalates to design-doc.
- **Inconclusive** — Research could not settle critical questions and the user opted not to commit to spikes. The report names what would need to be true for a verdict.

This skill is willing to deliver Not-Feasible. Do not soften Show-stoppers into High findings to avoid an uncomfortable verdict.

## Critical Rules

1. **No invented mitigations.** Mitigations come from the cold-read's findings, the existing design, or established patterns named in inputs. Don't fabricate one to give the user an easy out.
2. **`AskUserQuestion` is the only sanctioned channel for material decisions.** Disposition of every Show-stopper, High, and explicitly-accepted Medium goes through `AskUserQuestion`. Plain-text "I'm worried about Y" prompts don't count.
3. **Don't re-litigate sound decisions.** The cold-read only saw the artifacts; do not reintroduce conversational context to soften findings either. A finding requires *new* evidence — not "I would have chosen differently."
4. **Stay at design and contract altitude.** Critique architectural claims and contract-level commitments. Don't drift into implementation review.
5. **Identify, don't redesign.** When a finding requires a design change, name what must change and which TDD/contracts section owns it. Stop there; the user re-invokes the design-doc workflow.
6. **Honest uncertainty.** Inconclusive is a valid Verdict. Don't bluff to look decisive.

## Surfacing Findings to the User

`AskUserQuestion` is the only sanctioned channel for material findings (Show-stopper, High, and any Medium needing explicit acceptance).

- **Batch by tier.** Walk Show-stoppers first, then Highs, then Mediums needing disposition. Up to 4 findings per call.
- **Each finding presents the same option shape**:
  - **Accept as risk** — *for High/Medium only; never for Show-stoppers.* Records explicit user acceptance with rationale.
  - **Apply mitigation: <named mitigation>** — only offered if the cold-read draft surfaced a real mitigation. Mitigation is described concretely in the option label.
  - **Validate empirically (spike: <named spike>)** — for inconclusive items where a prototype would resolve it. The spike must have a concrete success criterion.
  - **Requires redesign** — escalates to design-doc. Required for any Show-stopper without a real mitigation or empirical path. The option label names which TDD/contracts section needs revisiting.
- **Every option's description includes a counter.** Format: `"<implication> · Counter: <trade-off or objection>"`. Non-recommended options state the key cost or risk of that path. If an option has no real counter, it's either the obvious choice (why offer alternatives?) or the option set needs rework.
- **Mark a recommended disposition** with "(Recommended)" when the cold-read draft's evidence clearly favors one option — not because it's the easiest path. The recommended option gets the strongest counter — the primary reason the user might reject it.
- **State the evidence in the question text, not just the label.** Format: `"<finding>. Evidence: <source + key fact>. PRD impact: <what's at risk>."` The user must see the evidence at the moment they choose.
- **Never invent option counts.** If only one real disposition exists (a true Show-stopper with no mitigation and no spike that would help), the question still goes through `AskUserQuestion` with the lone option plus "Defer — open discussion before recording" so the user explicitly acknowledges.

After every disposition, record it and move on.

## Push-Back Protocol

Push-back operates at two moments:

- **Interpretation walk (Step 3.1, structural).** When the cold-read draft flags an *Interpretation to Resolve*, present both candidate readings via `AskUserQuestion`. The user's choice either kills the candidate finding (claim was misread) or promotes it to the appropriate tier.
- **Disposition contradictions (Step 3 walk, conversational).** When the user's disposition contradicts the evidence on file (e.g., "just accept it" on a Show-stopper with no real mitigation, or "downgrade this to High"), re-ask: `"This finding's evidence indicates <X>; accepting without mitigation means committing to <Y>. Confirm: accept anyway (record as user-original deviation), or revisit the disposition?"` Do not silently record an unsafe disposition.

---

## Workflow

### Step 0: Setup

1. **Determine task slug.** If argument supplied, use it. Otherwise glob `/context/*/tdd-*.md` and ask via `AskUserQuestion` which feature folder to review (show the slug from the folder name and the latest TDD index in each).
2. **Resolve feature folder.** Glob `/context/*-<slug>/`. Single match: reuse. Multiple: ask. No match: hard-stop — feasibility-study requires a TDD that already exists; suggest running design-doc first.
3. **Pick TDD version to review.** Glob `/context/[nnn]-<slug>/tdd-*.md`. If multiple, ask via `AskUserQuestion` which (default to highest index). The feasibility report uses the same index: `feasibility-[nnn].md`.
4. **Check for prior runs.**
   - If `feasibility-[nnn].md` exists and is `Ready for Review`: ask: replace, or write `feasibility-[nnn]-v2.md` as a re-review.
   - If `.feasibility-[nnn]-draft.md` exists (interrupted prior run): ask: resume the findings walk from this draft, or restart (re-run the cold-read).

### Step 1: Scope and Depth

Single batched `AskUserQuestion` call:

1. **Dimensions to focus on** (multi-select) — derived from what the TDD actually contains. If the TDD has no external integrations, don't offer "integrations." Candidates: performance & scalability, external integrations, operational & deployment, security & compliance, cost, data model & access patterns, failure modes & recovery. Always offer "all critical dimensions" as a single option.
2. **Research depth** — Quick (verify only claims tied to committed PRD requirements), Standard (verify load-bearing claims), Deep (verify every external dependency and named technology, including versions).
3. **Specific concerns to investigate** — open-text via Other on a question presenting any concerns the user voiced earlier in the conversation as pre-filled options. Skip if none.

Brief sanity check: if the PRD has aggressive NFRs (named scale numbers, tight latency budgets) and the user picked Quick, push back once: `"Your PRD has load-bearing NFRs; Quick depth may miss Show-stoppers tied to them. Confirm Quick, or upgrade to Standard?"` Accept whatever they pick after that.

Record the chosen scope. It feeds the cold-read invocation in Step 2.

### Step 2: Invoke `feasibility-cold-read`

1. **Tell the user what's about to happen.** Brief framing: *"Spawning a cold-read in a forked context — fresh reviewer, no conversation history. This will take a few minutes."* Do not narrate further while it runs.
2. **Invoke `feasibility-cold-read` via the Skill tool**, passing the slug as positional argument and the scope as additional prompt context: dimensions selected, research depth chosen, specific concerns from the user. The cold-read writes `.feasibility-[nnn]-draft.md` and returns a summary.
3. **Validate the return.** Confirm the draft file exists and is well-formed (has Findings, Verified Claims, Inconclusive, Interpretations to Resolve sections). If the cold-read reported a failure (couldn't find TDD, ambiguous slug, web research blocked), surface to the user and stop — do not paper over.
4. **Read the draft into context.** This is your primary artifact for Step 3. You may read specific TDD/contracts sections on demand during the walk if the user asks "what does §X actually say?" — but do not re-extract claims or initiate new lines of research from the original artifacts. The point is to preserve the cold-read's adversarial posture, not to wall the TDD off entirely.

### Step 3: Findings Walk

Order is fixed: interpretations first, then findings by tier.

1. **Resolve interpretations.** For each item in *Interpretations to Resolve*, present both candidate readings via `AskUserQuestion`. The user's choice either kills the candidate finding (claim was misread) or promotes it to the appropriate tier. Update the working copy of the draft as choices land.
2. **Walk Show-stoppers.** Every Show-stopper requires disposition. Apply Surfacing Findings rules. For any Show-stopper without a real mitigation or spike path: disposition is "Requires redesign" — proceed but flag that the final Verdict will be Not-feasible.
3. **Walk Highs.** Same protocol. Disposition options vary by what the draft surfaced.
4. **Walk Mediums needing explicit acceptance** (those where the draft's proposed disposition was *Accept as risk* with non-trivial implications). Mediums marked as informational pass through without disposition.
5. **Push back on contradictory dispositions** per the Push-Back Protocol. Do not record a disposition that contradicts the evidence on file.

Throughout: if the user asks for clarification or wants to verify a specific source, you may run a focused WebSearch / WebFetch and present what it finds — but this is verification of the cold-read draft, not new research lines.

### Step 4: Final Report

1. **Determine the Verdict** from the disposed findings:
   - Any Show-stopper with disposition "Requires redesign" → **Not feasible as designed**.
   - High findings with mitigations applied, no unresolved Show-stoppers → **Feasible with mitigations**.
   - Any "validate empirically" dispositions on critical claims → **Feasible pending empirical validation**.
   - Critical claims still Inconclusive with no spike committed → **Inconclusive**.
   - Otherwise → **Feasible**.
2. **Write `/context/[nnn]-<slug>/feasibility-[nnn].md`** per [FINAL_REPORT_FORMAT.md](FINAL_REPORT_FORMAT.md). Pull verified claims and inconclusive items straight from the draft; pull findings with their user-confirmed dispositions.
3. **Delete `.feasibility-[nnn]-draft.md`** once the final report is written.
4. **Update the header** with final Status (`Ready for Review`) and date.
5. **Present the summary**: path to the feasibility file, the Verdict, and Findings counts per tier inline. If Verdict is Not-feasible, name the specific TDD/contracts sections the user should re-walk via design-doc.
