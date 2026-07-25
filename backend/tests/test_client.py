"""The bundled web client (lives in web/, served by the API as a convenience)."""

import re
from pathlib import Path

from fastapi.testclient import TestClient

from northstar.api import _WEB_DIR, app

client = TestClient(app)


def test_web_client_lives_outside_the_backend_package():
    """The client is a separate deliverable: the API must not own it."""
    assert (_WEB_DIR / "index.html").is_file()
    assert _WEB_DIR.name == "web"
    backend_pkg = Path(__file__).resolve().parents[1] / "northstar"
    assert not (backend_pkg / "static").exists()


def test_root_serves_client_page():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    body = r.text
    assert "North Star" in body
    # the page drives the same API endpoints
    for path in ("subjects", "combinations", "interests", "match"):
        assert path in body


def test_client_has_no_third_party_dependencies():
    """No CDN scripts, fonts or stylesheets: the page must load and work on a
    phone with a poor connection, with nothing but the API to talk to."""
    body = client.get("/").text
    assert "<script src" not in body
    assert '<link rel="stylesheet"' not in body
    external = [
        u for u in re.findall(r"https?://[^\s\"'<>)]+", body)
        if not u.startswith(("http://127.0.0.1", "http://localhost"))
        and "www.w3.org" not in u  # SVG xmlns is an identifier, not a fetch
    ]
    assert not external, f"unexpected external resources: {external}"


def test_api_is_usable_without_a_client(monkeypatch, tmp_path):
    """The API is the product; the client is optional. Missing client must not
    break the API, and must say where it looked."""
    monkeypatch.setattr("northstar.api._WEB_DIR", tmp_path)
    r = client.get("/")
    assert r.status_code == 404
    assert "NORTH_STAR_WEB_DIR" in r.json()["detail"]
    assert client.get("/health").status_code == 200
    assert client.post(
        "/match", json={"grades": {"physics": "B", "chemistry": "A", "biology": "A"}}
    ).status_code == 200


def test_cors_allows_a_separately_hosted_client():
    r = client.post(
        "/match",
        headers={"Origin": "https://example.org"},
        json={"grades": {"physics": "B", "chemistry": "A", "biology": "A"}},
    )
    assert r.headers.get("access-control-allow-origin") == "*"
