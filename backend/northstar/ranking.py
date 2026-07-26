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
    kb: KnowledgeBase,
    profile: StudentProfile,
    results: list[ProgrammeResult],
    interests: list[str] | None = None,
) -> dict:
    """Group and rank results. `interests` (optional) = ACT World of Work area
    ids the student says they're drawn to (ideas/people/data/things). When
    given, aligned results are annotated and a `bridge` group is added:
    interest-matched programmes the student is NOT eligible for, with the
    engine's reasons spelling out what it would take. Without interests, the
    output is exactly the cycle-1 shape (fully backward compatible)."""
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

    out = {
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

    if interests:
        wanted = frozenset(interests)
        # Annotate eligible results that align with the stated interests.
        for group in out["groups"].values():
            for d in group:
                areas = kb.programme_areas(frozenset(d["programme"]["tags"]))
                matched = sorted(areas & wanted)
                if matched:
                    d["interest_match"] = matched
        # The Bridge: what the student WANTS but cannot (yet) enter — with the
        # engine's reasons saying exactly what is missing. Honest, not hidden.
        bridge = [
            r for r in ineligible
            if kb.programme_areas(r.programme.tags) & wanted
        ]
        bridge.sort(key=lambda r: (
            -len(kb.programme_areas(r.programme.tags) & wanted),
            r.programme.name,
        ))
        out["groups"]["bridge"] = [
            {**r.to_dict(), "interest_match": sorted(
                kb.programme_areas(r.programme.tags) & wanted)}
            for r in bridge
        ]
        out["counts"]["bridge"] = len(bridge)
        out["interests"] = sorted(wanted)

    return out
