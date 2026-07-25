"""Thin web client (cycle 4): served by the API itself."""

from fastapi.testclient import TestClient

from northstar.api import app

client = TestClient(app)


def test_root_serves_client_page():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    body = r.text
    assert "North Star" in body
    # the page drives the same-origin API endpoints
    for path in ("subjects", "combinations", "interests", "match"):
        assert path in body


def test_client_page_is_self_contained():
    """No external scripts/styles — must work on a phone with poor connectivity
    once loaded, and has no third-party dependencies."""
    body = client.get("/").text
    # the SVG xmlns in the inline favicon is an XML identifier, not a fetch
    stripped = body.replace("http://www.w3.org/2000/svg", "")
    assert "http://" not in stripped
    assert "https://" not in stripped
    assert "<script src" not in body
    assert '<link rel="stylesheet"' not in body
