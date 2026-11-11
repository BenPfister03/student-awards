"""UT-HOURLOG: app.services.hourlog_service.HourLogService (submit / approve / reject)."""
import pytest
from sqlmodel import select

from app.models.hourlog import HourLog
from app.models.milestone import UserMilestone
from app.services.hourlog_service import HourLogService
from tests.conftest import make_approved_hours

pytestmark = pytest.mark.unit


@pytest.fixture()
def svc(db):
    return HourLogService(db)


def _submit(svc, student, activity, hours=2.0, note="photo"):
    return svc.submit_hourlog(
        {"user_id": student.id, "activity_id": activity.id, "hours": hours, "proof_note": note}
    )


def _unlocked_names(db, user):
    rows = db.exec(select(UserMilestone).where(UserMilestone.user_id == user.id)).all()
    return {r.milestone_id for r in rows}


# ---------------- submit ----------------
def test_submit_creates_pending_log(svc, student, catalog):
    log = _submit(svc, student, catalog["beach"], hours=3.0)
    assert log.id is not None
    assert log.status == "pending"
    assert log.hours == 3.0
    assert log.user_id == student.id
    assert log.proof_note == "photo"


def test_submit_does_not_award_hours_or_milestones(db, svc, student, catalog):
    _submit(svc, student, catalog["beach"], hours=100.0)
    assert _unlocked_names(db, student) == set()


# ---------------- list_pending ----------------
def test_list_pending_returns_only_pending_oldest_first(svc, student, admin, catalog):
    first = _submit(svc, student, catalog["beach"], 1)
    second = _submit(svc, student, catalog["food"], 2)
    done = _submit(svc, student, catalog["beach"], 3)
    svc.approve(done.id, admin.id)
    assert [h.id for h in svc.list_pending()] == [first.id, second.id]


def test_list_pending_empty(svc):
    assert svc.list_pending() == []


# ---------------- approve ----------------
def test_approve_sets_status_reviewer_and_timestamp(svc, student, admin, catalog):
    log = _submit(svc, student, catalog["beach"])
    approved = svc.approve(log.id, admin.id)
    assert approved.status == "approved"
    assert approved.reviewed_by == admin.id
    assert approved.reviewed_at is not None


def test_approve_below_threshold_unlocks_nothing(db, svc, student, admin, catalog):
    log = _submit(svc, student, catalog["beach"], hours=9.75)
    svc.approve(log.id, admin.id)
    assert _unlocked_names(db, student) == set()


def test_approve_at_exact_threshold_unlocks_bronze(db, svc, student, admin, catalog):
    log = _submit(svc, student, catalog["beach"], hours=10.0)
    svc.approve(log.id, admin.id)
    assert _unlocked_names(db, student) == {catalog["bronze"].id}


def test_approve_crossing_several_thresholds_unlocks_all_of_them(db, svc, student, admin, catalog):
    log = _submit(svc, student, catalog["beach"], hours=30.0)
    svc.approve(log.id, admin.id)
    assert _unlocked_names(db, student) == {catalog["bronze"].id, catalog["silver"].id}


def test_approve_counts_lifetime_approved_hours_not_just_this_log(db, svc, student, admin, catalog):
    make_approved_hours(db, student, catalog["beach"], 8.0)
    log = _submit(svc, student, catalog["food"], hours=2.0)
    svc.approve(log.id, admin.id)
    assert catalog["bronze"].id in _unlocked_names(db, student)


def test_pending_and_rejected_hours_do_not_count_towards_milestones(db, svc, student, admin, catalog):
    big_pending = _submit(svc, student, catalog["beach"], hours=50.0)
    rejected = _submit(svc, student, catalog["beach"], hours=50.0)
    svc.reject(rejected.id, admin.id, "no proof")
    small = _submit(svc, student, catalog["food"], hours=1.0)
    svc.approve(small.id, admin.id)
    assert big_pending.status == "pending"
    assert _unlocked_names(db, student) == set()


def test_approve_never_creates_duplicate_user_milestones(db, svc, student, admin, catalog):
    for _ in range(3):
        svc.approve(_submit(svc, student, catalog["beach"], hours=11.0).id, admin.id)
    rows = db.exec(
        select(UserMilestone).where(
            UserMilestone.user_id == student.id,
            UserMilestone.milestone_id == catalog["bronze"].id,
        )
    ).all()
    assert len(rows) == 1


def test_approve_keeps_original_unlock_timestamp(db, svc, student, admin, catalog):
    svc.approve(_submit(svc, student, catalog["beach"], hours=10.0).id, admin.id)
    first = db.exec(select(UserMilestone)).one().unlocked_at
    svc.approve(_submit(svc, student, catalog["beach"], hours=1.0).id, admin.id)
    assert db.exec(select(UserMilestone)).one().unlocked_at == first


def test_approve_only_unlocks_for_the_submitting_student(db, svc, student, admin, catalog):
    from tests.conftest import make_user

    other = make_user(db, "amy")
    svc.approve(_submit(svc, student, catalog["beach"], hours=12.0).id, admin.id)
    assert _unlocked_names(db, other) == set()


def test_approve_unknown_log_raises(svc, admin):
    with pytest.raises(Exception, match="HourLog not found"):
        svc.approve(9999, admin.id)


# ---------------- reject ----------------
def test_reject_sets_status_reason_and_reviewer(svc, student, admin, catalog):
    log = _submit(svc, student, catalog["beach"])
    rejected = svc.reject(log.id, admin.id, "Photo is unreadable")
    assert rejected.status == "rejected"
    assert rejected.reject_reason == "Photo is unreadable"
    assert rejected.reviewed_by == admin.id
    assert rejected.reviewed_at is not None


def test_reject_unlocks_no_milestones(db, svc, student, admin, catalog):
    svc.reject(_submit(svc, student, catalog["beach"], hours=60).id, admin.id, "fake")
    assert _unlocked_names(db, student) == set()


def test_reject_unknown_log_raises(svc, admin):
    with pytest.raises(Exception, match="HourLog not found"):
        svc.reject(9999, admin.id, "x")


def test_rejected_log_leaves_pending_queue(svc, student, admin, catalog):
    log = _submit(svc, student, catalog["beach"])
    svc.reject(log.id, admin.id, "nope")
    assert svc.list_pending() == []
