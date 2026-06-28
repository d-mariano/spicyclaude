# Design: Real-time notifications for workspace events

**Author:** A. Patel
**Status:** Draft (v0.3)
**Date:** 2026-04-09

## Background

Users want to know when things happen in their workspace — new comments, task assignments, mentions, status changes. Today, they have to refresh. We need real-time push.

## Proposed solution

We'll build a notification pipeline that pushes events to connected clients within seconds.

### Architecture

Events are emitted by the existing `EventBus` service. The new `NotificationService` subscribes to relevant topics, fans events out to per-user queues, and pushes to connected clients via WebSocket.

The system should be performant and scale well. We expect to handle a high volume of events.

### Delivery guarantees

Notifications are delivered in real-time over WebSockets.

Notifications are also persisted to the database so users can see what they missed when they reconnect. We use the `notification_log` table.

For mobile clients, we'll deliver via the existing push-notification gateway. This should be straightforward since it's already in production.

### Client experience

A small bell icon in the top nav shows unread count. Clicking it opens a panel listing recent notifications. The panel should feel snappy and modern.

Users can mark notifications as read, dismiss them, or click through to the source object.

### Asynchrony

The WebSocket connection is fire-and-forget. The server pushes, the client receives. We don't need acknowledgements.

Later in the design: we'll need delivery confirmation so we know when to stop showing the notification as undelivered. Clients send an `ack` message after rendering.

## Out of scope

- Notification preferences (which event types a user wants). Future work.
- Email digests. Future work.

## Open questions

- Should we use Redis pub/sub or Kafka for the per-user fan-out?
- What's the retention policy for the notification log?
