"""The bundled web client (lives in web/, served by the API as a convenience)."""

import re
from pathlib import Path

import pytest
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


GUIDANCE_PAGES = {
    "/barua": "Ahmad Sadri",          # the letter, attributed
    "/maswali": "Maswali ya kuuliza",  # the questions to carry
    "/dunia-ya-kazi": "Mawazo",        # the four work-interest areas
}


@pytest.mark.parametrize("path,marker", GUIDANCE_PAGES.items())
def test_guidance_pages_are_served(path, marker):
    """What the engine can't answer, these pages hand back to the student."""
    r = client.get(path)
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert marker in r.text


@pytest.mark.parametrize("path", list(GUIDANCE_PAGES) + ["/"])
def test_every_page_links_back_into_the_tool(path):
    """A student must never reach a dead end."""
    body = client.get(path).text
    assert 'href="./"' in body or 'href="maswali"' in body


@pytest.mark.parametrize("path", GUIDANCE_PAGES)
def test_guidance_pages_load_no_external_resources(path):
    """Same rule as the client: everything inline, so the pages work on a poor
    connection. A hyperlink to a cited source is fine — a *fetched* resource
    (script, stylesheet, font, image) is not."""
    body = client.get(path).text
    assert "<script" not in body, "guidance pages need no JavaScript at all"
    assert '<link rel="stylesheet"' not in body
    assert "url(http" not in body  # no remote CSS assets
    assert "<img" not in body


def test_unknown_facts_prompt_the_student_instead_of_showing_a_dash():
    """The heart of this cycle: cost/salary are unknown for almost every
    programme, and that gap is the letter's own call to action — not a
    rendering failure."""
    body = client.get("/").text
    assert "hatujui" in body, "an unknown fact must say so, and say what to do"
    assert 'href="maswali"' in body


def test_no_path_traversal_via_the_new_routes():
    """The guidance routes are explicitly named, not a static mount — the
    security review verified traversal is impossible and it must stay that way."""
    for attack in ("/barua/../../etc/passwd", "/maswali/%2e%2e/%2e%2e/etc/passwd",
                   "/dunia-ya-kazi/../api.py", "/../backend/northstar/api.py"):
        assert client.get(attack).status_code in (307, 404), attack


def test_api_is_usable_without_a_client(monkeypatch, tmp_path):
    """The API is the product; the client is optional. Missing client must not
    break the API, and must say where it looked."""
    monkeypatch.setattr("northstar.api._WEB_DIR", tmp_path)
    r = client.get("/")
    assert r.status_code == 404
    detail = r.json()["detail"]
    assert "/docs" in detail, "should point the visitor at the API instead"
    # Security: the response must not hand a stranger the filesystem layout or
    # internal env-var names — those go to the operator's log, not the client.
    assert str(tmp_path) not in detail
    assert "NORTH_STAR_WEB_DIR" not in detail
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
