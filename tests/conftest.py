"""Shared pytest fixtures for the Student Awards test-suite.

IMPORTANT: the environment is configured *before* any ``app`` module is
imported, because ``app.database`` builds its engine at import time.  Tests
therefore never touch the developer's real ``database.db``.

Run from the project root (templates are loaded from ``app/templates``):

    pytest tests/unit
    pytest tests/integration
"""
from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# --- 1. test environment (must precede every ``import app...``) -------------
_TMP_DIR = tempfile.mkdtemp(prefix="student_awards_tests_")
os.environ["DATABASE_URI"] = f"sqlite:///{Path(_TMP_DIR, 'test.db').as_posix()}"
os.environ["SECRET_KEY"] = "unit-test-secret-key-not-for-production-0123456789"
os.environ["ENV"] = "development"  # cookies: secure=False so http TestClient works
os.environ["CONFIG_PASSWORD"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

import app.models  # noqa: E402,F401  (register tables on SQLModel.metadata)
from app.models.hourlog import Activity, HourLog  # noqa: E402
from app.models.milestone import Milestone  # noqa: E402
from app.models.prize import Prize  # noqa: E402
from app.models.user import User  # noqa: E402
from app.utilities.security import encrypt_password  # noqa: E402

_HASH_CACHE: dict[str, str] = {}


def _hash(plain: str) -> str:
    """argon2 is deliberately slow; hash each distinct test password only once."""
    if plain not in _HASH_CACHE:
        _HASH_CACHE[plain] = encrypt_password(plain)
    return _HASH_CACHE[plain]


PASSWORDS = {"bob": "bobpass", "amy": "amypass", "cal": "calpass", "admin": "adminpass"}


# --- 2. helpers --------------------------------------------------------------
def make_user(
    db: Session,
    username: str,
    role: str = "regular_user",
    password: str | None = None,
    **extra,
) -> User:
    """Insert and return a user. Password defaults to ``<username>pass``."""
    user = User(
        username=username,
        email=f"{username}@example.com",
        password=_hash(password or PASSWORDS.get(username, f"{username}pass")),
        role=role,
        **extra,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_approved_hours(db: Session, user: User, activity: Activity, hours: float) -> HourLog:
    log = HourLog(
        user_id=user.id,
        activity_id=activity.id,
        hours=hours,
        proof_note="seeded",
        status="approved",
        reviewed_at=datetime.now(timezone.utc),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def seed_catalog(db: Session) -> dict:
    """Activities, milestones (10/25/50) and prizes mirroring ``manage.py init``."""
    activities = [
        Activity(title="Beach cleanup", category="Environment"),
        Activity(title="Food drive", category="Community"),
        Activity(title="Retired activity", category="Community", is_active=False),
    ]
    milestones = [
        Milestone(name="Bronze", hours_threshold=10.0, badge_label="Bronze 10h"),
        Milestone(name="Silver", hours_threshold=25.0, badge_label="Silver 25h"),
        Milestone(name="Gold", hours_threshold=50.0, badge_label="Gold 50h"),
    ]
    prizes = [
        Prize(name="Water bottle", hours_cost=10.0, stock=5),
        Prize(name="Mug", hours_cost=15.0, stock=5),
        Prize(name="T-shirt", hours_cost=25.0, stock=3),
        Prize(name="Tote bag", hours_cost=5.0, stock=0),  # out of stock
        Prize(name="Hidden prize", hours_cost=1.0, stock=9, is_active=False),
    ]
    db.add_all(activities + milestones + prizes)
    db.commit()
    for obj in activities + milestones + prizes:
        db.refresh(obj)
    return {
        "beach": activities[0],
        "food": activities[1],
        "retired": activities[2],
        "bronze": milestones[0],
        "silver": milestones[1],
        "gold": milestones[2],
        "bottle": prizes[0],
        "mug": prizes[1],
        "tshirt": prizes[2],
        "tote": prizes[3],
        "hidden": prizes[4],
    }


# --- 3. UNIT-TEST fixtures: private in-memory DB, no app engine, no HTTP ------
@pytest.fixture()
def db() -> Session:
    """A fresh, isolated in-memory SQLite database per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture()
def catalog(db):
    return seed_catalog(db)


@pytest.fixture()
def student(db) -> User:
    return make_user(db, "bob")


@pytest.fixture()
def admin(db) -> User:
    return make_user(db, "admin", role="admin")


# --- 4. INTEGRATION fixtures: real app, real routers, temp SQLite file --------
@pytest.fixture()
def app_db():
    """Reset the app's (temporary) database and yield a Session bound to it."""
    from app.database import engine

    engine.echo = False
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture()
def world(app_db):
    """Standard cast: admin, bob (0h), amy (40h), cal (25h) plus the catalog."""
    cat = seed_catalog(app_db)
    people = {
        "admin": make_user(app_db, "admin", role="admin"),
        "bob": make_user(app_db, "bob"),
        "amy": make_user(app_db, "amy"),
        "cal": make_user(app_db, "cal"),
    }
    make_approved_hours(app_db, people["amy"], cat["beach"], 40.0)
    make_approved_hours(app_db, people["cal"], cat["beach"], 25.0)
    app_db.commit()  # end any open read transaction before HTTP requests write
    return {"db": app_db, **cat, **people}


@pytest.fixture()
def anon():
    """Un-authenticated HTTP client."""
    from app.main import app

    with TestClient(app, follow_redirects=False, raise_server_exceptions=False) as c:
        yield c  # context manager => lifespan (table creation) runs


@pytest.fixture()
def login(world):
    """Factory: ``login('bob')`` -> a TestClient holding bob's auth cookie."""
    from app.main import app

    opened: list[TestClient] = []

    def _login(username: str, password: str | None = None) -> TestClient:
        client = TestClient(app, follow_redirects=False, raise_server_exceptions=False)
        opened.append(client)
        resp = client.post(
            "/login",
            data={"username": username, "password": password or PASSWORDS[username]},
        )
        assert resp.status_code == 303, f"login failed for {username}: {resp.status_code}"
        assert "access_token" in client.cookies, "login did not set the auth cookie"
        return client

    yield _login
    for c in opened:
        c.close()


def assert_unauthorized(resp) -> None:
    """The app renders ``401.html`` for any failed auth dependency."""
    assert "Return to Login" in resp.text
    assert "Unauthorized" in resp.text


def redirect_path(resp) -> str:
    """Path (+query) of a redirect's Location header, host stripped."""
    from urllib.parse import urlparse

    parsed = urlparse(resp.headers["location"])
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


def approved_total(db: Session, user: User) -> float:
    """Sum of a user's approved hours read fresh from the database."""
    from sqlmodel import select

    db.expire_all()
    rows = db.exec(select(HourLog).where(HourLog.user_id == user.id, HourLog.status == "approved")).all()
    return sum(r.hours for r in rows)
