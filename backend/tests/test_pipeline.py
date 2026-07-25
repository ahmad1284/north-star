"""Guidebook extraction pipeline (cycle 3): merged dataset integrity."""

import json
from pathlib import Path

import pytest

from northstar.engine import evaluate_all
from northstar.loader import DATA_DIR, load_knowledge_base
from northstar.models import StudentProfile
from northstar.ranking import rank_and_group


@pytest.fixture(scope="module")
def kb():
    return load_knowledge_base()


def test_extracted_dataset_present_and_substantial(kb):
    assert (DATA_DIR / "programmes_extracted.json").exists()
    assert len(kb.programmes) > 300, "extraction should multiply the knowledge base"
    institutions = {p.institution for p in kb.programmes}
    assert len(institutions) > 30


def test_curated_wins_on_code_conflict(kb):
    # SZ001 (SUZA MD) exists in both curated and raw extraction: exactly one
    # loaded, and it is the curated (human-verified) version.
    md = [p for p in kb.programmes if p.code == "SZ001"]
    assert len(md) == 1
    assert not md[0].machine_parsed
    assert md[0].id == "suza-doctor-of-medicine"


def test_provenance_flag_present_and_honest(kb):
    machine = [p for p in kb.programmes if p.machine_parsed]
    curated = [p for p in kb.programmes if not p.machine_parsed]
    assert len(machine) > 250
    assert len(curated) >= 30
    for p in machine:
        assert p.source, "every extracted entry keeps its guidebook page"


def test_review_file_is_honest_about_rejects():
    review = json.loads((DATA_DIR / "extraction_review.json").read_text())
    assert review["rows"], "review file must retain unparsed rows"
    for row in review["rows"][:20]:
        assert row["why"] and row["requirement_text" ] is not None


def test_engine_scales_to_full_dataset(kb):
    profile = StudentProfile(grades={"physics": "B", "chemistry": "A", "biology": "A"})
    out = rank_and_group(kb, profile, evaluate_all(kb, profile))
    assert out["counts"]["eligible"] > 50, "a strong PCB student sees a wide landscape"
    # grouping still disciplined: everything accounted for
    c = out["counts"]
    assert c["eligible"] == c["for_you"] + c["discoveries"] + c["other_eligible"]


def test_machine_parsed_surfaces_in_api_payload(kb):
    profile = StudentProfile(grades={"physics": "B", "chemistry": "A", "biology": "A"})
    out = rank_and_group(kb, profile, evaluate_all(kb, profile))
    flags = {r["programme"]["machine_parsed"] for g in out["groups"].values() for r in g}
    assert flags == {True, False}, "clients can distinguish verified vs machine-parsed data"
