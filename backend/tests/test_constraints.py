"""Cross-slot constraints (cycle 6): conditions that used to live only in prose.

The bug these guard against: a requirement like "one of the two principal
passes must be in Physics or Chemistry or Biology" was displayed to students
but never enforced, so the engine reported people eligible who were not.
"""

import pytest

from northstar.engine import evaluate_programme
from northstar.loader import DataError, KnowledgeBase, load_knowledge_base
from northstar.models import Constraint, Programme, Slot, StudentProfile


@pytest.fixture(scope="module")
def kb():
    return load_knowledge_base()


def prog(kb, code):
    return next(p for p in kb.programmes if p.code == code)


def _synthetic(constraints):
    """A programme requiring any 2 of {AdvMaths, Bio, Chem, Geo, Physics},
    mirroring ARU AR026, with the given constraints."""
    return Programme(
        id="test-prog", code="TEST001", name="Test", institution="Test U",
        location="", tags=frozenset({"science"}), requirement_text="",
        slots=(Slot(choose=2, subjects=frozenset(
            {"advanced_mathematics", "biology", "chemistry", "geography", "physics"}
        )),),
        min_points=4.0, points_basis="slots", additional_requirements=(),
        capacity=None, duration_years=None, checklist={}, source="",
        constraints=constraints,
    )


# --- must_include -----------------------------------------------------------

def test_must_include_rejects_assignment_without_a_required_subject(kb):
    p = _synthetic((Constraint("must_include", frozenset({"physics", "chemistry", "biology"})),))
    student = StudentProfile(grades={"advanced_mathematics": "B", "geography": "B"})
    r = evaluate_programme(kb, student, p)
    assert not r.eligible
    assert any(x.rule == "must_include" and not x.ok for x in r.reasons)


def test_must_include_accepts_a_student_who_has_one(kb):
    p = _synthetic((Constraint("must_include", frozenset({"physics", "chemistry", "biology"})),))
    student = StudentProfile(grades={"advanced_mathematics": "B", "chemistry": "B"})
    r = evaluate_programme(kb, student, p)
    assert r.eligible
    assert any(x.rule == "must_include" and x.ok for x in r.reasons)


def test_must_include_is_applied_during_search_not_after(kb):
    """The highest-points assignment may violate the constraint while a
    lower-scoring valid one exists — the student must still qualify."""
    p = _synthetic((Constraint("must_include", frozenset({"biology"})),))
    # AdvMaths A + Geography A scores highest but has no Biology;
    # Biology D + AdvMaths A is valid and must be found.
    student = StudentProfile(
        grades={"advanced_mathematics": "A", "geography": "A", "biology": "D"}
    )
    r = evaluate_programme(kb, student, p)
    assert r.eligible, "a valid lower-scoring assignment must not be missed"
    assert "biology" in r.matched_subjects


def test_ar026_regression_the_bug_ahmad_found(kb):
    """ARU AR026 requires one pass in Physics/Chemistry/Biology. A student with
    Advanced Mathematics + Geography satisfies the slots but not the rule."""
    p = prog(kb, "AR026")
    bad = StudentProfile(grades={"advanced_mathematics": "B", "geography": "B"})
    assert not evaluate_programme(kb, bad, p).eligible
    good = StudentProfile(grades={"advanced_mathematics": "B", "chemistry": "B"})
    assert evaluate_programme(kb, good, p).eligible


# --- subsidiary_from --------------------------------------------------------

def test_subsidiary_requirement_enforced_and_satisfiable(kb):
    p = _synthetic((Constraint("subsidiary_from", frozenset({"advanced_mathematics"})),))
    without = StudentProfile(grades={"biology": "B", "chemistry": "B"})
    r1 = evaluate_programme(kb, without, p)
    assert not r1.eligible
    assert any(x.rule == "subsidiary_requirement" and not x.ok for x in r1.reasons)
    # a subsidiary (S) pass is enough — it need not be a principal pass
    with_s = StudentProfile(
        grades={"biology": "B", "chemistry": "B", "advanced_mathematics": "S"}
    )
    assert evaluate_programme(kb, with_s, p).eligible


def test_holding_requirement_is_not_an_assignment_requirement(kb):
    """Regression (found by the reviewer pass): "must have a minimum of 'E' in
    either Chemistry or Geography" means the student must HOLD the subject —
    it need not be one of the passes counted toward the slots. Encoding it as
    must_include made the rule unsatisfiable whenever the subject was absent
    from the slot list, wrongly rejecting qualified students."""
    p = next(x for x in kb.programmes if x.code == "DM015")
    assert all(c.kind != "must_include" for c in p.constraints)
    student = StudentProfile(
        grades={"chemistry": "A", "advanced_mathematics": "A", "physics": "A"}
    )
    assert evaluate_programme(kb, student, p).eligible


def test_subsidiary_floor_is_enforced(kb):
    p = _synthetic((Constraint("subsidiary_from", frozenset({"geography"}), min_grade="C"),))
    weak = StudentProfile(grades={"physics": "A", "chemistry": "A", "geography": "E"})
    assert not evaluate_programme(kb, weak, p).eligible
    ok = StudentProfile(grades={"physics": "A", "chemistry": "A", "geography": "C"})
    assert evaluate_programme(kb, ok, p).eligible


# --- subsidiary_all (conjunctive) -------------------------------------------

def test_subsidiary_all_requires_every_subject(kb):
    p = _synthetic((Constraint("subsidiary_all", frozenset({"physics", "advanced_mathematics"})),))
    partial = StudentProfile(grades={"chemistry": "A", "biology": "A", "physics": "S"})
    r = evaluate_programme(kb, partial, p)
    assert not r.eligible, "holding only one of an AND-list must not qualify"
    assert any("missing" in x.detail.lower() for x in r.reasons if not x.ok)
    both = StudentProfile(
        grades={"chemistry": "A", "biology": "A", "physics": "S", "advanced_mathematics": "S"}
    )
    assert evaluate_programme(kb, both, p).eligible


# --- if_not_matched_subsidiary (conditional) ---------------------------------

def test_conditional_subsidiary_does_not_fire_when_trigger_is_used(kb):
    """'If one of the passes is NOT Adv Maths, you need a subsidiary in it' —
    a student who USES Adv Maths as a pass needs nothing extra."""
    p = _synthetic((
        Constraint("if_not_matched_subsidiary", frozenset({"basic_applied_mathematics"}),
                   trigger_subjects=frozenset({"advanced_mathematics"})),
    ))
    student = StudentProfile(grades={"advanced_mathematics": "B", "physics": "B"})
    r = evaluate_programme(kb, student, p)
    assert r.eligible
    assert any(x.rule == "conditional_subsidiary" and x.ok for x in r.reasons)


def test_conditional_subsidiary_fires_when_trigger_absent(kb):
    p = _synthetic((
        Constraint("if_not_matched_subsidiary", frozenset({"basic_applied_mathematics"}),
                   trigger_subjects=frozenset({"advanced_mathematics"})),
    ))
    without = StudentProfile(grades={"chemistry": "B", "physics": "B"})
    assert not evaluate_programme(kb, without, p).eligible
    with_bam = StudentProfile(
        grades={"chemistry": "B", "physics": "B", "basic_applied_mathematics": "S"}
    )
    assert evaluate_programme(kb, with_bam, p).eligible


def test_conditional_subsidiary_prefers_an_assignment_that_satisfies_it(kb):
    """Regression: the rule is evaluated DURING assignment search. A student
    holding the trigger subject must not be rejected just because the
    highest-scoring assignment happened to leave it out."""
    p = _synthetic((
        Constraint("if_not_matched_subsidiary", frozenset({"basic_applied_mathematics"}),
                   trigger_subjects=frozenset({"advanced_mathematics"})),
    ))
    # chemistry A + biology A scores highest but omits Adv Maths; the student
    # has no Basic Applied Maths, so the engine must pick an assignment
    # that uses Advanced Mathematics instead.
    student = StudentProfile(
        grades={"chemistry": "A", "biology": "A", "advanced_mathematics": "D"}
    )
    r = evaluate_programme(kb, student, p)
    assert r.eligible, "a valid assignment using the trigger subject must be found"
    assert "advanced_mathematics" in r.matched_subjects


def test_unencodable_conditions_stay_conditional_not_enforced(kb):
    """The 5 remaining prose conditions are unencodable for stated reasons
    (3 truncated by the PDF, 2 with O-level escape clauses). They must surface
    as `conditional`, never be silently enforced or silently dropped."""
    truncated_or_olevel = {"AR003", "AR026", "JC007", "DM041", "DM045"}
    present = {p.code for p in kb.programmes} & truncated_or_olevel
    assert present, "expected these programmes in the knowledge base"
    for code in present:
        p = next(x for x in kb.programmes if x.code == code)
        assert p.unverified_conditions, f"{code} must keep its condition visible"


# --- data integrity ---------------------------------------------------------

def test_constraints_validate_against_known_subjects(tmp_path, monkeypatch):
    from northstar import loader
    bad = {"kind": "must_include", "subjects": ["astrology"]}
    with pytest.raises(DataError, match="unknown subject"):
        loader._parse_constraint(bad, "p1", {"physics"})
    with pytest.raises(DataError, match="unknown constraint kind"):
        loader._parse_constraint({"kind": "vibes", "subjects": ["physics"]}, "p1", {"physics"})


def test_advisory_text_does_not_make_results_conditional(kb):
    """'Preference will be given to…' changes chances, not eligibility."""
    from northstar.loader import _unverified
    assert _unverified(("Preference to candidates with grade 'B' in Chemistry.",)) == ()
    assert _unverified(("Candidates with a 'C' grade in Chemistry given high priority",)) == ()
    kept = _unverified(("An applicant must have a credit in Mathematics at O-Level.",))
    assert len(kept) == 1
