import pytest
from fastapi.testclient import TestClient

from northstar.api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_reference_endpoints():
    assert client.get("/subjects").status_code == 200
    combos = client.get("/combinations").json()["combinations"]
    assert any(c["code"] == "PCB" for c in combos)
    progs = client.get("/programmes").json()["programmes"]
    assert len(progs) >= 20


def test_match_happy_path():
    r = client.post("/match", json={"grades": {"physics": "B", "chemistry": "A", "biology": "A"}})
    assert r.status_code == 200
    body = r.json()
    assert set(body["groups"]) == {"for_you", "discoveries", "other_eligible"}
    assert body["counts"]["eligible"] > 0
    top = body["groups"]["for_you"][0]
    assert top["eligible"] and top["reasons"]


def test_match_rejects_unknown_subject():
    r = client.post("/match", json={"grades": {"alchemy": "A"}})
    assert r.status_code == 422
    assert any("alchemy" in d for d in r.json()["detail"])


def test_match_rejects_bad_grade():
    r = client.post("/match", json={"grades": {"physics": "Q"}})
    assert r.status_code == 422
