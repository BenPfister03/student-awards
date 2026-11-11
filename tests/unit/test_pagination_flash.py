"""UT-UTIL: app.utilities.pagination and app.utilities.flash."""
from types import SimpleNamespace

import pytest

from app.utilities.flash import flash, get_flashed_messages
from app.utilities.pagination import Pagination

pytestmark = pytest.mark.unit


# ---------------- Pagination ----------------
def test_total_pages_rounds_up():
    assert Pagination(total_count=21, current_page=1, limit=10).total_pages == 3


def test_total_pages_zero_rows():
    assert Pagination(total_count=0, current_page=1, limit=10).total_pages == 0


def test_total_pages_with_zero_limit_is_one():
    assert Pagination(total_count=50, current_page=1, limit=0).total_pages == 1


def test_first_page_has_next_but_no_prev():
    p = Pagination(total_count=30, current_page=1, limit=10)
    assert p.has_prev is False
    assert p.has_next is True
    assert p.next_num == 2


def test_middle_page_has_both_neighbours():
    p = Pagination(total_count=30, current_page=2, limit=10)
    assert (p.has_prev, p.has_next) == (True, True)
    assert (p.prev_num, p.next_num) == (1, 3)


def test_last_page_has_prev_but_no_next():
    p = Pagination(total_count=30, current_page=3, limit=10)
    assert p.has_prev is True
    assert p.has_next is False


def test_iter_pages_small_set_lists_every_page():
    assert list(Pagination(30, 1, 10).iter_pages()) == [1, 2, 3]


def test_iter_pages_inserts_gap_marker_for_large_sets():
    pages = list(Pagination(total_count=200, current_page=10, limit=10).iter_pages())
    assert None in pages
    assert pages[0] == 1 and pages[-1] == 20


# ---------------- Flash ----------------
def _fake_request():
    return SimpleNamespace(session={})


def test_flash_defaults_to_success_type():
    req = _fake_request()
    flash(req, "Saved")
    assert req.session["_messages"] == [{"message": "Saved", "type": "success"}]


def test_flash_accumulates_messages_in_order():
    req = _fake_request()
    flash(req, "one")
    flash(req, "two", "danger")
    assert [m["message"] for m in req.session["_messages"]] == ["one", "two"]
    assert req.session["_messages"][1]["type"] == "danger"


def test_get_flashed_messages_pops_and_clears():
    req = _fake_request()
    flash(req, "hello")
    assert get_flashed_messages(req)[0]["message"] == "hello"
    assert get_flashed_messages(req) == []


def test_get_flashed_messages_empty_session():
    assert get_flashed_messages(_fake_request()) == []
