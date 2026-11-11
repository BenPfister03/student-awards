"""UT-AUTH: app.services.auth_service.AuthService (real repo, in-memory DB)."""
import jwt
import pytest

from app.config import get_settings
from app.repositories.user import UserRepository
from app.services.auth_service import AuthService
from app.utilities.security import verify_password
from tests.conftest import make_user

pytestmark = pytest.mark.unit


@pytest.fixture()
def service(db):
    return AuthService(UserRepository(db))


def _claims(token):
    s = get_settings()
    return jwt.decode(token, s.secret_key, algorithms=[s.jwt_algorithm])


def test_authenticate_returns_token_for_valid_credentials(db, service):
    bob = make_user(db, "bob")
    claims = _claims(service.authenticate_user("bob", "bobpass"))
    assert claims["sub"] == str(bob.id)
    assert claims["role"] == "regular_user"


def test_authenticate_token_carries_admin_role(db, service):
    make_user(db, "admin", role="admin")
    assert _claims(service.authenticate_user("admin", "adminpass"))["role"] == "admin"


def test_authenticate_wrong_password_returns_none(db, service):
    make_user(db, "bob")
    assert service.authenticate_user("bob", "nope") is None


def test_authenticate_unknown_user_returns_none(service):
    assert service.authenticate_user("ghost", "x") is None


def test_register_creates_regular_user_with_hashed_password(service):
    user = service.register_user("newbie", "newbie@example.com", "secret123")
    assert user.id is not None
    assert user.role == "regular_user"
    assert user.password != "secret123"
    assert verify_password("secret123", user.password)


def test_register_duplicate_username_raises(db, service):
    make_user(db, "bob")
    with pytest.raises(Exception):
        service.register_user("bob", "different@example.com", "pw")


def test_registered_user_can_then_authenticate(service):
    service.register_user("newbie", "newbie@example.com", "secret123")
    assert service.authenticate_user("newbie", "secret123") is not None
