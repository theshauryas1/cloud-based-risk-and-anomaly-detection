"""
tests/conftest.py
──────────────────
Shared pytest fixtures.
Uses an in-memory SQLite DB to avoid touching the real DB during tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.db.session import get_db
from app.main import app

# ── In-memory SQLite for tests ────────────────────────────────
TEST_DATABASE_URL = "sqlite://"   # pure in-memory; destroyed after process

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """TestClient with in-memory DB wired in."""
    with TestClient(app) as c:
        yield c
