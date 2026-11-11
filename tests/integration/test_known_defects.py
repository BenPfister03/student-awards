"""IT-DEFECT: behaviour the *requirements* demand but the current code does not provide.

Each test states the CORRECT behaviour and is marked ``xfail`` so the suite stays
green today.  When a defect is fixed its test starts to XPASS - remove the marker
then.  These findings are listed in the Test Reporting section of the report.
"""
import pytest
from sqlmodel import select

from app.models.hourlog import HourLog
from tests.conftest import assert_unauthorized

pytestmark = pytest.mark.integration


def _count_logs(world):
    world["db"].expire_all()
    return len(world["db"].exec(select(HourLog).where(HourLog.user_id == world["bob"].id)).all())


@pytest.mark.xfail(reason="DEF-01: negative hours are accepted by /hours/submit", strict=False)
def test_negative_hours_are_rejected(world, login):
    login("bob").post("/hours/submit", data={"activity_id": world["beach"].id, "hours": -5, "proof_note": "x"})
    assert _count_logs(world) == 0


@pytest.mark.xfail(reason="DEF-02: zero hours are accepted by /hours/submit", strict=False)
def test_zero_hours_are_rejected(world, login):
    login("bob").post("/hours/submit", data={"activity_id": world["beach"].id, "hours": 0, "proof_note": "x"})
    assert _count_logs(world) == 0


@pytest.mark.xfail(reason="DEF-03: submitting against a non-existent / inactive activity is accepted", strict=False)
def test_inactive_activity_is_rejected(world, login):
    login("bob").post("/hours/submit", data={"activity_id": world["retired"].id, "hours": 2, "proof_note": "x"})
    assert _count_logs(world) == 0


@pytest.mark.xfail(reason="DEF-04: Jinja environment has autoescape off - stored XSS via proof_note", strict=False)
def test_proof_note_html_is_escaped_in_admin_queue(world, login):
    payload = "<script>alert(1)</script>"
    login("bob").post("/hours/submit", data={"activity_id": world["beach"].id, "hours": 1, "proof_note": payload})
    assert payload not in login("admin").get("/admin/approvals").text


@pytest.mark.xfail(reason="DEF-05: unknown hour-log id raises -> HTTP 500 instead of 404", strict=False)
def test_approving_unknown_entry_returns_404(world, login):
    assert login("admin").post("/admin/approvals/99999/approve").status_code == 404


@pytest.mark.xfail(reason="DEF-06: 401 page is returned with HTTP 200, not 401", strict=False)
def test_unauthenticated_page_request_returns_401_status(world, anon):
    resp = anon.get("/app")
    assert_unauthorized(resp)
    assert resp.status_code == 401


@pytest.mark.xfail(reason="DEF-07: /api/users is unauthenticated and lists every user's e-mail", strict=False)
def test_api_users_requires_authentication(world, anon):
    assert anon.get("/api/users").status_code in (401, 403)
