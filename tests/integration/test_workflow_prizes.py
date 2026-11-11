"""IT-WF3: Redeem a prize (Student) and fulfil it (Admin)."""
import re
from urllib.parse import unquote_plus

import pytest
from sqlmodel import select

from app.models.prize import Prize, Redemption
from tests.conftest import make_approved_hours, redirect_path

pytestmark = pytest.mark.integration


@pytest.fixture()
def bob_with_20h(world):
    make_approved_hours(world["db"], world["bob"], world["beach"], 20.0)
    return world["bob"]


def _balance(html: str) -> str:
    return re.search(r"Redeemable balance: <strong>(.*?)</strong>", html).group(1)


def _redeem(client, prize):
    return client.post(f"/prizes/{prize.id}/redeem")


# ---------------- browsing ----------------
def test_prizes_page_lists_active_prizes_only(world, login):
    html = login("bob").get("/prizes").text
    assert "Water bottle" in html and "T-shirt" in html
    assert "Hidden prize" not in html


def test_prizes_page_shows_balance(world, bob_with_20h, login):
    assert _balance(login("bob").get("/prizes").text) == "20.0"


def test_unaffordable_prize_is_disabled_with_hours_needed(world, bob_with_20h, login):
    html = login("bob").get("/prizes").text
    assert "Need 5.0 more hours" in html  # T-shirt costs 25, balance 20


def test_out_of_stock_prize_is_labelled(world, login):
    assert "Out of stock" in login("bob").get("/prizes").text


# ---------------- redeem ----------------
def test_redeem_deducts_balance_decrements_stock_and_creates_request(world, bob_with_20h, login):
    bob = login("bob")
    resp = _redeem(bob, world["bottle"])
    assert resp.status_code == 303 and redirect_path(resp) == "/prizes"
    db = world["db"]
    db.expire_all()
    assert db.get(Prize, world["bottle"].id).stock == 4
    redemption = db.exec(select(Redemption)).one()
    assert (redemption.user_id, redemption.status, redemption.hours_cost) == (world["bob"].id, "requested", 10.0)
    assert _balance(bob.get("/prizes").text) == "10.0"


def test_redeem_updates_home_balance_but_not_approved_hours(world, bob_with_20h, login):
    bob = login("bob")
    _redeem(bob, world["bottle"])
    html = bob.get("/app").text
    assert re.search(r"Approved Hours</h6>\s*<p class=\"h3 mb-0\">20.0</p>", html)
    assert re.search(r"Redeemable Balance</h6>\s*<p class=\"h3 mb-0\">10.0</p>", html)


def test_insufficient_balance_redirects_with_error_and_changes_nothing(world, login):
    bob = login("bob")  # 0 hours
    resp = _redeem(bob, world["bottle"])
    assert resp.status_code == 303
    assert "Insufficient balance: need 10 more hours" in unquote_plus(resp.headers["location"])
    assert "Insufficient balance: need 10 more hours" in bob.get(redirect_path(resp)).text
    db = world["db"]
    db.expire_all()
    assert db.exec(select(Redemption)).all() == []
    assert db.get(Prize, world["bottle"].id).stock == 5


def test_out_of_stock_prize_cannot_be_redeemed(world, bob_with_20h, login):
    resp = _redeem(login("bob"), world["tote"])
    assert "Out of stock" in unquote_plus(resp.headers["location"])


def test_inactive_prize_cannot_be_redeemed(world, bob_with_20h, login):
    resp = _redeem(login("bob"), world["hidden"])
    assert "Prize not available" in unquote_plus(resp.headers["location"])


def test_unknown_prize_cannot_be_redeemed(world, bob_with_20h, login):
    resp = login("bob").post("/prizes/99999/redeem")
    assert "Prize not available" in unquote_plus(resp.headers["location"])


def test_balance_cannot_be_overspent_by_repeat_redemptions(world, bob_with_20h, login):
    bob = login("bob")
    _redeem(bob, world["bottle"])   # 10
    _redeem(bob, world["bottle"])   # 10  -> 0 left
    resp = _redeem(bob, world["bottle"])
    assert "Insufficient balance" in unquote_plus(resp.headers["location"])
    world["db"].expire_all()
    assert len(world["db"].exec(select(Redemption)).all()) == 2


def test_stock_runs_out(world, bob_with_20h, login):
    world["bottle"].stock = 1
    world["db"].add(world["bottle"])
    world["db"].commit()
    bob = login("bob")
    _redeem(bob, world["bottle"])
    assert "Out of stock" in unquote_plus(_redeem(bob, world["bottle"]).headers["location"])


# ---------------- admin fulfilment ----------------
def test_admin_sees_redemption_request(world, bob_with_20h, login):
    _redeem(login("bob"), world["bottle"])
    html = login("admin").get("/redemptions").text
    rid = world["db"].exec(select(Redemption)).one().id
    assert "bob" in html and "Water bottle" in html and "Requested" in html
    assert f"/redemptions/{rid}/fulfill" in html


def test_admin_home_counts_requested_redemptions(world, bob_with_20h, login):
    _redeem(login("bob"), world["bottle"])
    html = login("admin").get("/admin").text
    assert re.search(r"Requested Redemptions</h5>\s*<p class=\"display-6 mb-0\">1</p>", html)


def test_admin_fulfils_redemption(world, bob_with_20h, login):
    _redeem(login("bob"), world["bottle"])
    admin = login("admin")
    rid = world["db"].exec(select(Redemption)).one().id
    resp = admin.post(f"/redemptions/{rid}/fulfill")
    assert resp.status_code == 303 and redirect_path(resp) == "/redemptions"
    world["db"].expire_all()
    r = world["db"].get(Redemption, rid)
    assert (r.status, r.fulfilled_by) == ("fulfilled", world["admin"].id)
    assert r.fulfilled_at is not None
    html = admin.get("/redemptions").text
    assert "bg-success" in html and f"/redemptions/{rid}/fulfill" not in html


def test_fulfilment_does_not_change_student_balance(world, bob_with_20h, login):
    bob, admin = login("bob"), login("admin")
    _redeem(bob, world["bottle"])
    admin.post(f"/redemptions/{world['db'].exec(select(Redemption)).one().id}/fulfill")
    assert _balance(bob.get("/prizes").text) == "10.0"
