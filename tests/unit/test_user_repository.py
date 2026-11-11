"""UT-REPO-USER: app.repositories.user.UserRepository against in-memory SQLite."""
import pytest

from app.repositories.user import UserRepository
from app.schemas.user import RegularUserCreate, UserUpdate
from tests.conftest import make_user

pytestmark = pytest.mark.unit


@pytest.fixture()
def repo(db):
    return UserRepository(db)


def test_create_persists_user_and_assigns_id(repo):
    created = repo.create(RegularUserCreate(username="zed", email="zed@example.com", password="h"))
    assert created.id is not None
    assert repo.get_by_username("zed").email == "zed@example.com"


def test_create_duplicate_username_raises_and_rolls_back(repo):
    repo.create(RegularUserCreate(username="zed", email="zed@example.com", password="h"))
    with pytest.raises(Exception):
        repo.create(RegularUserCreate(username="zed", email="zed2@example.com", password="h"))
    # session is still usable after the rollback
    assert len(repo.get_all_users()) == 1


def test_get_by_username_returns_none_when_missing(repo):
    assert repo.get_by_username("ghost") is None


def test_get_by_id_returns_user(db, repo):
    bob = make_user(db, "bob")
    assert repo.get_by_id(bob.id).username == "bob"


def test_get_by_id_returns_none_when_missing(repo):
    assert repo.get_by_id(999) is None


def test_get_all_users_returns_everyone(db, repo):
    make_user(db, "bob")
    make_user(db, "amy")
    assert {u.username for u in repo.get_all_users()} == {"bob", "amy"}


def test_search_users_filters_by_username_case_insensitively(db, repo):
    make_user(db, "bob")
    make_user(db, "amy")
    users, pagination = repo.search_users("BO")
    assert [u.username for u in users] == ["bob"]
    assert pagination.total_count == 1


def test_search_users_filters_by_email(db, repo):
    make_user(db, "bob")
    make_user(db, "amy")
    users, _ = repo.search_users("amy@")
    assert [u.username for u in users] == ["amy"]


def test_search_users_paginates(db, repo):
    for i in range(5):
        make_user(db, f"user{i}")
    page1, p1 = repo.search_users("", page=1, limit=2)
    page3, p3 = repo.search_users("", page=3, limit=2)
    assert len(page1) == 2 and len(page3) == 1
    assert p1.total_pages == 3 and p1.has_next and p3.has_prev


def test_update_user_changes_username_and_email(db, repo):
    bob = make_user(db, "bob")
    updated = repo.update_user(bob.id, UserUpdate(username="bobby", email="bobby@example.com"))
    assert (updated.username, updated.email) == ("bobby", "bobby@example.com")


def test_update_user_ignores_empty_fields(db, repo):
    bob = make_user(db, "bob")
    updated = repo.update_user(bob.id, UserUpdate(username=None, email=None))
    assert updated.username == "bob"


def test_update_unknown_user_raises(repo):
    with pytest.raises(Exception, match="Invalid user id"):
        repo.update_user(999, UserUpdate(username="x", email=None))


def test_delete_user_removes_row(db, repo):
    bob = make_user(db, "bob")
    repo.delete_user(bob.id)
    assert repo.get_by_id(bob.id) is None


def test_delete_unknown_user_raises(repo):
    with pytest.raises(Exception, match="doesn't exist"):
        repo.delete_user(999)
