# Module 2 — Reflection

**Team name**: solo
**Branch**: `module-02/solo`
**Submitted**: before Module 3 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

You built a service with distinct layers: models, schemas, repository, service, and routes — each with a single responsibility.

**Why not just put everything in one file and call it done?**

Think about what happens six months later when someone new joins the team, or when you need to swap SQLite for PostgreSQL. What does the layered structure protect you from?

> Putting everything in one file works until you need to change something. Six months later, when someone needs to swap SQLite for PostgreSQL, the layered structure means they only touch `database.py` — not the business logic, not the HTTP layer, not the schemas. If everything were in one file, a database change would require reading hundreds of lines just to find the three that matter. The layers are documentation: when you open `repository.py` you know exactly what kind of code belongs there, and what does not.

---

## 2. Your choice

Each service owns its data exclusively — no other service is allowed to touch its database directly.

**Pick one entity your service owns (e.g. `User`, `Game`). What would go wrong if another service could write to that table directly?**

Give a concrete scenario, not a general principle.

> The `Game` table is owned exclusively by `game-service`. If `user-service` could write to it directly — say, to record which games a user has played — you would end up with two services that silently disagree on what a valid game record looks like. `user-service` might insert a row without a `platform`, which `game-service`'s validation would have rejected. Now the data is inconsistent and neither service knows it. The boundary forces all writes through `game-service`'s own validation, so the data stays clean regardless of who is asking.

---

## 3. The tradeoff

You now have models, schemas, a repository, a service, and routes — five layers for what is essentially a CRUD service.

**For a system this small, what is the cost of all this structure?**

And at what point does the complexity start to pay off? Where is the tipping point?

> For a four-endpoint CRUD service, five layers is real overhead. Adding a new field means touching `models.py`, `schemas.py`, `repository.py`, `service.py`, and sometimes `routes.py` — five files for what would be one line in a monolith. The structure starts paying off when the service grows: when the repository needs pagination logic, when the service needs to enforce business rules before writing, or when a second developer joins and needs to find things fast. For a service this small and stable, the cost is friction with no immediate return.

---

*Keep this file. You will refer back to it during the oral presentation.*