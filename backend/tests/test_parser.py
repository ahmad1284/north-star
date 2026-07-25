"""Tests for the guidebook requirement parser.

Why this file exists: `scripts/extract_guidebook.py` decides what 332
programmes' admission rules *mean*, and until cycle 7's review it had no tests
at all. Mutation testing showed every parser mutation surviving the suite —
`protect_names` reduced to a no-op, the and/or branch inverted, the
multi-clause floor path disabled — because CI validates the committed JSON's
*shape* but never re-runs extraction. A parser regression would only surface
the next time someone regenerated the data, silently changing who qualifies.

The module imports standalone; no PDF is needed for these.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import extract_guidebook as ex  # noqa: E402


# --- subject lists -----------------------------------------------------------

def test_and_inside_a_subject_name_is_not_a_conjunction():
    """'Science and Practice of Agriculture' is ONE subject. Splitting it
    would both lose the subject and make a choice-list look conjunctive —
    silently stricter than the guidebook."""
    assert ex.parse_subject_list(
        "Science and Practice of Agriculture or Chemistry"
    ) == ["agriculture", "chemistry"]
    assert ex.list_semantics("Science and Practice of Agriculture or Chemistry") == "choice"


def test_and_versus_or_decides_all_versus_choice():
    """The difference between needing one subject and needing two."""
    assert ex.list_semantics("Physics and Mathematics") == "all"
    assert ex.list_semantics("Physics or Mathematics") == "choice"


def test_an_explicit_choice_marker_beats_the_separator():
    """'one of the following: A, B and C' is a CHOICE despite the 'and' —
    reading it as conjunctive hides real options from a student."""
    assert ex.list_semantics("one of the following subjects: Geography, Physics and Advanced Mathematics") == "choice"
    assert ex.list_semantics("either Chemistry and Biology") == "choice"


def test_unknown_subject_rejects_the_whole_list():
    """Honesty contract: parse cleanly or quarantine. A partially-understood
    list must not become a rule."""
    assert ex.parse_subject_list("Physics or Underwater Basket Weaving") is None


def test_olevel_subjects_poison_a_principal_pass_list():
    assert ex.parse_subject_list("Physics or Basic Mathematics") is None


# --- constraint extraction ---------------------------------------------------

def test_conjunctive_subsidiary_becomes_subsidiary_all():
    got, rest = ex.extract_constraints(
        ["In addition, an applicant must have at least a subsidiary pass in "
         "Physics and Mathematics at A-Level."]
    )
    assert len(got) == 1 and not rest
    assert got[0]["kind"] == "subsidiary_all"
    assert set(got[0]["subjects"]) == {"physics", "advanced_mathematics"}


def test_choice_subsidiary_becomes_subsidiary_from():
    got, _ = ex.extract_constraints(
        ["In addition, the applicant must have at least a subsidiary pass in "
         "one of the following subjects: Geography, Physics or Advanced Mathematics."]
    )
    assert len(got) == 1
    assert got[0]["kind"] == "subsidiary_from"


def test_multi_clause_floors_split_per_grade():
    """The highest-risk-per-line regex in the extractor, governing only three
    programmes — nothing else would notice it breaking."""
    got, rest = ex.extract_constraints(
        ['A minimum of "C" grade in Chemistry and "D" grade in Biology '
         'and at least E grade in Physics.']
    )
    assert not rest
    assert [(c["min_grade"], c["subjects"]) for c in got] == [
        ("C", ["chemistry"]), ("D", ["biology"]), ("E", ["physics"]),
    ]


def test_zu024_shape_conjunctive_floor_is_all_not_choice():
    """The live false positive found by the cycle-7 correctness review: a
    clause naming two subjects with 'and' requires BOTH."""
    got, _ = ex.extract_constraints(
        ["A minimum of D grades in Chemistry and Biology and at least E grade "
         "in Physics, Advanced Mathematics, Nutrition, Geography or Agriculture."]
    )
    kinds = {c["kind"] for c in got}
    both = next(c for c in got if set(c["subjects"]) == {"chemistry", "biology"})
    assert both["kind"] == "subsidiary_all", "D in Chemistry AND Biology means both"
    assert both["min_grade"] == "D"
    assert "subsidiary_from" in kinds, "the third clause is a choice"


def test_conditional_rule_captures_trigger_and_requirement():
    got, _ = ex.extract_constraints(
        ["If one of the principal passes is not in Advanced Mathematics, an "
         "applicant must have a subsidiary pass in Basic Applied Mathematics."]
    )
    assert len(got) == 1
    c = got[0]
    assert c["kind"] == "if_not_matched_subsidiary"
    assert c["trigger_subjects"] == ["advanced_mathematics"]
    assert c["subjects"] == ["basic_applied_mathematics"]


@pytest.mark.parametrize("sentence", [
    # O-level alternatives are only half-checkable: we never see O-level
    # results, so enforcing the A-level half alone rejects qualified students.
    'If one of the principal passes do not include Advanced Mathematics an '
    'applicant must have a subsidiary pass in Advanced Mathematics at A-Level, '
    'or a minimum of "D" grade in Mathematics at O-Level.',
    "If one of the principal passes is not in Advanced Mathematics, an applicant "
    "must have at least a subsidiary pass in Advanced Mathematics or Basic "
    "Applied Mathematics or D in ordinary level Mathematics.",
])
def test_olevel_escape_clauses_are_never_encoded(sentence):
    got, rest = ex.extract_constraints([sentence])
    assert got == [], "half a rule is worse than none — must stay prose"
    assert rest == [sentence]


def test_advisory_language_is_never_encoded_as_a_rule():
    """'Preference will be given to…' changes chances, not eligibility."""
    got, rest = ex.extract_constraints(
        ["Preference will be given to candidates with a subsidiary pass in Physics."]
    )
    assert got == [] and len(rest) == 1


# --- points / grade scale ----------------------------------------------------

def test_points_cell_detects_best_three_basis():
    assert ex.parse_points_cell("5 from 3 subjects") == (5.0, "best_three")
    assert ex.parse_points_cell("4.0") == (4.0, "slots")


def test_level_reference_normalisation():
    """The PDF renders these inconsistently; patterns depend on the canonical
    form. Only the UPPERCASE letter is normalised — matching case-insensitively
    would rewrite the ordinary English article ('achieve a level of skill')."""
    for raw in ("O - Level", "O'level", "O-LEVEL", "A- level"):
        out = ex.norm(f"a pass at {raw} in Mathematics")
        assert "-Level" in out, out
    # the article must survive untouched
    assert ex.norm("achieve a level of proficiency") == "achieve a level of proficiency"


def test_lowercase_level_references_are_still_caught_by_the_guards():
    """norm() leaves lowercase alone, so the safety nets must be
    case-insensitive — otherwise a lowercase 'o level' sentence would slip
    through and be half-encoded."""
    assert ex.OLEVEL_ESCAPE_RE.search("or a D in ordinary level Mathematics")
    assert ex.OLEVEL_ESCAPE_RE.search("or a pass at o level")
    assert ex.parse_subject_list("Physics or basic mathematics") is None
    # and it must not fire on unrelated words containing "level"
    assert not ex.OLEVEL_ESCAPE_RE.search("progress to Level 5")
