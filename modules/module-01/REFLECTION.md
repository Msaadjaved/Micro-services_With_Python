## YOU NEED TO COMMIT THIS FILE BEFORE MOVING ON TO THE NEXT MODULE ! 🚨

**feel free to delete this comment**

# Module 1 — Reflection

**Team name**: **\*\***\_\_\_**\*\***
**Branch**: `module-01/<team-name>`
**Submitted**: before Module 2 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

You started from a painful monolith. Now you're splitting it into separate services.

**What concrete problem does that split solve: and for whom?**

Think about it from three angles: the developer who has to change code, the team that has to deploy it, and the user who has to live with its failures. You don't need to cover all three, pick the one that felt most real to you today.

> _The split solves a deployment problem. In a monolith, fixing a bug in the notification logic means redeploying the entire application — including auth, game library, and user profiles. Every deploy is a risk to everything. With separate services, you can push a change to notification-service without touching auth-service at all. The blast radius of a bad deploy shrinks to one service. That independence is the real win._

---

## 2. Your choice

Look at your service map. Every arrow between two services is a decision someone made.

**Pick one boundary, one place where you decided service A should not be part of service B. Explain why that line exists.**

What would break, slow down, or become harder to manage if you merged those two services back together?

> _I kept activity-service and logging-service separate rather than having activity-service log directly to its own database. The line exists because they have different reasons to change — activity-service is a domain service that records what users do, logging-service is a compliance service that decides whether recording is allowed based on GDPR consent. If you merged them, a logging failure would block the activity feed entirely. Keeping them connected only by a RabbitMQ event means a logging failure is invisible to the user._

---

## 3. The tradeoff

Microservices solve the monolith's problems. But they create new ones.

**Name one thing that was simpler in the monolith and is now harder in your distributed design.**

No need to solve it: just name it honestly. This is exactly the tension the rest of the course is about.

> _In a monolith, checking whether a user has given GDPR consent is a single function call — one line, same process, same database transaction. In the distributed design, logging-service has to make a network call to user-service to check consent before every log write. That call can fail, time out, or add latency. You now have to think about what to do when the consent check is unavailable: fail open (log anyway, risk a GDPR violation) or fail closed (drop the log, risk losing data). Neither is free. A simple conditional became a distributed decision with failure modes._

---

_Keep this file. You will refer back to it during the oral presentation._
