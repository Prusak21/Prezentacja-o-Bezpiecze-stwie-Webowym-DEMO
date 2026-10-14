import os

# Ustawiamy środowisko PRZED importem aplikacji (testy nie używają prawdziwego .env).
os.environ["JWT_SECRET"] = "test-secret-only-for-pytest-0123456789abcdef"
os.environ["CORS_ORIGINS"] = "https://localhost:5173"
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def login(client, email: str) -> dict:
    client.post("/auth/register", json={"email": email, "password": "pass12345"})
    r = client.post("/auth/login", data={"username": email, "password": "pass12345"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def alice(client):
    return login(client, "alice@example.com")


@pytest.fixture
def bob(client):
    return login(client, "bob@example.com")
