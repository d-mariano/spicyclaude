# What NOT to Flag

Shared suppression list. **Every reviewer reads this** and applies it before reporting.
A review that cries wolf is worse than no review. When a candidate finding matches anything
below, drop it (or score its confidence near 0 so the gate removes it).

## Do not flag

- **Pre-existing issues in unchanged code.** Review only what this change touches. If the line
  was already there and the diff didn't modify it, it's out of scope — even if it's wrong.
- **Pedantic / style nits a linter or formatter catches.** Whitespace, import order, quote
  style, naming preferences, line length. Tooling owns these, not the review.
- **Theoretical risks needing unlikely preconditions.** "If an attacker already had X and Y and
  the moon were full…" If the precondition is implausible in this codebase, skip it.
- **Defense-in-depth when a primary defense already exists.** Don't demand a second guard for a
  case the first guard already covers. Note it at most as Low, usually not at all.
- **"Consider using library X" suggestions.** Don't re-architect around a different dependency
  unless the current one is concretely broken or unsafe here.
- **Anything the repo's conventions explicitly allow.** If `CLAUDE.md`, a documented standard,
  or a clear established pattern in the codebase sanctions it, it is not a finding.
- **Speculative future-proofing.** "This won't scale when we have 10M users" is not a finding
  unless the change makes that outcome concrete and imminent.
- **Taste / cleverness debates with no correctness or maintainability cost.** State the rule you'd
  be enforcing; if you can't, it's taste.

## The test before you report anything

1. Did *this change* introduce or touch it? (No → drop.)
2. Can you name the concrete bad outcome? (No → drop or Low.)
3. Is your confidence ≥ 80 per the [rubric](severity-rubric.md)? (No → drop.)
4. Would a linter/formatter catch it? (Yes → drop.)

Only what survives all four belongs in the report.
