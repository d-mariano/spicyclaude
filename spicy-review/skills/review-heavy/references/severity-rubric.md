# Severity & Confidence Rubric

The single shared scale for every reviewer (light and heavy) and the orchestrator.
Each finding gets **one severity** and **one confidence score**. Do not invent other tiers.

## Severity

| Severity     | Meaning                                                                                                                                                              | Gate                     |
| :----------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------- |
| **Critical** | Outage, data loss/corruption, a concretely exploitable security flaw, or a broken build / failing test introduced by this change.                                   | **Blocks merge.**        |
| **High**     | A measurable regression, a real bug that will be hit in practice, or a clear, quotable guideline / `CLAUDE.md` violation.                                            | **Blocks / strong gate.**|
| **Medium**   | A real issue but lower-impact or situational — worth fixing, not a blocker.                                                                                          | Advisory.                |
| **Low**      | Minor / nice-to-have. Advisory; **suppress if it would make the report noisy.**                                                                                      | Advisory.                |

Rules of thumb:
- If you cannot name the concrete bad outcome, it is not Critical or High.
- "Could theoretically…" with unlikely preconditions is at most Low, and usually [not flagged at all](what-not-to-flag.md).
- A guideline violation only reaches **High** if you can quote the specific rule (from `CLAUDE.md` or an explicit repo convention).

## Confidence (0–100)

How sure are you that this is a *real, in-scope, worth-raising* problem — not a false positive or a nitpick.

| Score      | Meaning                                                                                                  |
| :--------- | :------------------------------------------------------------------------------------------------------ |
| **0**      | False positive, or the issue is pre-existing in code this change did not touch.                          |
| **~50**    | Real, but might just be a nitpick / matter of taste.                                                     |
| **80–90**  | Important and verified — you traced the code path and it holds up.                                       |
| **91–100** | Critical impact, or an explicit, quotable guideline violation.                                           |

## The confidence gate

**Surface only findings with confidence ≥ 80.** The orchestrator drops everything below 80
(see [verdict-algorithm.md](verdict-algorithm.md)). When in doubt, score lower and stay silent —
a missed nitpick is cheaper than a false alarm that erodes trust in the review.

## Required shape of every finding

```
- title:      minimal words naming the issue (becomes the bolded header when posted)
  severity:   Critical | High | Medium | Low
  confidence: 0-100
  location:   path/to/file.ext:LINE   (range if needed)
  category:   the reviewer's domain — mental-alignment | security | code-quality | documentation |
              tests | performance | deps | observability | simplification
  problem:    one or two sentences — the concrete bad outcome
  fix:        a specific, actionable change (not "consider improving")
```

## Rendering (report line)

Every report line — light's summary, heavy's terminal report, posted summary bullets — uses one
format:

```
- [NN] path:line — **Title.** problem. Fix: …
```

`NN` is the bare confidence number.

If you have nothing at or above the gate, say exactly: **"No concerns identified."**
