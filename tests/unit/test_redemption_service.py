"""UT-REDEEM: app.services.redemption_service.RedemptionService."""
import pytest
from sqlmodel import select

from app.models.prize import Prize, Redemption
from app.services.redemption_service import RedemptionService
from tests.conftest import make_approved_hours, make_user

pytestmark = pytest.mark.unit


@pytest.fixture()
def svc(db):
    return RedemptionService(db)


@pytest.fixture()
def rich_student(db, student, catalog):
    """bob with 30 approved hours."""
    make_approved_hours(db, student, catalog["beach"], 30.0)
    return student


# ---------------- redeem: happy path ----------------
def test_redeem_creates_requested_redemption(svc, rich_student, catalog):
    r = svc.redeem_prize(rich_student, catalog["bottle"].id)
    assert r.id is not None
    assert r.status == "requested"
    assert r.user_id == rich_student.id
    assert r.prize_id == catalog["bottle"].id
    assert r.hours_cost == 10.0


def test_redeem_deducts_hours_cost_from_balance(db, svc, rich_student, catalog):
    svc.redeem_prize(rich_student, catalog["bottle"].id)
    db.refresh(rich_student)
    assert rich_student.points_spent == pytest.approx(10.0)


def test_redeem_decrements_stock_by_one(db, svc, rich_student, catalog):
    svc.redeem_prize(rich_student, catalog["bottle"].id)
    db.refresh(catalog["bottle"])
    assert catalog["bottle"].stock == 4


def test_redeem_snapshots_cost_even_if_price_changes_later(db, svc, rich_student, catalog):
    r = svc.redeem_prize(rich_student, catalog["bottle"].id)
    catalog["bottle"].hours_cost = 99.0
    db.add(catalog["bottle"])
    db.commit()
    db.refresh(r)
    assert r.hours_cost == 10.0


def test_redeem_can_spend_exact_balance(db, svc, student, catalog):
    make_approved_hours(db, student, catalog["beach"], 10.0)
    svc.redeem_prize(student, catalog["bottle"].id)  # cost 10
    db.refresh(student)
    assert student.points_spent == pytest.approx(10.0)


def test_same_prize_can_be_redeemed_repeatedly_while_balance_and_stock_allow(db, svc, rich_student, catalog):
    svc.redeem_prize(rich_student, catalog["bottle"].id)
    svc.redeem_prize(rich_student, catalog["bottle"].id)
    assert len(db.exec(select(Redemption)).all()) == 2
    db.refresh(rich_student)
    assert rich_student.points_spent == pytest.approx(20.0)


def test_redeem_takes_prior_spending_into_account(db, svc, rich_student, catalog):
    svc.redeem_prize(rich_student, catalog["mug"].id)     # 15 -> 15 left
    with pytest.raises(Exception, match="Insufficient balance"):
        svc.redeem_prize(rich_student, catalog["tshirt"].id)  # needs 25


# ---------------- redeem: failures leave state untouched ----------------
def test_redeem_with_insufficient_hours_reports_shortfall(db, svc, student, catalog):
    make_approved_hours(db, student, catalog["beach"], 4.0)
    with pytest.raises(Exception, match="need 6 more hours"):
        svc.redeem_prize(student, catalog["bottle"].id)


def test_failed_redeem_changes_nothing(db, svc, student, catalog):
    with pytest.raises(Exception):
        svc.redeem_prize(student, catalog["bottle"].id)
    db.refresh(student)
    db.refresh(catalog["bottle"])
    assert student.points_spent == 0
    assert catalog["bottle"].stock == 5
    assert db.exec(select(Redemption)).all() == []


def test_redeem_out_of_stock_prize_fails(db, svc, rich_student, catalog):
    with pytest.raises(Exception, match="Out of stock"):
        svc.redeem_prize(rich_student, catalog["tote"].id)


def test_redeem_inactive_prize_fails(svc, rich_student, catalog):
    with pytest.raises(Exception, match="Prize not available"):
        svc.redeem_prize(rich_student, catalog["hidden"].id)


def test_redeem_unknown_prize_fails(svc, rich_student):
    with pytest.raises(Exception, match="Prize not available"):
        svc.redeem_prize(rich_student, 9999)


def test_pending_and_rejected_hours_are_not_spendable(db, svc, student, catalog):
    from app.models.hourlog import HourLog

    db.add_all(
        [
            HourLog(user_id=student.id, activity_id=catalog["beach"].id, hours=50, status="pending"),
            HourLog(user_id=student.id, activity_id=catalog["beach"].id, hours=50, status="rejected"),
        ]
    )
    db.commit()
    with pytest.raises(Exception, match="Insufficient balance"):
        svc.redeem_prize(student, catalog["bottle"].id)


def test_last_unit_of_stock_can_be_redeemed_then_sells_out(db, svc, rich_student, catalog):
    catalog["bottle"].stock = 1
    db.add(catalog["bottle"])
    db.commit()
    svc.redeem_prize(rich_student, catalog["bottle"].id)
    with pytest.raises(Exception, match="Out of stock"):
        svc.redeem_prize(rich_student, catalog["bottle"].id)


# ---------------- fulfil ----------------
def test_fulfill_marks_fulfilled_with_admin_and_timestamp(svc, rich_student, admin, catalog):
    r = svc.redeem_prize(rich_student, catalog["bottle"].id)
    done = svc.fulfill(r.id, admin.id)
    assert done.status == "fulfilled"
    assert done.fulfilled_by == admin.id
    assert done.fulfilled_at is not None


def test_fulfill_does_not_refund_or_restock(db, svc, rich_student, admin, catalog):
    r = svc.redeem_prize(rich_student, catalog["bottle"].id)
    svc.fulfill(r.id, admin.id)
    db.refresh(rich_student)
    db.refresh(catalog["bottle"])
    assert rich_student.points_spent == pytest.approx(10.0)
    assert catalog["bottle"].stock == 4


def test_fulfill_unknown_redemption_raises(svc, admin):
    with pytest.raises(Exception, match="Redemption not found"):
        svc.fulfill(9999, admin.id)
