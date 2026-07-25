"""Cross-slot constraints (cycle 6): conditions that used to live only in prose.

The bug these guard against: a requirement like "one of the two principal
passes must be in Physics or Chemistry or Biology" was displayed to students
but never enforced, so the engine reported people eligible who were not.
"""

import re

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
    """The remaining prose conditions are unencodable for stated reasons
    (truncated by the PDF, or carrying an O-level escape clause). They must
    surface as `conditional`, and must NEVER be silently turned into an
    enforced rule — that would reject students who satisfy the real thing."""
    codes = {"AR003", "AR026", "JC007", "DM041", "DM045"}
    present = {p.code for p in kb.programmes} & codes
    assert present == codes, f"missing from knowledge base: {codes - present}"
    for code in codes:
        p = next(x for x in kb.programmes if x.code == code)
        assert p.unverified_conditions, f"{code} must keep its condition visible"
        encoded_from = {c.source_text for c in p.constraints}
        for cond in p.unverified_conditions:
            assert cond not in encoded_from, (
                f"{code}: an unencodable condition was turned into a hard rule"
            )


def test_no_constraint_is_encoded_from_an_olevel_sentence(kb):
    """Invariant, independent of which regex enforces it: a sentence offering
    an O-level alternative is only half-checkable, so it must never become an
    enforced constraint."""
    olevel = re.compile(r"\bo-level|\bordinary\s+level|\bo\s*'?\s*level", re.IGNORECASE)
    offenders = [
        (p.code, c.source_text)
        for p in kb.programmes
        for c in p.constraints
        if c.source_text and olevel.search(c.source_text)
    ]
    assert not offenders, f"constraints encoded from O-level sentences: {offenders}"


# --- real-data anchors -------------------------------------------------------
# Mutation testing showed the synthetic tests above pass even when every
# subsidiary_all / if_not_matched constraint is stripped from the real
# knowledge base. These tie the engine to actual guidebook rules.

def test_zu024_regression_conjunctive_floor_is_not_a_choice(kb):
    """Found by the cycle-7 correctness review: 'A minimum of D grades in
    Chemistry and Biology' was parsed as a CHOICE, so a student with Biology
    at E was told they qualified. Both subjects are required."""
    p = prog(kb, "ZU024")
    assert any(c.kind == "subsidiary_all" for c in p.constraints)
    for bad in ({"chemistry": "C", "biology": "E", "physics": "C"},
                {"chemistry": "E", "biology": "C", "physics": "C"}):
        assert not evaluate_programme(kb, StudentProfile(grades=bad), p).eligible
    ok = {"chemistry": "D", "biology": "D", "physics": "E"}
    assert evaluate_programme(kb, StudentProfile(grades=ok), p).eligible


def test_ar031_requires_both_physics_and_maths(kb):
    """Real subsidiary_all: 'a subsidiary pass in Physics and Mathematics'."""
    p = prog(kb, "AR031")
    assert any(c.kind == "subsidiary_all" for c in p.constraints)
    only_one = StudentProfile(grades={"advanced_mathematics": "B", "geography": "B"})
    assert not evaluate_programme(kb, only_one, p).eligible
    both = StudentProfile(
        grades={"advanced_mathematics": "B", "physics": "B", "geography": "B"}
    )
    assert evaluate_programme(kb, both, p).eligible


def test_dm006_accepts_economics_as_a_trigger(kb):
    """DM006 is the only real programme with MULTIPLE trigger subjects
    ({advanced_mathematics, economics}) — a truncated trigger list would go
    unnoticed without this."""
    p = prog(kb, "DM006")
    cond = next(c for c in p.constraints if c.kind == "if_not_matched_subsidiary")
    assert cond.trigger_subjects == frozenset({"advanced_mathematics", "economics"})
    # qualifies via the economics trigger, holding no maths at all
    student = StudentProfile(grades={"economics": "C", "commerce": "D", "accountancy": "C"})
    assert evaluate_programme(kb, student, p).eligible


# --- data integrity ---------------------------------------------------------

def test_a_failed_subject_is_not_a_subsidiary_pass(kb):
    """`_holds` treats anything but F as a pass; mutation testing showed
    nothing caught F being accepted, because existing tests used ABSENT
    subjects rather than failed ones."""
    for kind in ("subsidiary_from", "subsidiary_all"):
        p = _synthetic((Constraint(kind, frozenset({"geography"})),))
        failed = StudentProfile(grades={"physics": "A", "chemistry": "A", "geography": "F"})
        assert not evaluate_programme(kb, failed, p).eligible, kind
        passed = StudentProfile(grades={"physics": "A", "chemistry": "A", "geography": "S"})
        assert evaluate_programme(kb, passed, p).eligible, kind


def test_grade_floors_are_enforced_on_the_new_constraint_kinds(kb):
    """`min_grade` was dead-untested on both new kinds."""
    all_kind = _synthetic((
        Constraint("subsidiary_all", frozenset({"geography"}), min_grade="C"),
    ))
    weak = StudentProfile(grades={"physics": "A", "chemistry": "A", "geography": "E"})
    assert not evaluate_programme(kb, weak, all_kind).eligible
    ok = StudentProfile(grades={"physics": "A", "chemistry": "A", "geography": "C"})
    assert evaluate_programme(kb, ok, all_kind).eligible

    cond_kind = _synthetic((
        Constraint("if_not_matched_subsidiary", frozenset({"geography"}),
                   min_grade="C", trigger_subjects=frozenset({"biology"})),
    ))
    weak2 = StudentProfile(grades={"physics": "A", "chemistry": "A", "geography": "E"})
    assert not evaluate_programme(kb, weak2, cond_kind).eligible
    ok2 = StudentProfile(grades={"physics": "A", "chemistry": "A", "geography": "C"})
    assert evaluate_programme(kb, ok2, cond_kind).eligible


def test_conditional_reason_text_matches_which_branch_fired(kb):
    """README principle 2 is 'always explain' — the explanation IS the product,
    so the wrong branch of the message is a real defect."""
    p = _synthetic((
        Constraint("if_not_matched_subsidiary", frozenset({"geography"}),
                   trigger_subjects=frozenset({"physics"}), source_text="x"),
    ))
    used = StudentProfile(grades={"physics": "B", "chemistry": "B"})
    detail = next(x.detail for x in evaluate_programme(kb, used, p).reasons
                  if x.rule == "conditional_subsidiary")
    assert "does not apply" in detail

    not_used = StudentProfile(grades={"chemistry": "B", "biology": "B", "geography": "S"})
    detail2 = next(x.detail for x in evaluate_programme(kb, not_used, p).reasons
                   if x.rule == "conditional_subsidiary")
    assert "does not apply" not in detail2


def test_result_is_independent_of_grade_entry_order(kb):
    """Ties in the assignment search must not depend on the order a client
    happened to send the subjects, or the same student sees different
    explanations on different devices."""
    p = prog(kb, "ZU024")
    a = StudentProfile(grades={"chemistry": "B", "biology": "B", "physics": "B"})
    b = StudentProfile(grades={"physics": "B", "biology": "B", "chemistry": "B"})
    ra, rb = evaluate_programme(kb, a, p), evaluate_programme(kb, b, p)
    assert ra.eligible == rb.eligible
    assert ra.matched_subjects == rb.matched_subjects


def test_loader_rejects_conditional_without_trigger_subjects():
    from northstar import loader
    with pytest.raises(DataError, match="trigger_subjects"):
        loader._parse_constraint(
            {"kind": "if_not_matched_subsidiary", "subjects": ["physics"]},
            "p1", {"physics"},
        )


def test_loader_rejects_unknown_trigger_subject():
    from northstar import loader
    with pytest.raises(DataError, match="unknown subject"):
        loader._parse_constraint(
            {"kind": "if_not_matched_subsidiary", "subjects": ["physics"],
             "trigger_subjects": ["astrology"]},
            "p1", {"physics"},
        )


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
