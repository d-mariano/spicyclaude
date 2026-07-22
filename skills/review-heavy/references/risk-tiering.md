# Risk Tiering

Scale review depth to the change's risk. The orchestrator computes a tier from the diff **before**
fanning out, then runs only the reviewer set that tier calls for. This keeps small changes fast and
gives risky changes full coverage. Thresholds below are sensible defaults — tune per repo.

## Signals (read from the diff + PR)

- **Size** — lines changed and files touched.
- **Sensitive paths** — auth / authz / session, crypto, payments / billing, DB migrations or
  schema, infra / CI / deploy / IaC, and public API surface (exported/published interfaces).
- **Dependency changes** — any manifest or lockfile touched (`package.json`, lockfiles,
  `requirements.txt`, `go.mod`, …) or a new third-party import.
- **Tests** — a behavioral change that touches no test file (raises the tier — see bumps below).

## Tiers

| Tier       | When                                                                                              | Reviewer set                                                                                             | Verification | Posting            |
| :--------- | :------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------- | :----------- | :----------------- |
| **Low**    | Small (≈ ≤ 30 lines / ≤ 3 files), no sensitive path, no dep change.                                | Delegate to `/code-review-light` — its single consolidated pass includes security. No fan-out.           | Skip         | — (see bumps)      |
| **Medium** | The default — anything not clearly Low or High.                                                    | Tier-1: `mental-alignment`, `security`, `code-quality`, `documentation`.                                 | Run          | Optional (`--post`)|
| **High**   | Large diff, **or** touches any sensitive path, **or** changes dependencies, **or** changes public API. | Tier-1 **+ all** Tier-2: `tests`, `performance`, `deps`, `observability`, `simplification`.              | Run          | Recommended        |

**Tier bumps** (apply after the table):

- A behavioral change with **no test file touched** raises the tier one level (Low → Medium,
  Medium → High).
- **`--post`** raises Low to Medium — posting always goes through the full pipeline and its
  [verification pass](verification.md), never through the light path.

## Output

State the computed tier and the chosen reviewer set at the top of the run, e.g.
`Risk tier: High (touches src/auth/, package.json changed) → 9 reviewers`.
