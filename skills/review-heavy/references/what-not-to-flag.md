# What Not to Flag

Shared suppression list. Every reviewer reads this before returning findings. The goal is signal: a review full of noise gets ignored.

Do **not** flag:

- **Pre-existing issues in unchanged code.** Review only the changed lines. If the diff didn't touch it, it's out of scope.
- **Pedantic / style nits a linter catches.** Formatting, import order, naming style — the toolchain owns these.
- **Theoretical risks needing unlikely preconditions.** If exploiting or hitting it requires a chain of improbable events, skip it.
- **Defense-in-depth when a primary defense already exists.** Don't demand a second lock on a door that's already locked.
- **"Consider using library X" suggestions.** Don't relitigate dependency or tooling choices the change didn't raise.
- **Anything the repo's conventions explicitly allow.** If `CLAUDE.md` or established patterns sanction it, it is not a finding.

When a finding is borderline against this list, drop it or score it below 80. Suppression is the default; surface only what a reviewer would genuinely want to act on before merging.
