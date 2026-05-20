# Contracts Walk

A second interactive pass after the design walk. Same `AskUserQuestion` discipline, separate output file: `/context/[nnn]-<slug>/contracts-[nnn].md`.

## Why a separate walk

The TDD operates at alignment altitude — components, contracts as *concepts*, invariants. Field-level shapes (IDL, request/response bodies, error envelope JSON, document schemas) live a layer below.

If you bake field shapes into the TDD, two things go wrong:
1. **Doc bloat.** Components stop being scannable; readers can't get the system shape from the headlines.
2. **Premature commitment.** Field-level decisions force architectural confrontations that the alignment altitude lets you skate past. Mixing them with design-level decisions makes both walks harder.

Putting contracts in a companion file solves both: the TDD stays terse; `contracts-[nnn].md` is where field-level commitments land.

## Why between Step 1 and Step 3 (not at the very end)

Writing field shapes forces architectural questions to surface — "wait, where does this URL come from? which service owns this config? why are these two methods doing the same thing?" These are **architectural** issues that the design walk missed because alignment altitude doesn't expose them.

If contracts run AFTER Final Pass, those discoveries become retro-patches against a "done" design. If contracts run BEFORE Final Pass, they feed back into design naturally — same cycle, no ceremony — and Final Pass then validates consistency across both files at once.

## What the walk does

1. **Asks whether contracts are needed.** Skips for designs that don't introduce new wire surfaces (UI-only changes, edits to an existing API, simple refactors).
2. **Surfaces wire conventions first.** A single batched `AskUserQuestion` for the cross-cutting decisions that govern every subsequent section. Which conventions are needed is derived from the surfaces present in the TDD, not pre-enumerated.
3. **Walks each contract surface** named in the TDD's Public Contract bullets — one section per surface. Same `AskUserQuestion` discipline as the design walk.
4. **Applies push-back when contracts reveal design issues.** When pinning a field shape exposes a layering problem, fix at the design layer first; then pin the contract. This is where the contracts walk earns its keep — design issues caught at field-shape time.

## Critical rules

- **No invented fields.** Every field comes from PRD, the TDD, decisions register, or `AskUserQuestion`. If it can't be sourced, ask.
- **One naming convention per wire surface.** Mixed casing within a single surface is a bug.
- **`AskUserQuestion` is the only sanctioned channel for contract decisions.** Same as design walk's Critical Rule 9.
- **Push-back fixes the design layer first.** Don't paper over architectural issues with contract gymnastics.

## What stays out

- Code bodies, file-by-file responsibilities, build steps, S/M/L estimates — same exclusions as the TDD.
- Design-level invariants — those belong in the TDD's Public Contract bullets, not duplicated here.
- Implementation choices that don't affect wire surface (internal data structures, in-memory caches, retry policies that don't change the contract) — planning territory.
