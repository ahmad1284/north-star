import pytest

from northstar.engine import evaluate_all, evaluate_programme, validate_profile
from northstar.loader import load_knowledge_base
from northstar.models import StudentProfile


@pytest.fixture(scope="module")
def kb():
    return load_knowledge_base()


def prog(kb, pid):
    return next(p for p in kb.programmes if p.id == pid)


def test_strong_pcb_student_eligible_for_md(kb):
    student = StudentProfile(grades={"physics": "B", "chemistry": "A", "biology": "A"})
    r = evaluate_programme(kb, student, prog(kb, "suza-doctor-of-medicine"))
    assert r.eligible
    assert r.strength > 0.9
    assert any(x.rule == "minimum_points" and x.ok for x in r.reasons)


def test_md_grade_floor_blocks_e_in_physics(kb):
    # E in Physics fails the 'minimum D in each' floor even with great points
    student = StudentProfile(grades={"physics": "E", "chemistry": "A", "biology": "A"})
    r = evaluate_programme(kb, student, prog(kb, "suza-doctor-of-medicine"))
    assert not r.eligible


def test_md_points_threshold(kb):
    # D,D,E = 5 points < 6 -> ineligible on points even though floors D,D met? E fails floor anyway.
    # Use D,D,D = 6 points -> eligible boundary.
    student = StudentProfile(grades={"physics": "D", "chemistry": "D", "biology": "D"})
    r = evaluate_programme(kb, student, prog(kb, "suza-doctor-of-medicine"))
    assert r.eligible
    assert r.strength == pytest.approx(6.0 / 15.0)


def test_weak_pcb_fails_md_but_gets_science_education(kb):
    student = StudentProfile(grades={"physics": "E", "chemistry": "D", "biology": "D"})
    md = evaluate_programme(kb, student, prog(kb, "suza-doctor-of-medicine"))
    assert not md.eligible
    bed = evaluate_programme(kb, student, prog(kb, "suza-bsc-with-education"))
    assert bed.eligible  # best two: D+D = 4.0 points


def test_subsidiary_pass_is_not_principal(kb):
    student = StudentProfile(grades={"physics": "S", "chemistry": "A", "biology": "A"})
    r = evaluate_programme(kb, student, prog(kb, "suza-doctor-of-medicine"))
    assert not r.eligible


def test_one_subject_cannot_fill_two_slots(kb):
    # SUZA CS needs Adv Maths/CS PLUS a second subject from another set
    student = StudentProfile(grades={"advanced_mathematics": "A"})
    r = evaluate_programme(kb, student, prog(kb, "suza-bsc-computer-science"))
    assert not r.eligible


def test_pcm_student_gets_engineering(kb):
    student = StudentProfile(
        grades={"physics": "B", "chemistry": "C", "advanced_mathematics": "B"}
    )
    r = evaluate_programme(kb, student, prog(kb, "udsm-bsc-mining-engineering"))
    assert r.eligible
    assert r.matched_subjects and set(r.matched_subjects) == {"advanced_mathematics", "physics"}


def test_best_three_basis_udsm_economics(kb):
    # EGM with E,E,E: subjects OK (economics + any) but best-three = 3.0 < 5.0
    weak = StudentProfile(grades={"economics": "E", "geography": "E", "advanced_mathematics": "E"})
    r = evaluate_programme(kb, weak, prog(kb, "udsm-ba-economics"))
    assert not r.eligible
    ok = StudentProfile(grades={"economics": "C", "geography": "D", "advanced_mathematics": "D"})
    r2 = evaluate_programme(kb, ok, prog(kb, "udsm-ba-economics"))
    assert r2.eligible  # 3+2+2 = 7 >= 5


def test_any_slot_accepts_any_principal(kb):
    student = StudentProfile(grades={"economics": "B", "divinity": "C"})
    r = evaluate_programme(kb, student, prog(kb, "udsm-ba-economics"))
    assert r.eligible


def test_additional_requirements_surface_in_reasons(kb):
    student = StudentProfile(
        grades={"physics": "B", "chemistry": "B", "advanced_mathematics": "B"}
    )
    r = evaluate_programme(kb, student, prog(kb, "udsm-bsc-mining-engineering"))
    assert r.eligible
    assert any(x.rule == "additional_requirements" for x in r.reasons)


def test_evaluate_all_covers_every_programme(kb):
    student = StudentProfile(grades={"physics": "A", "chemistry": "A", "biology": "A"})
    results = evaluate_all(kb, student)
    assert len(results) == len(kb.programmes)


def test_validate_profile_rejects_unknowns(kb):
    assert validate_profile(kb, {}) == ["no subjects given"]
    problems = validate_profile(kb, {"alchemy": "A", "physics": "Z"})
    assert any("alchemy" in p for p in problems)
    assert any("'Z'" in p for p in problems)
    assert validate_profile(kb, {"physics": "A"}) == []
