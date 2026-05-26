# Design: Idempotency keys for the Payments API

**Author:** R. Chen
**Status:** Approved
**Date:** 2026-02-14

## Background

Our public `POST /v1/payments` endpoint is not idempotent. Clients retrying after a network blip can charge a customer twice. Support has logged 47 such incidents in Q4. We need to add idempotency-key support to prevent this.

## Goal

Allow clients to safely retry `POST /v1/payments` by supplying an `Idempotency-Key` header. Identical requests with the same key within 24 hours return the original response instead of creating a new charge.

## Proposed approach

### API surface

- Accept an optional `Idempotency-Key: <string>` header on `POST /v1/payments`.
- Keys are arbitrary client-chosen strings, max 64 chars.
- If the header is missing, behave as today (no idempotency guarantee).

### Storage

Add a new table `payment_idempotency_keys`:

| column | type | notes |
|---|---|---|
| key_hash | varchar(64) | SHA-256 of (client_id, idempotency_key) |
| request_fingerprint | varchar(64) | SHA-256 of the request body |
| response_body | jsonb | the original 2xx response |
| response_status | int | the original status code |
| created_at | timestamptz | for 24h expiry |

Index on `key_hash`. TTL via a daily cleanup job.

### Request handling

On `POST /v1/payments` with an `Idempotency-Key`:

1. Compute `key_hash` and `request_fingerprint`.
2. Look up the key in `payment_idempotency_keys`.
3. If found and `request_fingerprint` matches → return stored response.
4. If found and `request_fingerprint` differs → return `409 Conflict`.
5. If not found → process the payment, then store the response keyed on `key_hash` before returning.

### Concurrency

If two requests with the same key arrive simultaneously, the second should wait for the first. Use a row-level lock on `payment_idempotency_keys` keyed on `key_hash`.

## Out of scope

- Idempotency for other endpoints (refunds, subscriptions) — separate work.
- Cross-region key replication. Single-region only for v1.

## Open questions

- Should the 24h TTL be configurable per client, or fixed?
- Do we need a metric for idempotency-key hit rate from day one, or can it wait?

## Rollout

Feature flag `payments_idempotency_keys` controls whether the header is honoured. Default off in prod for one week, then on.
