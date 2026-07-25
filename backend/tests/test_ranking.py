import pytest

from northstar.engine import evaluate_all
from northstar.loader import load_knowledge_base
from northstar.models import StudentProfile
from northstar.ranking import rank_and_group


@pytest.fixture(scope="module")
def kb():
    return load_knowledge_base()


def grouped(kb, grades):
    profile = StudentProfile(grades=grades)
    return rank_and_group(kb, profile, evaluate_all(kb, profile))


def ids(group):
    return [r["programme"]["id"] for r in group]


def test_strong_pcb_student_for_you_and_discoveries(kb):
    out = grouped(kb, {"physics": "B", "chemistry": "A", "biology": "A"})
    for_you = ids(out["groups"]["for_you"])
    discoveries = ids(out["groups"]["discoveries"])
    # Health programmes land in "for you" (obvious area for PCB)
    assert "suza-doctor-of-medicine" in for_you
    # A strong-fit programme OUTSIDE health/science lands in discoveries
    assert "aru-bsc-interior-design" in discoveries
    # Nothing eligible is hidden
    counts = out["counts"]
    assert counts["eligible"] == counts["for_you"] + counts["discoveries"] + counts["other_eligible"]


def test_groups_ranked_by_strength(kb):
    out = grouped(kb, {"physics": "C", "chemistry": "A", "biology": "B"})
    for group in out["groups"].values():
        strengths = [r["strength"] for r in group]
        assert strengths == sorted(strengths, reverse=True)


def test_obvious_areas_reflect_combination(kb):
    out = grouped(kb, {"history": "B", "geography": "C", "kiswahili": "B"})
    assert "arts" in out["obvious_areas"]
    # Arts student: education/arts programmes are for_you, not discoveries
    assert "suza-ba-with-education" in ids(out["groups"]["for_you"])


def test_results_carry_reasons_through(kb):
    out = grouped(kb, {"physics": "B", "chemistry": "A", "biology": "A"})
    top = out["groups"]["for_you"][0]
    assert top["reasons"], "explainability must survive to the output"
    assert top["programme"]["checklist"] is not None
