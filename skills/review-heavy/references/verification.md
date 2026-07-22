# Verification Pass

A cross-check gate that runs **after** aggregation and **before** the verdict and any posting. It
exists because a finding that reaches a human — and especially one **posted to a public PR** — must
be real. Precision beats recall here.

## When to run

- **Medium and High** tiers (see [risk-tiering.md](risk-tiering.md)).
- **Always** before posting (`--post`), regardless of tier.
- Skip only for the **Low** tier when not posting.

## How the orchestrator runs it

1. Take the **survivors** of the confidence filter + dedup + reasonableness steps (see
   [verdict-algorithm.md](verdict-algorithm.md) steps 2–4).
2. Invoke the `verification` subagent once, passing it the **absolute path to the shared context
   file** and the **candidate findings** (inline, or write them to a findings file and pass its
   path).
3. The subagent returns one verdict per candidate: **CONFIRM**, **ADJUST → severity/confidence**,
   or **DROP (reason)**.

## How to apply the results

- **CONFIRM** → keep the finding unchanged.
- **ADJUST** → update the finding's severity/confidence, then re-apply the confidence gate: if it
  now falls below 80, drop it.
- **DROP** → remove the finding entirely.

Only the **confirmed (and re-gated)** set proceeds to the verdict and, if requested, to posting.

## Guardrail

Verification never *adds* findings and never posts — it only confirms, rescopes, or removes. If the
subagent can't independently confirm a finding, that finding is dropped.
