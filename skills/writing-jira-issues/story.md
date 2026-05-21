# Story

User-facing features and behaviour changes.

## Definitions
- **Acceptance Criteria**: observable behaviour from the user's perspective. Testable from the outside. Cover happy path AND at least one unhappy path (empty, error, edge state).
- **Out of Scope**: explicit list of what is NOT being built. Include whenever there is plausible scope-creep ambiguity. Link follow-up tickets by ID where they exist.

## Steps
- Use the Story template below
- Title format: `[Area] Plain-English description of what the ticket does`. Bracketed prefix is the functional area (Cart, Auth, Reporting, etc.); the rest reads scannably without opening the ticket
- The user benefit in the Summary must be concrete — not "to do my job better" or "to improve UX". If you cannot articulate a concrete benefit, push back before creating
- If there are gaps (missing why, vague ACs, no user perspective, unclear scope), push back with clarifying questions before creating
- Surface obvious edge cases as questions — do not invent answers. Examples worth asking about:
  - What happens in the empty state?
  - What happens on error or permission denied?
  - What happens to existing data when this changes (out of stock, price change, deletion, etc.)?
  - Is there a limit (max items, max length, rate limit)?
- ACs describe observable behaviour, not implementation. "User sees X" not "endpoint returns Y"
- State the persona once above the ACs; do not repeat "As a <user>" on every line

## Refinement Check
Before creating, verify:
- [ ] Title follows `[Area] description` form
- [ ] Summary states what AND why in one or two sentences
- [ ] User benefit is concrete (not "to do my job better" or "to improve UX")
- [ ] ACs are written from the user's perspective and observable from the outside
- [ ] At least one AC covers an unhappy path (empty, error, edge)
- [ ] Out of Scope present when scope is ambiguous; omitted only when scope is genuinely tight
- [ ] Engineering Notes link to designs, APIs, or existing patterns (not bare file paths)
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
- Existing pattern: [permalink to canonical example](https://github.com/org/repo/blob/<sha>/path)
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
