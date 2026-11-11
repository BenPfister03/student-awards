"""IT-AUTH: login, logout, registration and token handling through the real HTTP stack."""
from datetime import timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.utilities.security import create_access_token
from tests.conftest import assert_unauthorized, redirect_path

pytestmark = pytest.mark.integration


# ---------------- public pages ----------------
def test_health_endpoint_reports_ok(anon):
    resp = anon.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_landing_page_is_public(anon):
    assert anon.get("/").status_code == 200


def test_login_page_renders_username_and_password_fields(anon):
    resp = anon.get("/login")
    assert resp.status_code == 200
    assert 'name="username"' in resp.text and 'name="password"' in resp.text


def test_register_page_renders_form(anon):
    resp = anon.get("/register")
    assert resp.status_code == 200
    assert 'name="email"' in resp.text


# ---------------- login ----------------
def test_student_login_redirects_home_and_sets_httponly_cookie(world, anon):
    resp = anon.post("/login", data={"username": "bob", "password": "bobpass"})
    assert resp.status_code == 303
    assert redirect_path(resp) == "/app"
    assert "access_token=" in resp.headers["set-cookie"]
    assert "httponly" in resp.headers["set-cookie"].lower()


def test_admin_login_redirects_to_admin_dashboard(world, anon):
    resp = anon.post("/login", data={"username": "admin", "password": "adminpass"})
    assert resp.status_code == 303
    assert redirect_path(resp) == "/admin"


def test_login_cookie_contains_user_id_and_role(world, anon):
    anon.post("/login", data={"username": "admin", "password": "adminpass"})
    s = get_settings()
    claims = jwt.decode(anon.cookies["access_token"], s.secret_key, algorithms=[s.jwt_algorithm])
    assert claims["sub"] == str(world["admin"].id)
    assert claims["role"] == "admin"


@pytest.mark.parametrize(
    "username,password",
    [("bob", "wrongpass"), ("ghost", "bobpass"), ("BOB", "bobpass")],
)
def test_bad_credentials_redirect_back_with_error_and_no_cookie(world, anon, username, password):
    resp = anon.post("/login", data={"username": username, "password": password})
    assert resp.status_code == 303
    assert redirect_path(resp) == "/login"
    assert "access_token" not in anon.cookies
    assert "Incorrect username or password" in anon.get("/login").text


def test_login_with_missing_fields_is_rejected_with_422(world, anon):
    assert anon.post("/login", data={"username": "bob"}).status_code == 422


# ---------------- session ----------------
def test_logged_in_user_can_reach_home(login):
    resp = login("bob").get("/app")
    assert resp.status_code == 200
    assert "Approved Hours" in resp.text


def test_logout_redirects_to_login_and_ends_session(login):
    bob = login("bob")
    resp = bob.get("/logout")
    assert resp.status_code == 303
    assert redirect_path(resp) == "/login"
    assert_unauthorized(bob.get("/app"))


def test_two_users_have_independent_sessions(login):
    bob, admin = login("bob"), login("admin")
    assert bob.get("/app").status_code == 200
    assert admin.get("/admin").status_code == 200
    assert_unauthorized(bob.get("/admin"))


# ---------------- token handling ----------------
def test_tampered_token_is_rejected(world, anon):
    anon.cookies.set("access_token", "not.a.jwt")
    assert_unauthorized(anon.get("/app"))


def test_token_signed_with_wrong_key_is_rejected(world, anon):
    forged = jwt.encode(
        {"sub": str(world["bob"].id), "role": "admin"},
        "wrong-key-that-is-long-enough-to-avoid-insecure-key-warning-1234",
        algorithm="HS256",
    )
    anon.cookies.set("access_token", forged)
    assert_unauthorized(anon.get("/admin"))


def test_expired_token_is_rejected(world, anon):
    token = create_access_token({"sub": str(world["bob"].id)}, expires_delta=timedelta(seconds=-10))
    anon.cookies.set("access_token", token)
    assert_unauthorized(anon.get("/app"))


def test_token_for_deleted_user_is_rejected(world, anon):
    token = create_access_token({"sub": "99999", "role": "regular_user"})
    anon.cookies.set("access_token", token)
    assert_unauthorized(anon.get("/app"))


def test_role_claim_in_token_cannot_grant_admin_access(world):
    """Authorisation is decided from the DB row, not from the (client-held) token claim."""
    token = create_access_token({"sub": str(world["bob"].id), "role": "admin"})
    client = TestClient(app, follow_redirects=False, raise_server_exceptions=False)
    client.cookies.set("access_token", token)
    assert_unauthorized(client.get("/admin/approvals"))


# ---------------- registration ----------------
def test_register_creates_account_then_user_can_log_in(world, anon):
    resp = anon.post(
        "/register", data={"username": "newbie", "email": "newbie@example.com", "password": "pw12345"}
    )
    assert resp.status_code == 303
    assert redirect_path(resp) == "/login"
    assert "Registration completed" in anon.get("/login").text
    login_resp = anon.post("/login", data={"username": "newbie", "password": "pw12345"})
    assert redirect_path(login_resp) == "/app"


def test_new_registrations_are_students_not_admins(world, anon):
    anon.post("/register", data={"username": "newbie", "email": "n@example.com", "password": "pw"})
    anon.post("/login", data={"username": "newbie", "password": "pw"})
    assert_unauthorized(anon.get("/admin"))


def test_register_duplicate_username_is_refused(world, anon):
    resp = anon.post("/register", data={"username": "bob", "email": "other@example.com", "password": "x"})
    assert redirect_path(resp) == "/register"
    assert "Username or email already exists" in anon.get("/register").text


def test_register_duplicate_email_is_refused(world, anon):
    resp = anon.post("/register", data={"username": "other", "email": "bob@example.com", "password": "x"})
    assert redirect_path(resp) == "/register"
    assert "Username or email already exists" in anon.get("/register").text


def test_register_with_missing_field_returns_422(world, anon):
    assert anon.post("/register", data={"username": "x", "password": "y"}).status_code == 422
