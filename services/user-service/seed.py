"""
Seed script for user-service.
Idempotent — safe to run multiple times.
Usage: python seed.py (from inside services/user-service)
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal, engine
from app.models import User
from app.database import Base
import uuid
from datetime import datetime, timezone

Base.metadata.create_all(bind=engine)

SEED_USERS = [
    {
        "id": "aaaaaaaa-0000-0000-0000-000000000001",
        "username": "nova",
        "email": "nova@example.com",
        "bio": "FPS and RPG lover",
        "avatar_url": None,
        "gdpr_consent": True,
    },
    {
        "id": "aaaaaaaa-0000-0000-0000-000000000002",
        "username": "pixel",
        "email": "pixel@example.com",
        "bio": "Indie game enthusiast",
        "avatar_url": None,
        "gdpr_consent": True,
    },
    {
        "id": "aaaaaaaa-0000-0000-0000-000000000003",
        "username": "ghost",
        "email": "ghost@example.com",
        "bio": "Speedrunner",
        "avatar_url": None,
        "gdpr_consent": False,
    },
]


def seed():
    db = SessionLocal()
    try:
        inserted = 0
        for data in SEED_USERS:
            existing = db.query(User).filter(User.id == data["id"]).first()
            if existing:
                continue
            user = User(
                id=data["id"],
                username=data["username"],
                email=data["email"],
                bio=data["bio"],
                avatar_url=data["avatar_url"],
                gdpr_consent=data["gdpr_consent"],
                created_at=datetime.now(timezone.utc),
            )
            db.add(user)
            inserted += 1
        db.commit()
        print(f"Seeded {inserted} users (skipped {len(SEED_USERS) - inserted} existing).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
