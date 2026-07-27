"""Tests for the TCU accreditation-register cross-check helpers.

Only the pure join logic is tested here — harvesting hits tcu.go.tz and has no
business in a unit suite.

Both cases below are bugs this script actually shipped with, and both are the same
brittleness class the guidebook extractor died of: a matcher that fails quietly and
files the result under a reassuring label. An institution that cannot be joined is
reported as "cannot be verified from this source", which reads as *fine* — so a
matching bug here doesn't look like a bug, it looks like a limitation.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from crosscheck_tcu_register import acronym, squash  # noqa: E402


def test_acronym_tolerates_a_leading_space_inside_parentheses():
    """The PDF's text layer renders "University of Dodoma ( UDOM), Dodoma".
    A regex anchored on "(" + letter misses it and drops UDOM into "unverifiable"."""
    assert acronym("University of Dodoma ( UDOM), Dodoma") == "UDOM"
    assert acronym("University of Dodoma (UDOM), Dodoma") == "UDOM"


def test_acronym_falls_back_when_none_is_printed():
    """"KCMC University, Kilimanjaro" prints no acronym at all. Returning "" would
    file a real, checkable university under "cannot be checked"."""
    assert acronym("KCMC University, Kilimanjaro") == "KCMC"


def test_acronym_fallback_skips_generic_words():
    assert acronym("Institute of Social Work, Dar es Salaam") == "SOCIALWORK"


def test_acronym_is_case_and_punctuation_stable():
    assert acronym("Mzumbe University (MU), Morogoro") == "MU"
    assert acronym("Some Body (M.U.), Town") == "MU"


def test_squash_ignores_degree_wording():
    """"Bachelor of Science in Nursing" and "BSc Nursing" are the same programme
    named two ways; the join must not treat that as a discrepancy."""
    assert squash("Bachelor of Science in Nursing") == squash("BSc Nursing")


def test_squash_is_order_independent_but_content_sensitive():
    assert squash("Bachelor of Arts in Literature and Language") == \
           squash("Bachelor of Language and Literature Arts")
    assert squash("Bachelor of Science in Nursing") != \
           squash("Bachelor of Science in Midwifery")


@pytest.mark.parametrize("name", ["", "Bachelor of", "of in and the"])
def test_squash_handles_degenerate_titles(name):
    """Must not raise; an empty key simply never matches."""
    assert isinstance(squash(name), str)
