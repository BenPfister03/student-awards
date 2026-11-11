"""IT-API: JSON API, OpenAPI contract, static files and 404 behaviour."""
import pytest

pytestmark = pytest.mark.integration


def test_api_users_returns_json_list_of_users(world, anon):
    resp = anon.get("/api/users")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    assert {u["username"] for u in resp.json()} == {"admin", "bob", "amy", "cal"}


def test_api_users_exposes_only_id_username_email(world, anon):
    for user in anon.get("/api/users").json():
        assert set(user) == {"id", "username", "email"}


def test_api_users_never_leaks_password_hashes(world, anon):
    assert "argon2" not in anon.get("/api/users").text
    assert "password" not in anon.get("/api/users").text


def test_openapi_documents_the_api_endpoint(anon):
    spec = anon.get("/openapi.json")
    assert spec.status_code == 200
    assert "/api/users" in spec.json()["paths"]


def test_unknown_route_returns_404(anon):
    assert anon.get("/definitely/not/here").status_code == 404


def test_wrong_http_method_returns_405(anon):
    assert anon.delete("/api/users").status_code == 405


def test_static_stylesheet_is_served(anon):
    assert anon.get("/static/css/app.css").status_code == 200
