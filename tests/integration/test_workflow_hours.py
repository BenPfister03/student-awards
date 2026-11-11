"""IT-WF1: Log and approve volunteer hours (Student + Admin)."""
import re

import pytest
from sqlmodel import select

from app.models.hourlog import HourLog
from app.models.milestone import UserMilestone
from tests.conftest import approved_total, redirect_path

pytestmark = pytest.mark.integration


def _submit(client, world, hours=3, note="photo", activity="beach"):
    return client.post(
        "/hours/submit",
        data={"activity_id": world[activity].id, "hours": hours, "proof_note": note},
    )


def _home_stat(html: str, label: str) -> str:
    m = re.search(rf"{label}</h6>\s*<p class=\"h\d mb-0\">(.*?)</p>", html, re.S)
    assert m, f"stat {label!r} not found on home page"
    return m.group(1).strip()


def test_log_form_lists_only_active_activities(world, login):
    html = login("bob").get("/hours/log").text
    assert "Beach cleanup" in html and "Food drive" in html
    assert "Retired activity" not in html


def test_empty_history_message_for_new_student(world, login):
    assert "You have not submitted any hour entries yet" in login("bob").get("/hours/log").text


def test_submit_creates_pending_entry_and_redirects_home(world, login):
    resp = _submit(login("bob"), world, hours=3, note="photo")
    assert resp.status_code == 303 and redirect_path(resp) == "/app"
    world["db"].expire_all()
    log = world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).one()
    assert (log.status, log.hours, log.proof_note) == ("pending", 3.0, "photo")


def test_submitted_entry_shows_in_student_history_as_pending(world, login):
    bob = login("bob")
    _submit(bob, world, hours=2.5)
    html = bob.get("/hours/log").text
    assert "Beach cleanup" in html and "2.5" in html and "pending" in html


def test_proof_note_is_optional(world, login):
    resp = login("bob").post(
        "/hours/submit", data={"activity_id": world["beach"].id, "hours": 1}
    )
    assert resp.status_code == 303


@pytest.mark.parametrize("data", [{"hours": 1}, {"activity_id": 1}, {"activity_id": "x", "hours": 1}, {"activity_id": 1, "hours": "abc"}])
def test_submit_with_missing_or_malformed_fields_returns_422(world, login, data):
    assert login("bob").post("/hours/submit", data=data).status_code == 422


def test_pending_hours_do_not_count_until_approved(world, login):
    bob = login("bob")
    _submit(bob, world, hours=20)
    assert approved_total(world["db"], world["bob"]) == 0
    assert _home_stat(bob.get("/app").text, "Approved Hours") in ("0", "0.0")


def test_admin_queue_shows_student_activity_hours_and_note(world, login):
    _submit(login("bob"), world, hours=2, note="photo evidence", activity="food")
    html = login("admin").get("/admin/approvals").text
    assert "bob" in html and "Food drive" in html and "2.0" in html and "photo evidence" in html
    assert "Approve" in html and "Reject" in html


def test_admin_queue_empty_state(world, login):
    assert "No pending entries" in login("admin").get("/admin/approvals").text


def test_admin_home_counts_pending_entries(world, login):
    bob = login("bob")
    _submit(bob, world)
    _submit(bob, world)
    html = login("admin").get("/admin").text
    assert re.search(r"Pending Hours</h5>\s*<p class=\"display-6 mb-0\">2</p>", html)


# ---------------- approve ----------------
def test_approve_updates_status_and_clears_queue(world, login):
    bob, admin = login("bob"), login("admin")
    _submit(bob, world, hours=4)
    log = world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).one()
    resp = admin.post(f"/admin/approvals/{log.id}/approve")
    assert resp.status_code == 303 and redirect_path(resp) == "/admin/approvals"
    world["db"].refresh(log)
    assert log.status == "approved" and log.reviewed_by == world["admin"].id
    assert "No pending entries" in admin.get("/admin/approvals").text


def test_approval_increases_student_total_hours(world, login):
    bob, admin = login("bob"), login("admin")
    _submit(bob, world, hours=4)
    log = world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).one()
    admin.post(f"/admin/approvals/{log.id}/approve")
    assert approved_total(world["db"], world["bob"]) == 4.0
    assert _home_stat(bob.get("/app").text, "Approved Hours") == "4.0"
    assert _home_stat(bob.get("/app").text, "Redeemable Balance") == "4.0"


def test_approval_showing_in_history_as_approved(world, login):
    bob, admin = login("bob"), login("admin")
    _submit(bob, world, hours=4)
    log = world["db"].exec(select(HourLog)).all()[-1]
    admin.post(f"/admin/approvals/{log.id}/approve")
    assert "approved" in bob.get("/hours/log").text


def test_approval_reaching_threshold_unlocks_milestone(world, login):
    bob, admin = login("bob"), login("admin")
    _submit(bob, world, hours=10)
    log = world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).one()
    admin.post(f"/admin/approvals/{log.id}/approve")
    world["db"].expire_all()
    unlocked = world["db"].exec(select(UserMilestone).where(UserMilestone.user_id == world["bob"].id)).all()
    assert [u.milestone_id for u in unlocked] == [world["bronze"].id]


# ---------------- reject ----------------
def test_reject_records_reason_and_student_sees_it(world, login):
    bob, admin = login("bob"), login("admin")
    _submit(bob, world, hours=6)
    log = world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).one()
    resp = admin.post(f"/admin/approvals/{log.id}/reject", data={"reason": "Photo is blurry"})
    assert resp.status_code == 303 and redirect_path(resp) == "/admin/approvals"
    html = bob.get("/hours/log").text
    assert "rejected" in html and "Photo is blurry" in html
    assert approved_total(world["db"], world["bob"]) == 0


def test_reject_requires_a_reason(world, login):
    _submit(login("bob"), world)
    log = world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).one()
    assert login("admin").post(f"/admin/approvals/{log.id}/reject").status_code == 422
    world["db"].refresh(log)
    assert log.status == "pending"


def test_rejected_entry_does_not_unlock_milestones(world, login):
    bob, admin = login("bob"), login("admin")
    _submit(bob, world, hours=60)
    log = world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).one()
    admin.post(f"/admin/approvals/{log.id}/reject", data={"reason": "no"})
    world["db"].expire_all()
    assert world["db"].exec(select(UserMilestone).where(UserMilestone.user_id == world["bob"].id)).all() == []


def test_students_only_see_their_own_history(world, login):
    _submit(login("bob"), world, hours=7)
    log = world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).one()
    login("admin").post(f"/admin/approvals/{log.id}/reject", data={"reason": "bob-only-reason-xyz"})
    assert "bob-only-reason-xyz" in login("bob").get("/hours/log").text
    assert "bob-only-reason-xyz" not in login("amy").get("/hours/log").text
