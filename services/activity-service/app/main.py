# activity-service — Module 3: Synchronous Communication

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app import repository, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="activity-service")


# ---------------------------------------------------------------------------
# Implemented functions
# ---------------------------------------------------------------------------

async def validate_user(user_id: str) -> None:
    """
    Verify that the user exists in user-service before logging an activity.
    This call is CRITICAL — the request must not proceed if validation fails.
    """
    url = f"{settings.user_service_url}/v1/users/{user_id}"

    for attempt in range(2):  # try once, retry once on network error
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)

            if response.status_code == 200:
                return  # user exists, proceed

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")

            # any other non-2xx
            raise HTTPException(status_code=503, detail="user-service unavailable")

        except httpx.RequestError:
            if attempt == 1:
                # second attempt also failed
                raise HTTPException(status_code=503, detail="user-service unavailable")
            # first attempt failed — retry


async def fetch_game(game_id: str) -> dict | None:
    """
    Fetch game data from game-service to enrich the activity response.
    This call is OPTIONAL — returns None on any failure, never raises.
    """
    url = f"{settings.game_service_url}/v1/games/{game_id}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except httpx.RequestError:
        return None


# ---------------------------------------------------------------------------
# Endpoints — pre-written, they call the two functions above
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "activity-service"}


@app.post("/v1/activities", response_model=schemas.ActivityOut, status_code=201)
async def create_activity(data: schemas.ActivityCreate, db: Session = Depends(get_db)):
    await validate_user(data.user_id)
    activity = repository.create_activity(db, data)
    game_data = await fetch_game(activity.game_id)
    return {
        "id": activity.id,
        "user_id": activity.user_id,
        "action": activity.action,
        "duration_minutes": activity.duration_minutes,
        "created_at": activity.created_at,
        "game": game_data,
    }


@app.get("/v1/activities", response_model=schemas.ActivityList)
async def list_activities(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    activities, total = repository.list_activities(db, limit=limit, offset=offset)
    items = []
    for a in activities:
        game_data = await fetch_game(a.game_id)
        items.append({
            "id": a.id,
            "user_id": a.user_id,
            "action": a.action,
            "duration_minutes": a.duration_minutes,
            "created_at": a.created_at,
            "game": game_data,
        })
    return schemas.ActivityList(items=items, total=total, limit=limit, offset=offset)


@app.get("/v1/activities/user/{user_id}", response_model=schemas.ActivityList)
async def list_user_activities(
    user_id: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)
):
    activities, total = repository.list_user_activities(db, user_id, limit=limit, offset=offset)
    items = []
    for a in activities:
        game_data = await fetch_game(a.game_id)
        items.append({
            "id": a.id,
            "user_id": a.user_id,
            "action": a.action,
            "duration_minutes": a.duration_minutes,
            "created_at": a.created_at,
            "game": game_data,
        })
    return schemas.ActivityList(items=items, total=total, limit=limit, offset=offset)