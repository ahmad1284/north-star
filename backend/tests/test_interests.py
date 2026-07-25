"""Interests layer (cycle 2): ACT World of Work areas + the Bridge."""

import pytest
from fastapi.testclient import TestClient

from northstar.api import app
from northstar.engine import evaluate_all
from northstar.loader import load_knowledge_base
from northstar.models import StudentProfile
from northstar.ranking import rank_and_group

client = TestClient(app)


@pytest.fixture(scope="module")
def kb():
    return load_knowledge_base()


def run(kb, grades, interests=None):
    profile = StudentProfile(grades=grades)
    return rank_and_group(kb, profile, evaluate_all(kb, profile), interests=interests)


def test_every_programme_has_an_interest_area(kb):
    for p in kb.programmes:
        assert kb.programme_areas(p.tags), p.id


def test_no_interests_means_cycle1_output_shape(kb):
    out = run(kb, {"chemistry": "A", "biology": "A", "physics": "B"})
    assert set(out["groups"]) == {"for_you", "discoveries", "other_eligible"}
    assert "bridge" not in out["groups"]
    assert "interests" not in out


def test_hamisi_arts_student_bridging_toward_things(kb):
    """HKL student drawn to Things (machines, building): the bridge must show
    engineering/technical programmes he is NOT eligible for, with reasons —
    interests beyond what he studied, honestly explained."""
    out = run(
        kb,
        {"history": "B", "kiswahili": "A", "literature_in_english": "C"},
        interests=["things"],
    )
    bridge = out["groups"]["bridge"]
    assert bridge, "interests outside the combination must open a bridge"
    bridge_ids = [r["programme"]["id"] for r in bridge]
    assert "udsm-bsc-mining-engineering" in bridge_ids
    entry = next(r for r in bridge if r["programme"]["id"] == "udsm-bsc-mining-engineering")
    assert not entry["eligible"]
    assert entry["reasons"], "the bridge must say what it would take"
    assert "things" in entry["interest_match"]


def test_eligible_results_get_interest_annotations(kb):
    out = run(
        kb,
        {"chemistry": "A", "biology": "A", "physics": "B"},
        interests=["people"],
    )
    md = next(
        r for r in out["groups"]["for_you"]
        if r["programme"]["id"] == "suza-doctor-of-medicine"
    )
    assert "people" in md["interest_match"]  # medicine = working with People


def test_api_match_with_interests_and_validation():
    r = client.post(
        "/match",
        json={
            "grades": {"history": "B", "kiswahili": "A", "literature_in_english": "C"},
            "interests": ["things"],
        },
    )
    assert r.status_code == 200
    assert r.json()["groups"]["bridge"]
    bad = client.post(
        "/match", json={"grades": {"history": "B"}, "interests": ["vibes"]}
    )
    assert bad.status_code == 422
    assert any("vibes" in d for d in bad.json()["detail"])


def test_api_interests_reference_endpoint():
    r = client.get("/interests")
    assert r.status_code == 200
    ids = {a["id"] for a in r.json()["areas"]}
    assert ids == {"ideas", "people", "data", "things"}
