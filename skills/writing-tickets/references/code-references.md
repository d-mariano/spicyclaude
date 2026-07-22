# Code & file references in tickets

How to reference code so the ticket stands on its own — actionable by an agent or engineer who has only the ticket, not this conversation or your working copy.

## The format

Pair the short path with a SHA-pinned permalink:

> `src/payments/idempotency.ts` ([permalink](https://github.com/org/repo/blob/a1b2c3d/src/payments/idempotency.ts#L42-L67))

- The path serves readers working inside the repo; the permalink serves everyone else and names the repo.
- Name symbols in prose (`extractIdempotencyKey`), don't lean on line numbers alone — a SHA permalink never 404s but shows a snapshot; a symbol name lets the reader re-find code that has moved since.

## Building the permalink

- Base URL: `git remote get-url origin`, normalised (`git@github.com:org/repo.git` → `https://github.com/org/repo`).
- Pin: `git rev-parse HEAD` — never a branch name; branch links rot as the branch moves.
- Shapes: GitHub `<base>/blob/<sha>/<path>#L10-L20` (directories use `/tree/`), GitLab `<base>/-/blob/<sha>/<path>#L10-20`, Bitbucket `<base>/src/<sha>/<path>#lines-10:20`.

## Rules

- **Repo anchor**: every ticket carries at least one canonical repo URL. A ticket in Jira full of bare paths doesn't say which repo they're in.
- **Hard gate — no local-only load-bearing content.** If acting on the ticket depends on something only the author can see, the ticket isn't done:
  - Uncommitted design doc → commit it and permalink, or upload (Confluence/Drive) and link.
  - Local logs / terminal output → paste the relevant lines into the ticket; link the log-platform query as the source.
  - A decision made in conversation → state the decision in the ticket. "As discussed" is a broken reference.
- Auth-gated SaaS links (Figma, Confluence) are fine as supplements, but anything acceptance depends on gets summarised inline — the assignee may not have access.
- Relative links between breakdown files (`./01-slug.md`) are allowed pre-publish only; the publisher rewrites them to tracker URLs. Everything else is absolute from the start.
