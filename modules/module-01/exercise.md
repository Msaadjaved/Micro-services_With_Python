# Module 1 — Service Decomposition

**Duration**: 2h in class
**Branch to submit**: `module-01/solo`

---

## Objective

Before writing a single line of code, you need to design the system on paper. Every decision you make here: where to draw service boundaries, who owns what data, how services talk to each other, is hard to reverse once you start coding.

This module is about slowing down and thinking like an architect, not a developer.

Read these two documents before doing anything else:

- `docs/domain.md` — what GameHub is and who uses it
- `docs/specs.md` — the tech stack and key architectural decisions

> The CTO has already laid out the `services/` folder structure. Use it as a starting point, but your job is to **justify** why each folder deserves to be its own service — not just accept it.

---

## Task 1 — Identify bounded contexts _(~40 min)_

A bounded context is a part of the system that has a clear responsibility and owns its data exclusively. No other service should reach into its database.

| Bounded Context | Responsibilities | Owned Entities | Team |
| --- | --- | --- | --- |
| Identity | Manages who users are, handles registration and profiles | User, Profile | Platform |
| Authentication | Issues and validates JWT tokens, manages the shared secret | Token, Session | Platform |
| Game Library | Tracks games a user owns or plays, stores game metadata, powers recommendations based on play history | Game, UserGame, Genre, Recommendation | Discovery |
| Activity | Records player actions (started a game, added a friend), emits events to RabbitMQ for downstream consumers | ActivityEvent | Engagement |
| Notification | Consumes RabbitMQ events, decides how and when to alert users, stores notification preferences | Notification, NotificationPreference | Engagement |
| Logging | GDPR-compliant audit log — stores user consent state, records activity only if opted in | ConsentRecord, ActivityLog | Compliance |

**Justifications:**

- **Identity vs Authentication** — who you *are* and proving who you are change independently. Profile updates have nothing to do with token expiry or secret rotation. Merging them means touching auth code every time a product manager wants a new profile field.
- **Activity vs Logging** — activity-service *produces* facts about what happened; logging-service *decides whether it is allowed to store them* under GDPR. One is business logic, the other is compliance policy.
- **Activity vs Notification** — both react to the same RabbitMQ events but for different reasons. They can evolve, scale, and fail independently.
- **Game Library** — owns all game data and recommendations. No other service queries the games table directly.

---

## Task 2 — Define service contracts _(~30 min)_

**1. gateway → auth-service**
Direction: gateway → auth-service
Trigger: every incoming client request that carries a JWT token
Protocol: REST (synchronous) — the gateway must block until the token is validated
Payload: `{ token }` → Response: `{ valid, user_id, roles }`
Why sync: the gateway cannot route the request forward until it knows who is asking.

**2. gateway → user-service / game-service / activity-service**
Direction: gateway → downstream service
Trigger: authenticated client request for a resource
Protocol: REST (synchronous), path-based routing
Payload: original request body + injected `X-User-Id` header set by the gateway after token validation. Downstream services trust the gateway, not the client.

**3. activity-service → logging-service**
Direction: activity-service → logging-service
Trigger: a user action is recorded (started a game, added a friend)
Protocol: RabbitMQ message (async)
Payload: `{ activity_id, user_id, action, game_id, timestamp }`
Why async: if logging-service is down or slow, it must not block or slow down the activity feed. A REST call here would create a hard dependency — one failure cascades to the other.

**4. activity-service → notification-service**
Direction: activity-service → notification-service
Trigger: an activity event that should alert another user
Protocol: RabbitMQ message (async)
Payload: `{ event_type, source_user_id, target_user_id, game_id, timestamp }`
Why async: notifications are best-effort. A user should not wait for their friend to be notified before their own action is confirmed.

**5. logging-service → user-service (consent check)**
Direction: logging-service → user-service
Trigger: before recording any activity log entry
Protocol: REST (synchronous)
Payload: `{ user_id }` → Response: `{ gdpr_consent: bool }`
Why this boundary: consent is owned by the Identity context. If consent is false, the log entry is dropped silently.

---

## Task 3 — Draw the service map _(~20 min)_

Legend: `──►` synchronous REST · `--►` async RabbitMQ event

```
                        ┌─────────────────────────┐
         HTTP ─────────►│         gateway          │  port 8000
                        │  JWT validation          │  single entry point
                        │  path-based routing      │
                        │  circuit breaking        │
                        └────────────┬─────────────┘
                                     │
              ┌──────────────────────┼───────────────────────┐
              │ REST                 │ REST                   │ REST
              ▼                     ▼                         ▼
    ┌──────────────────┐  ┌──────────────────┐   ┌──────────────────────┐
    │  auth-service    │  │  user-service    │   │   game-service       │
    │  port 8005       │  │  port 8001       │   │   port 8002          │
    │  JWT issue +     │  │  User, Profile   │   │   Game, UserGame     │
    │  validation      │  │                 ◄│   │   + Redis cache      │
    └──────────────────┘  └────────┬─────────┘   └──────────────────────┘
                                   ▲ REST (consent check)
                                   │
                        ┌──────────┴─────────────┐
         REST ─────────►│   activity-service     │  port 8003
                        │   ActivityEvent        │
                        └──────────┬─────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                  async                          async
                 (RabbitMQ)                   (RabbitMQ)
                    ▼                              ▼
    ┌───────────────────────┐      ┌───────────────────────────┐
    │  notification-service │      │     logging-service       │
    │  port 8004            │      │     port 8006             │
    │  Node.js, SQLite      │      │     Flask (not FastAPI)   │
    │  always local         │      │     GDPR consent check    │
    └───────────────────────┘      └───────────────────────────┘
```

---

## Discussion _(~15 min)_

1. Why does `notification-service` use Node.js instead of Python like the rest? What does that tell you about microservices and technology choices?
2. What is the risk of `activity-service` calling `logging-service` synchronously — why might you prefer an async event instead?
3. Why does `logging-service` need a GDPR consent check before recording any activity?

You do not need to write these answers down — they are warm-up for your REFLECTION.md.

---

## Minimum to submit this branch

- [x] Bounded context table filled in (at least 4 services justified)
- [x] At least 3 service contracts defined
- [x] Service map committed (sketch, photo, or ASCII)
- [x] `REFLECTION.md` completed and committed

The map does not need to be perfect. It needs to be yours.