"""Ranking & output shaping: turn raw engine results into the grouped,
ranked structure clients render ("rich, but in style").

Groups
------
- for_you:        eligible + strong fit, in areas a student with this
                  combination is typically steered toward (obvious tags).
- discoveries:    eligible + strong fit, OUTSIDE the obvious tags — programmes
                  the student's strengths open up that they likely never
                  considered. The serendipity channel.
- other_eligible: everything else the student qualifies for. Nothing is
                  hidden; it's organized, not truncated.

Tunables live in one place below so the heuristic is easy to adjust.
"""

from __future__ import annotations

from .loader import KnowledgeBase
from .models import ProgrammeResult, StudentProfile

# ---- tunables (single source of truth) -------------------------------------
DISCOVERY_MIN_STRENGTH = 0.6   # how strong a fit must be to count as a discovery
FOR_YOU_MIN_STRENGTH = 0.35    # floor below which an obvious-area match is just "other"
# ----------------------------------------------------------------------------


def _obvious_tags(kb: KnowledgeBase, profile: StudentProfile) -> frozenset[str]:
    """Obvious programme areas for the student's subjects: union of the
    obvious_tags of every known combination whose subjects the student holds."""
    student_subjects = set(profile.grades)
    tags: set[str] = set()
    for combo in kb.combinations.values():
        if set(combo.subjects) <= student_subjects:
            tags |= combo.obvious_tags
    return frozenset(tags)


def rank_and_group(
    kb: KnowledgeBase, profile: StudentProfile, results: list[ProgrammeResult]
) -> dict:
    obvious = _obvious_tags(kb, profile)
    eligible = [r for r in results if r.eligible]
    ineligible = [r for r in results if not r.eligible]

    for_you: list[ProgrammeResult] = []
    discoveries: list[ProgrammeResult] = []
    other: list[ProgrammeResult] = []

    for r in eligible:
        in_obvious_area = bool(r.programme.tags & obvious)
        if in_obvious_area and r.strength >= FOR_YOU_MIN_STRENGTH:
            for_you.append(r)
        elif not in_obvious_area and r.strength >= DISCOVERY_MIN_STRENGTH:
            discoveries.append(r)
        else:
            other.append(r)

    # Rank by the admission points the student brings to each programme's
    # defining subjects — TCU's own currency, not an invented weighting. This
    # rewards programmes that use MORE of the student's strengths (14 points
    # into Medicine outranks 10 points into a two-subject programme).
    # Strength breaks ties; programme name keeps ordering deterministic.
    key = lambda r: (-r.matched_points, -r.strength, r.programme.name)
    for group in (for_you, discoveries, other):
        group.sort(key=key)

    return {
        "obvious_areas": sorted(obvious),
        "groups": {
            "for_you": [r.to_dict() for r in for_you],
            "discoveries": [r.to_dict() for r in discoveries],
            "other_eligible": [r.to_dict() for r in other],
        },
        "counts": {
            "eligible": len(eligible),
            "for_you": len(for_you),
            "discoveries": len(discoveries),
            "other_eligible": len(other),
            "not_eligible": len(ineligible),
        },
    }
