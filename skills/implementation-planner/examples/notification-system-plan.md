# Implementation Plan: Event-Driven Notification System

**Design**: `docs/design/notification-system/design.md`
**Date**: 2025-02-06

## Overview

Building an event-driven notification system that decouples producers from delivery channels. 5 phases, 19 parent tasks, estimated 3-4 sessions with `/clear` between phases. Phase 1 (Walking Skeleton) proves the full async pipeline. Phases 2-4 add channels, preferences, and retry. Phase 5 hardens for production.

*Skills Required section omitted — this project does not use a skill system.*

<!-- This is an abbreviated example to calibrate depth and format. Your output should include ALL phases in full detail. Phase 1 is shown completely; later phases are abbreviated here but should NOT be abbreviated in your output. -->

---

## Phase 1: Walking Skeleton

> **Done when**: Event → email → DB record
> **Size**: M

### Dependencies
- PostgreSQL running locally or in Docker
- RabbitMQ running locally or in Docker
- SendGrid sandbox API key in environment

### Tasks

- [ ] **1.1 Database Schema & Migration**
  - **Files**: `src/store/migrations/001-create-notifications.sql`, `src/store/notification-repository.ts`
  - **Depends on**: None
  - **Verification**: Migration test
  - [ ] 1.1.1 Write migration `001-create-notifications.sql` with schema from design: `notifications` table (id, userId, eventType, channel, status, idempotencyKey, attempts, nextRetryAt, lastAttemptAt, externalId, createdAt)
  - [ ] 1.1.2 Run migration — verify table exists with correct columns and types
  - [ ] 1.1.3 Test rollback — verify clean DROP TABLE

- [ ] **1.2 Notification Repository**
  - **Files**: `src/store/notification-repository.ts`, `tests/unit/notification-repository.test.ts`
  - **Depends on**: 1.1
  - **Verification**: TDD
  - [ ] 1.2.1 RED: Write failing tests for repository CRUD
    - `test_creates_notification_with_all_fields` — insert returns notification with generated ID
    - `test_finds_notification_by_id` — retrieves what was inserted
    - `test_updates_notification_status` — status changes from "pending" to "sent"
    - `test_idempotency_key_prevents_duplicates` — inserting same key throws
  - [ ] 1.2.2 GREEN: Implement `NotificationRepository` with `create()`, `findById()`, `updateStatus()`
  - [ ] 1.2.3 REFACTOR: Skip — implementation is straightforward CRUD

- [ ] **1.3 Event Consumer**
  - **Files**: `src/events/event-consumer.ts`, `src/events/event-schemas.ts`, `tests/unit/event-consumer.test.ts`
  - **Depends on**: None
  - **Verification**: TDD
  - [ ] 1.3.1 RED: Write failing tests for event consumption
    - `test_consumes_order_confirmed_event` — handler called with parsed payload
    - `test_validates_event_schema` — malformed payload logs error and acks (no poison pill)
    - `test_rejects_unknown_event_type` — unknown events acked and logged
  - [ ] 1.3.2 GREEN: Implement `EventConsumer` class wrapping amqplib, `NotificationEvent` Zod schema
  - [ ] 1.3.3 REFACTOR: Skip — minimal at this stage

- [ ] **1.4 Template Engine**
  - **Files**: `src/templates/template-engine.ts`, `src/templates/template-registry.ts`, `src/templates/content/order-confirmed-email.hbs`, `tests/unit/template-engine.test.ts`
  - **Depends on**: None
  - **Verification**: TDD
  - [ ] 1.4.1 RED: Write failing tests for rendering
    - `test_renders_email_template_with_context` — produces HTML with interpolated order data
    - `test_returns_subject_and_body` — `RenderedContent` has subject, bodyHtml, bodyText
    - `test_throws_on_unknown_template` — missing templateId throws descriptive error
  - [ ] 1.4.2 GREEN: Implement `TemplateEngine` with Handlebars, `TemplateRegistry` loading `.hbs` files from disk
  - [ ] 1.4.3 REFACTOR: Extract template loading into `TemplateRegistry.loadAll()` if constructor is doing too much

- [ ] **1.5 Email Channel**
  - **Files**: `src/delivery/channels/channel.ts`, `src/delivery/channels/email-channel.ts`, `tests/unit/email-channel.test.ts`
  - **Depends on**: None
  - **Verification**: TDD
  - [ ] 1.5.1 RED: Write failing tests for email delivery
    - `test_sends_email_via_sendgrid` — calls SendGrid API with correct payload, returns `delivered` with externalId
    - `test_returns_failed_on_sendgrid_error` — 500 response returns `{ status: "failed", retryable: true }`
    - `test_returns_rate_limited_on_429` — 429 response returns `{ status: "rate_limited", retryAfterMs }`
  - [ ] 1.5.2 GREEN: Define `DeliveryChannel` interface in `channel.ts`, implement `EmailChannel`
  - [ ] 1.5.3 REFACTOR: Skip — thin adapter over SendGrid SDK

- [ ] **1.6 Notification Router**
  - **Files**: `src/router/notification-router.ts`, `src/router/routing-rules.ts`, `tests/unit/notification-router.test.ts`
  - **Depends on**: 1.2, 1.4, 1.5
  - **Verification**: TDD
  - [ ] 1.6.1 RED: Write failing tests for routing
    - `test_routes_order_confirmed_to_email` — event type maps to email channel via routing rules
    - `test_checks_idempotency_before_routing` — duplicate idempotencyKey skips processing
    - `test_renders_template_and_delivers` — full flow: resolve rule → render → deliver → persist
  - [ ] 1.6.2 GREEN: Implement `NotificationRouter.handle(event)` orchestrating repo, templates, delivery
  - [ ] 1.6.3 REFACTOR: Extract routing rule resolution if `handle()` exceeds 30 lines

- [ ] **1.7 Walking Skeleton Integration**
  - **Files**: `src/index.ts`, `src/config.ts`, `tests/integration/walking-skeleton.test.ts`
  - **Depends on**: 1.3, 1.6
  - **Verification**: Integration test
  - [ ] 1.7.1 Wire `EventConsumer` → `NotificationRouter` in `src/index.ts`
  - [ ] 1.7.2 Create `src/config.ts` with typed env var loading (RABBITMQ_URL, DATABASE_URL, SENDGRID_API_KEY)
  - [ ] 1.7.3 Write integration test: publish `OrderConfirmed` event → assert notification in DB with status "sent" → assert SendGrid sandbox received the call
  - [ ] 1.7.4 Verify: `npm test` all green, `npm run lint` clean

**Phase 1 checkpoint** ✅
- Safe to `/clear` — all progress tracked in this file
- Proven: full async pipeline from domain event to delivered email to DB record
- Deployable: yes, handles `OrderConfirmed` → email (single event type, single channel)

---

## Phase 2: Push & In-App Channels

> **Done when**: Each channel passes integration test
> **Size**: S

*(Abbreviated in this example — your output should have full task detail for every phase.)*

### Tasks

- [ ] **2.1 Push Channel (FCM)** — TDD, follows pattern of 1.5
- [ ] **2.2 In-App Channel** — TDD, follows pattern of 1.5
- [ ] **2.3 Register New Channels** — Integration test, wires 2.1 + 2.2 into DI and routing rules

---

## Phase 3: User Preferences

> **Done when**: Push-only user gets push, not email
> **Size**: S

*(Abbreviated.)*

- [ ] **3.1 User Preference Resolver** — TDD
- [ ] **3.2 Integrate Preferences into Router** — TDD
  - ⚠️ **Shared code**: Modifying `NotificationRouter.handle()` which is the core orchestration path

---

## Phase 4: Retry & Dead Letter

> **Done when**: Failed → 3 retries → dead-lettered
> **Size**: M

*(Abbreviated.)*

- [ ] **4.1 Retry Policy** — TDD, pure calculation
- [ ] **4.2 Retry Worker** — TDD
  - ⚠️ **Coupling**: Reads and writes notification records — must not conflict with the main delivery path
- [ ] **4.3 Wire Retry into Delivery Manager** — Integration test

---

## Phase 5: Observability & Hardening

> **Done when**: Dashboard shows rates/latency/failures
> **Size**: S

*(Abbreviated.)*

- [ ] **5.1 Health Endpoint** — Smoke test
- [ ] **5.2 Structured Logging** — Manual verification
  - ⚠️ **Shared code**: Adding logging to all existing service files
- [ ] **5.3 Metrics** — Smoke test
- [ ] **5.4 Graceful Shutdown** — Manual verification

---

## Coverage Analysis

### Component Coverage

| Component (from design) | Task(s) | Status |
|------------------------|---------|--------|
| EventConsumer | 1.3 | ✅ Covered |
| NotificationRouter | 1.6, 3.2 | ✅ Covered |
| TemplateEngine | 1.4 | ✅ Covered |
| TemplateRegistry | 1.4 | ✅ Covered |
| EmailChannel | 1.5 | ✅ Covered |
| DeliveryManager | 4.3 | ✅ Covered |
| PushChannel | 2.1 | ✅ Covered |
| InAppChannel | 2.2 | ✅ Covered |
| RetryWorker | 4.2 | ✅ Covered |
| RetryPolicy | 4.1 | ✅ Covered |
| UserPreferenceResolver | 3.1 | ✅ Covered |
| NotificationRepository | 1.2 | ✅ Covered |

### Contract Coverage

| Contract | Tested In | Status |
|----------|-----------|--------|
| `NotificationRouter.handle(event)` | 1.6.1 RED | ✅ |
| `TemplateEngine.render(request)` | 1.4.1 RED | ✅ |
| `DeliveryChannel.send(request)` | 1.5.1, 2.1.1, 2.2.1 RED | ✅ |
| `RetryPolicy.nextRetryAt(attempts)` | 4.1.1 RED | ✅ |
| `UserPreferenceResolver.resolve()` | 3.1.1 RED | ✅ |
| `NotificationRepository` CRUD | 1.2.1 RED | ✅ |

### Gaps

| Item | Type | Notes |
|------|------|-------|
| None | — | Full coverage |

---

## Execution Notes

### How to Use This Plan

Execute phases in order. Within each phase, execute tasks in order.

```bash
# Start with Phase 1
# After each parent task: mark subtasks [x], then parent [x]
# At phase checkpoint: /clear and resume with this file

# Or with an iterate command:
/iterate docs/design/notification-system/plan.md
```

### Verification Commands

```bash
npm test                    # Full test suite
npm run lint                # ESLint
npx tsc --noEmit            # Type checking
```

All three must pass before marking any parent task complete.
