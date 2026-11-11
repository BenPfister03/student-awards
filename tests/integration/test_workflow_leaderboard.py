"""IT-WF2: Leaderboard and milestones (Student)."""
import re

import pytest
from sqlmodel import select

from app.models.hourlog import HourLog
from tests.conftest import make_approved_hours

pytestmark = pytest.mark.integration


def _usernames_in_order(html: str) -> list[str]:
    return re.findall(r"<td>(\w+)(?: <small|\s*</td>| )", html)


def _approve_via_ui(world, login, student_name: str, hours: float):
    """Drive the real submit -> approve flow so milestone side-effects run."""
    student = login(student_name)
    student.post("/hours/submit", data={"activity_id": world["beach"].id, "hours": hours, "proof_note": "p"})
    log = world["db"].exec(
        select(HourLog).where(HourLog.user_id == world[student_name].id, HourLog.status == "pending")
    ).first()
    assert login("admin").post(f"/admin/approvals/{log.id}/approve").status_code == 303
    world["db"].expire_all()
    return student


# ---------------- leaderboard ----------------
def test_leaderboard_ranks_students_by_approved_hours_descending(world, login):
    html = login("bob").get("/leaderboard").text
    order = _usernames_in_order(html)
    assert order.index("amy") < order.index("cal") < order.index("bob")


def test_leaderboard_shows_hours_to_two_decimals(world, login):
    html = login("bob").get("/leaderboard").text
    assert "40.00" in html and "25.00" in html


def test_leaderboard_marks_the_current_user_and_shows_their_rank(world, login):
    html = login("bob").get("/leaderboard").text
    assert "(you)" in html
    assert re.search(r"Your rank:</strong>\s*3", html)


def test_leaderboard_excludes_admins(world, login):
    assert "<td>admin" not in login("bob").get("/leaderboard").text


def test_tie_is_broken_alphabetically(world, login):
    make_approved_hours(world["db"], world["bob"], world["beach"], 25.0)  # ties with cal
    order = _usernames_in_order(login("amy").get("/leaderboard").text)
    assert order.index("amy") < order.index("bob") < order.index("cal")


def test_pending_and_rejected_hours_are_ignored(world, login):
    world["db"].add_all(
        [
            HourLog(user_id=world["bob"].id, activity_id=world["beach"].id, hours=500, status="pending"),
            HourLog(user_id=world["bob"].id, activity_id=world["beach"].id, hours=500, status="rejected"),
        ]
    )
    world["db"].commit()
    html = login("bob").get("/leaderboard").text
    assert re.search(r"Your rank:</strong>\s*3", html)


def test_rank_changes_after_approval(world, login):
    bob = _approve_via_ui(world, login, "bob", 30)  # 30h beats cal's 25h
    html = bob.get("/leaderboard").text
    assert re.search(r"Your rank:</strong>\s*2", html)
    assert "30.00" in html


def test_student_with_no_hours_is_still_listed_with_zero(world, login):
    assert "0.00" in login("bob").get("/leaderboard").text


def test_home_page_shows_rank_after_approval(world, login):
    bob = _approve_via_ui(world, login, "bob", 30)
    assert re.search(r"Rank</h6>\s*<p class=\"h3 mb-0\">2</p>", bob.get("/app").text)


# ---------------- milestones ----------------
def test_milestones_page_lists_all_milestones_locked_for_new_student(world, login):
    html = login("bob").get("/milestones").text
    for name in ("Bronze", "Silver", "Gold"):
        assert name in html
    assert html.count("Unlocked") == 0
    assert html.count("Locked") == 3


def test_milestones_show_progress_to_next_milestone(world, login):
    bob = _approve_via_ui(world, login, "bob", 4)
    assert "4.00 / 10.0" in bob.get("/milestones").text


def test_crossing_threshold_unlocks_badge_and_advances_progress(world, login):
    bob = _approve_via_ui(world, login, "bob", 12)
    html = bob.get("/milestones").text
    assert html.count("Unlocked") == 1
    assert "12.00 / 25.0" in html


def test_big_approval_unlocks_multiple_badges(world, login):
    bob = _approve_via_ui(world, login, "bob", 30)
    assert bob.get("/milestones").text.count("Unlocked") == 2


def test_home_page_shows_latest_unlocked_milestone(world, login):
    bob = _approve_via_ui(world, login, "bob", 12)
    assert re.search(r"Latest Milestone</h6>\s*<p class=\"h5 mb-0\">Bronze</p>", bob.get("/app").text)


def test_other_students_milestones_are_not_shown(world, login):
    _approve_via_ui(world, login, "bob", 30)
    assert login("cal").get("/milestones").text.count("Unlocked") == 0


def test_milestones_and_rank_survive_redeeming_a_prize(world, login):
    bob = _approve_via_ui(world, login, "bob", 12)
    bob.post(f"/prizes/{world['bottle'].id}/redeem")  # spends 10h
    assert bob.get("/milestones").text.count("Unlocked") == 1
    assert "12.00" in bob.get("/leaderboard").text
