# Story

Features and behaviour changes that have an **identifiable consumer**.

"Consumer" is intentionally broad — it covers any party that observes the change from outside the implementation:

- **End users** (humans interacting with a UI) — the canonical case.
- **API callers** (any service that hits a REST/gRPC endpoint, posts to a webhook, subscribes to a topic, reads a Firestore collection, or imports a generated stub).
- **Downstream services** (a sibling deployment that consumes this change's output — e.g. a Pub/Sub subscriber, a webhook receiver, a contract-using gRPC client).
- **Future engineers writing against the surface** (when this story introduces or changes a contract that other code will be written against — e.g. a per-tool extension point, a new SDK helper signature).

If you can write an AC in the form "**When `<consumer>` does `<X>`, they observe `<Y>`**", it's a Story. The persona block at the top of the AC list names the consumer explicitly — `**As an API caller of /webhook/metronome:**`, `**As bblocks-ui:**`, `**As a future tool author:**` — not just `**As a user:**`.

If the work has no externally observable consumer surface (a Terraform resource that creates a Pub/Sub topic, a worker-class flip with identical request/response shape, a logging-only change), it's a **Task**, not a Story. See [task.md](task.md).

## Definitions
- **Acceptance Criteria**: observable behaviour from the consumer's perspective. Testable from the outside. Cover happy path AND at least one unhappy path (empty, error, edge state).
- **Out of Scope**: explicit list of what is NOT being built. Include whenever there is plausible scope-creep ambiguity. Link follow-up tickets by ID where they exist.

## Steps
- Use the Story template below
- Title format: `[Area] Plain-English description of what the ticket does`. Bracketed prefix is the functional area (Cart, Auth, Reporting, etc.); the rest reads scannably without opening the ticket
- The **consumer benefit** in the Summary must be concrete — not "to do my job better" or "to improve UX". For API/service consumers the benefit is the new capability the contract unlocks ("downstream X can now Y without doing Z themselves"); for end users it's the outcome they get to experience. If you cannot articulate a concrete benefit, push back before creating
- If there are gaps (missing why, vague ACs, no consumer perspective, unclear scope), push back with clarifying questions before creating
- Surface obvious edge cases as questions — do not invent answers. Examples worth asking about:
  - What happens in the empty state?
  - What happens on error or permission denied?
  - What happens to existing data when this changes (out of stock, price change, deletion, etc.)?
  - Is there a limit (max items, max length, rate limit)?
- ACs describe observable behaviour, not implementation. "User sees X" not "endpoint returns Y" — and when the consumer IS another service, that becomes "when caller posts X, response carries Y" not "the handler calls FooService.bar()"
- State the persona once above the ACs; do not repeat the persona block on every line. For API-consumer stories the persona is the calling service or contract surface (`**As bblocks-ui calling the dashboards endpoint:**`, `**As Pub/Sub push-delivering to /pubsub/metronome-ingest:**`)

## Refinement Check
Before creating, verify:
- [ ] Title follows `[Area] description` form
- [ ] Summary states what AND why in one or two sentences
- [ ] Consumer is identified explicitly (end user, API caller, downstream service, future engineer) and the benefit to that consumer is concrete (not "to do my job better" or "to improve UX")
- [ ] ACs are written from the consumer's perspective and observable from outside the implementation
- [ ] At least one AC covers an unhappy path (empty, error, edge)
- [ ] Out of Scope present when scope is ambiguous; omitted only when scope is genuinely tight
- [ ] Engineering Notes pair every code/file reference with a SHA-pinned permalink per [references/code-references.md](references/code-references.md), and at least one canonical repo URL anchors the ticket
- [ ] No load-bearing content that exists only locally or in this conversation — commit + permalink, upload + link, or inline it
- [ ] No clarifying questions left unanswered

## Template
```markdown
# Summary
One or two sentences on what we are building and why it matters. Lead with the user outcome and a concrete user benefit; anchor the business why in a concrete signal (metric, support ticket volume, known pain point) where one exists.

# Acceptance Criteria
**As a** <persona>:
- [ ] When I <do this>, I <see / can do that>
- [ ] When <empty / error / edge state>, I see <observable behaviour>
- [ ] <Non-functional check where relevant: analytics event fires, telemetry captured, a11y, perf budget>

# Out of Scope
- <What we are explicitly not building this sprint>
- <Follow-up captured in TICKET-ID>

# Engineering Notes
- [Figma Design](https://link.to/design)
- [API Endpoint](https://link.to/api)
- Existing pattern: `path/in/repo.ts` ([permalink](https://github.com/org/repo/blob/<sha>/path/in/repo.ts))
- Docs: [link](https://link.to/docs)
```

## Template Notes
- **Title**: `[Area] description` form. Scannable in the backlog without opening the ticket
- **Summary**: combines what + why. Skip a separate Context section unless the why genuinely needs its own real estate
- **Acceptance Criteria**: persona stated once above; criteria in user-narrative form, not Gherkin. Outcome-focused. Let QA decide how to verify
- **Out of Scope**: omit the section entirely when there is nothing to call out — do not include the header with "N/A" underneath
- **Engineering Notes**: pointers, not prose. A dev should be able to start without asking what to read first

## Examples

**Good Title:**
> `[Cart] Move items to a Save-for-Later list`

**Bad Title** (no area, no scannable description):
> `Save for later`

**Good Summary** (concrete user benefit + concrete business signal):
> Move items from the active cart into a Save-for-Later list so shoppers can hold onto things they want later without abandoning checkout. Users currently use the active cart as a wishlist; checkout completion drops 15% above 5 cart items.

**Bad Summary** (no why):
> Add a Save for Later button to the cart.

**Bad Summary** (vague user benefit):
> Add a Save for Later button so users can do their shopping better.

**Good AC** (persona once, observable, covers unhappy path):
> **As a** logged-in shopper:
> - [ ] When I click "Save for Later" on a cart item, the item moves to a Saved-for-Later section and the cart subtotal updates
> - [ ] When I have zero saved items, I do not see the Saved-for-Later section at all
> - [ ] When a saved item goes out of stock, I see it marked unavailable with a "Notify me" option in place of "Move to Cart"

**Bad AC** (implementation, not behaviour):
> - [ ] POST /api/v2/user/saved-items returns 201
> - [ ] Redux store updates with new saved item

**Good AC for an API-consumer story** (persona is the calling service; ACs read as contract observations):
> **As bblocks-ui calling `GET /api/dashboards/embed`:**
> - [ ] When I pass `?type=usage` with a valid Firebase ID token, I receive `200` with `{ "url": "https://embeddable-dashboards.metronome.com/..." }`
> - [ ] When I pass an invalid `?type` value, I receive `400` with the documented error envelope and a clear `error.message`
> - [ ] When billing-service is unreachable, I receive `503` so I can render a retry CTA instead of a blank iframe

The shape "When the calling service does X, it observes Y" is what makes this a Story rather than a Task — even though no human ever sees the JSON response directly.
