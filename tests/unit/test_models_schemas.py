"""UT-MODEL: default values / constraints of the SQLModel tables and schemas."""
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.hourlog import HourLog
from app.models.milestone import Milestone
from app.models.prize import Prize, Redemption
from app.models.user import User
from app.schemas.user import AdminCreate, RegularUserCreate, UserResponse
from tests.conftest import make_user

pytestmark = pytest.mark.unit


def test_hourlog_defaults_to_pending_and_unreviewed():
    log = HourLog(user_id=1, activity_id=1, hours=2)
    assert log.status == "pending"
    assert log.reviewed_by is None
    assert log.reviewed_at is None
    assert log.reject_reason is None
    assert log.submitted_at is not None


def test_redemption_defaults_to_requested():
    r = Redemption(user_id=1, prize_id=1, hours_cost=10)
    assert r.status == "requested"
    assert r.fulfilled_by is None and r.fulfilled_at is None


def test_prize_defaults_are_active_with_zero_stock():
    p = Prize(name="Pen", hours_cost=1)
    assert p.stock == 0
    assert p.is_active is True


def test_user_defaults_have_no_hours():
    u = User(username="x", email="x@example.com", password="h")
    assert u.total_hours == 0.0
    assert u.points_spent == 0.0


def test_milestone_has_created_timestamp():
    assert Milestone(name="Bronze", hours_threshold=10).created_at is not None


def test_regular_user_schema_defaults_role():
    assert RegularUserCreate(username="a", email="a@example.com", password="p").role == "regular_user"


def test_admin_schema_defaults_role():
    assert AdminCreate(username="a", email="a@example.com", password="p").role == "admin"


def test_user_response_schema_does_not_expose_password():
    assert "password" not in UserResponse.model_fields


def test_duplicate_username_violates_unique_constraint(db):
    make_user(db, "bob")
    with pytest.raises(IntegrityError):
        db.add(User(username="bob", email="other@example.com", password="h"))
        db.commit()


def test_duplicate_email_violates_unique_constraint(db):
    make_user(db, "bob")
    with pytest.raises(IntegrityError):
        db.add(User(username="bob2", email="bob@example.com", password="h"))
        db.commit()
