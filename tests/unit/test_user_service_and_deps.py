"""UT-USER-SVC / UT-DEP: UserService and the role helper in dependencies.auth."""
import asyncio
from types import SimpleNamespace

import pytest

from app.dependencies.auth import is_admin, is_admin_dep
from app.repositories.user import UserRepository
from app.services.user_service import UserService
from fastapi import HTTPException
from tests.conftest import make_user

pytestmark = pytest.mark.unit


def test_user_service_lists_all_users(db):
    make_user(db, "bob")
    make_user(db, "admin", role="admin")
    users = UserService(UserRepository(db)).get_all_users()
    assert {u.username for u in users} == {"bob", "admin"}


def test_is_admin_true_for_admin_role():
    assert asyncio.run(is_admin(SimpleNamespace(role="admin"))) is True


@pytest.mark.parametrize("role", ["regular_user", "student", ""])
def test_is_admin_false_for_other_roles(role):
    assert asyncio.run(is_admin(SimpleNamespace(role=role))) is False


def test_is_admin_dep_passes_admin_through():
    admin = SimpleNamespace(role="admin")
    assert asyncio.run(is_admin_dep(admin)) is admin


def test_is_admin_dep_blocks_students_with_401():
    with pytest.raises(HTTPException) as exc:
        asyncio.run(is_admin_dep(SimpleNamespace(role="regular_user")))
    assert exc.value.status_code == 401
