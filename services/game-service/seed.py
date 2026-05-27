"""
Seed script for game-service.
Idempotent — safe to run multiple times.
Usage: python seed.py (from inside services/game-service)
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal, engine
from app.models import Game
from app.database import Base
from datetime import datetime, timezone

Base.metadata.create_all(bind=engine)

SEED_GAMES = [
    {
        "id": "bbbbbbbb-0000-0000-0000-000000000001",
        "title": "Hollow Knight",
        "genre": "metroidvania",
        "platform": "PC",
        "cover_url": "https://example.com/hollow-knight.jpg",
    },
    {
        "id": "bbbbbbbb-0000-0000-0000-000000000002",
        "title": "Elden Ring",
        "genre": "RPG",
        "platform": "PC",
        "cover_url": "https://example.com/elden-ring.jpg",
    },
    {
        "id": "bbbbbbbb-0000-0000-0000-000000000003",
        "title": "Celeste",
        "genre": "platformer",
        "platform": "PC",
        "cover_url": "https://example.com/celeste.jpg",
    },
]


def seed():
    db = SessionLocal()
    try:
        inserted = 0
        for data in SEED_GAMES:
            existing = db.query(Game).filter(Game.id == data["id"]).first()
            if existing:
                continue
            game = Game(
                id=data["id"],
                title=data["title"],
                genre=data["genre"],
                platform=data["platform"],
                cover_url=data["cover_url"],
                created_at=datetime.now(timezone.utc),
            )
            db.add(game)
            inserted += 1
        db.commit()
        print(f"Seeded {inserted} games (skipped {len(SEED_GAMES) - inserted} existing).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
