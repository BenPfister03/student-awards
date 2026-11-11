"""IT-RBAC: every protected route against anonymous / student / admin callers."""
import pytest
from sqlmodel import select

from app.models.hourlog import HourLog
from app.models.prize import Redemption
from tests.conftest import assert_unauthorized, redirect_path

pytestmark = pytest.mark.integration

STUDENT_PAGES = ["/app", "/hours/log", "/leaderboard", "/milestones", "/prizes"]
ADMIN_PAGES = ["/admin", "/admin/approvals", "/redemptions"]


@pytest.mark.parametrize("path", STUDENT_PAGES + ADMIN_PAGES)
def test_anonymous_users_cannot_open_protected_pages(world, anon, path):
    assert_unauthorized(anon.get(path))


@pytest.mark.parametrize("path", STUDENT_PAGES)
def test_students_can_open_student_pages(login, path):
    assert login("bob").get(path).status_code == 200


@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_students_cannot_open_admin_pages(login, path):
    assert_unauthorized(login("bob").get(path))


@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_admins_can_open_admin_pages(login, path):
    assert login("admin").get(path).status_code == 200


@pytest.mark.parametrize("path", ["/leaderboard", "/milestones", "/prizes"])
def test_admins_can_view_shared_pages(login, path):
    assert login("admin").get(path).status_code == 200


def test_admin_is_redirected_away_from_student_home(login):
    resp = login("admin").get("/app")
    assert resp.status_code == 303 and redirect_path(resp) == "/admin"


def test_admin_is_redirected_away_from_log_hours_form(login):
    resp = login("admin").get("/hours/log")
    assert resp.status_code == 303 and redirect_path(resp) == "/admin/approvals"


def test_admin_cannot_submit_hours(world, login):
    resp = login("admin").post(
        "/hours/submit", data={"activity_id": world["beach"].id, "hours": 5, "proof_note": "x"}
    )
    assert resp.status_code == 303 and redirect_path(resp) == "/admin/approvals"
    world["db"].expire_all()
    assert world["db"].exec(select(HourLog).where(HourLog.user_id == world["admin"].id)).all() == []


# ---------------- state-changing endpoints ----------------
def _pending_log(world):
    db = world["db"]
    log = HourLog(user_id=world["bob"].id, activity_id=world["beach"].id, hours=3.0, proof_note="p")
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def test_anonymous_cannot_submit_hours(world, anon):
    resp = anon.post("/hours/submit", data={"activity_id": world["beach"].id, "hours": 1})
    assert_unauthorized(resp)


def test_anonymous_cannot_redeem(world, anon):
    assert_unauthorized(anon.post(f"/prizes/{world['bottle'].id}/redeem"))


def test_student_cannot_approve_hours(world, login):
    log = _pending_log(world)
    assert_unauthorized(login("bob").post(f"/admin/approvals/{log.id}/approve"))
    world["db"].refresh(log)
    assert log.status == "pending"


def test_student_cannot_reject_hours(world, login):
    log = _pending_log(world)
    assert_unauthorized(login("bob").post(f"/admin/approvals/{log.id}/reject", data={"reason": "x"}))
    world["db"].refresh(log)
    assert log.status == "pending"


def test_student_cannot_fulfil_redemptions(world, login):
    db = world["db"]
    r = Redemption(user_id=world["bob"].id, prize_id=world["bottle"].id, hours_cost=10)
    db.add(r)
    db.commit()
    db.refresh(r)
    assert_unauthorized(login("bob").post(f"/redemptions/{r.id}/fulfill"))
    db.refresh(r)
    assert r.status == "requested"


def test_anonymous_cannot_approve_hours(world, anon):
    log = _pending_log(world)
    assert_unauthorized(anon.post(f"/admin/approvals/{log.id}/approve"))
    world["db"].refresh(log)
    assert log.status == "pending"
