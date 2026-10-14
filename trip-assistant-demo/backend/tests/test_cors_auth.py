"""Pokaz 1: CORS i middleware autoryzacji (modules/auth/)."""
import jwt

OK_ORIGIN = "https://localhost:5173"
EVIL_ORIGIN = "https://evil.example"


def preflight(client, origin, method="GET"):
    return client.options(
        "/trips", headers={"Origin": origin, "Access-Control-Request-Method": method}
    )


def test_cors_allows_configured_origin(client):
    r = preflight(client, OK_ORIGIN)
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == OK_ORIGIN


def test_cors_rejects_foreign_origin(client):
    r = preflight(client, EVIL_ORIGIN)
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers


def test_cors_rejects_unlisted_method(client):
    assert preflight(client, OK_ORIGIN, method="PUT").status_code == 400


def test_no_token_gives_401(client):
    assert client.get("/trips").status_code == 401


def test_garbage_token_gives_401(client):
    r = client.get("/trips", headers={"Authorization": "Bearer abc.def.ghi"})
    assert r.status_code == 401


def test_token_signed_with_wrong_secret_gives_401(client):
    forged = jwt.encode({"sub": "1"}, "another-wrong-secret-0123456789abcdef", algorithm="HS256")
    assert client.get("/trips", headers={"Authorization": f"Bearer {forged}"}).status_code == 401


def test_alg_none_token_gives_401(client):
    unsigned = jwt.encode({"sub": "1"}, "", algorithm="none")
    assert client.get("/trips", headers={"Authorization": f"Bearer {unsigned}"}).status_code == 401


def test_valid_token_gives_200(client, alice):
    assert client.get("/trips", headers=alice).status_code == 200
