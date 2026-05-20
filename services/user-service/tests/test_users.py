import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_users.db"

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


def test_create_user():
    response = client.post("/v1/users/", json={
        "username": "saad",
        "email": "saad@example.com",
        "gdpr_consent": True
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "saad"
    assert data["gdpr_consent"] is True
    assert "id" in data


def test_list_users_empty():
    response = client.get("/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_get_user_by_id():
    create_resp = client.post("/v1/users/", json={
        "username": "alice",
        "email": "alice@example.com"
    })
    user_id = create_resp.json()["id"]
    response = client.get(f"/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_get_user_not_found():
    response = client.get("/v1/users/nonexistent-id")
    assert response.status_code == 404


def test_update_user():
    create_resp = client.post("/v1/users/", json={
        "username": "bob",
        "email": "bob@example.com"
    })
    user_id = create_resp.json()["id"]
    response = client.patch(f"/v1/users/{user_id}", json={"bio": "I love games"})
    assert response.status_code == 200
    assert response.json()["bio"] == "I love games"


def test_delete_user():
    create_resp = client.post("/v1/users/", json={
        "username": "charlie",
        "email": "charlie@example.com"
    })
    user_id = create_resp.json()["id"]
    response = client.delete(f"/v1/users/{user_id}")
    assert response.status_code == 204
    assert client.get(f"/v1/users/{user_id}").status_code == 404


def test_duplicate_username():
    client.post("/v1/users/", json={"username": "dave", "email": "dave@example.com"})
    response = client.post("/v1/users/", json={"username": "dave", "email": "dave2@example.com"})
    assert response.status_code == 409
