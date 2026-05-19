import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_games.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_game():
    response = client.post("/v1/games/", json={
        "title": "Elden Ring",
        "genre": "RPG",
        "platform": "PC",
        "cover_url": "https://example.com/elden.jpg"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Elden Ring"
    assert data["genre"] == "RPG"
    assert "id" in data


def test_list_games_empty():
    response = client.get("/v1/games/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_get_game_by_id():
    create_resp = client.post("/v1/games/", json={
        "title": "Hollow Knight",
        "genre": "Metroidvania",
        "platform": "PC"
    })
    game_id = create_resp.json()["id"]
    response = client.get(f"/v1/games/{game_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Hollow Knight"


def test_get_game_not_found():
    response = client.get("/v1/games/nonexistent-id")
    assert response.status_code == 404


def test_search_games():
    client.post("/v1/games/", json={"title": "Dark Souls", "genre": "RPG", "platform": "PC"})
    client.post("/v1/games/", json={"title": "Dark Souls II", "genre": "RPG", "platform": "PC"})
    client.post("/v1/games/", json={"title": "Celeste", "genre": "Platformer", "platform": "PC"})

    response = client.get("/v1/games/search?q=dark")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all("Dark" in g["title"] for g in data["items"])
