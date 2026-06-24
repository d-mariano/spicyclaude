# Severity Rubric

Shared scoring for every reviewer. Each finding gets a **severity** and a **confidence**. The orchestrator surfaces only findings with confidence ≥ 80.

## Severity

- **Critical** — Outage, data loss or corruption, a concretely exploitable security flaw, or a broken build / failing test. **Blocks merge.**
- **High** — A measurable regression, a real bug that will be hit in practice, or a clear, quotable guideline / `CLAUDE.md` violation. **Blocks or strong gate.**
- **Medium** — Real but lower-impact or situational. **Advisory.**
- **Low** — Minor or nice-to-have. **Advisory; suppress if noisy.**

Severity is about impact if the finding is true. Confidence is about whether it is true. Score them independently.

## Confidence (0–100)

- **0–49** — Likely a false positive, pre-existing, or pure nitpick. Do not surface.
- **50–79** — Real but possibly a nitpick, or not fully verified. Do not surface.
- **80–90** — Important and verified against the actual diff.
- **91–100** — Critical, or an explicit, quotable guideline / `CLAUDE.md` violation.

**Surface only confidence ≥ 80.** When unsure, score lower — a missed nitpick costs nothing; a false alarm costs trust.

## Each finding carries

`severity` · `confidence` · `file:line` · `category` · concrete fix.
