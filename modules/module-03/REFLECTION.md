# Module 3 — Reflection

**Team name**: solo
**Branch**: `module-03/solo`
**Submitted**: before Module 4 lesson

---

## 1. The "why"

Without the gateway, a frontend app would need to hardcode the port and address of every service — port 8001 for users, 8002 for games, 8003 for activities. If any service moves to a different machine or port, every client that talked to it directly breaks and needs to be updated. With the gateway as the single entry point, the client only ever knows one address: port 8000. The routing is the gateway's problem, not the client's. Services can be moved, renamed, or replaced without the client noticing.

---

## 2. Your choice

The user validation call retries and blocks because the data integrity of the activity depends on it. If we save an activity for a user that doesn't exist, the database contains an orphaned record that can never be resolved — there's no user to attach it to. Skipping or softening this check would silently corrupt the data.

The game fetch is different because the activity itself is still valid without it. The game data is enrichment — it makes the response richer, but the core fact being recorded is that a user performed an action. If game-service is down, we lose some detail in the response but we don't lose the activity. Blocking the whole request over optional data would make activity logging fragile for no benefit.

---

## 3. The tradeoff

Every synchronous hop adds its latency to the total. If user-service takes 200ms and game-service takes 300ms, the client waits at least 500ms before getting a response — and that's on a good day. If one service in the chain is slow or timing out, the entire request hangs until the timeout fires. Worse, if user-service goes down entirely, activity creation stops working even though the activity-service itself is healthy. The chain makes the system only as available as its weakest link.

---

*Keep this file. You will refer back to it during the oral presentation.*