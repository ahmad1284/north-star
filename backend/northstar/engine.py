"""The eligibility + strength-scoring engine (the "expert system" core).

Pure and deterministic: KnowledgeBase in, explained results out. No I/O here.

How a programme is evaluated
----------------------------
A programme's requirement is a set of *slots* (e.g. MD: Chemistry>=D, Biology>=D,
Physics>=D; SUZA CS: one of {Adv Maths, CS} + one of {Geo, Econ, ..., Bio}).
Each slot position must be filled by a DISTINCT student subject that is a
principal pass (E or above) meeting the slot's grade floor. We search all
assignments and keep the one with the highest total points — i.e. we always
read the rules in the student's favour. Total points (over the slot subjects,
or the student's best three, per `points_basis`) must reach `min_points`.

Strength score
--------------
strength = (points achieved in the subjects that satisfied the requirement)
           / (maximum possible points for that many subjects, 5.0 each)
A student with A,A in the two defining subjects scores 1.0; with E,E scores 0.2.
Deterministic, explainable, and comparable across programmes.
"""

from __future__ import annotations

from itertools import permutations

from .loader import KnowledgeBase
from .models import Programme, ProgrammeResult, Reason, Slot, StudentProfile


def _positions(slots: tuple[Slot, ...]) -> list[Slot]:
    """Expand slots into individual positions (a slot choosing k = k positions)."""
    out: list[Slot] = []
    for s in slots:
        out.extend([s] * s.choose)
    return out


def _fits(kb: KnowledgeBase, subject: str, grade: str, slot: Slot) -> bool:
    if not kb.scale.is_principal_pass(grade):
        return False
    if slot.subjects is not None and subject not in slot.subjects:
        return False
    if slot.min_grade is not None and not kb.scale.at_least(grade, slot.min_grade):
        return False
    return True


def _best_assignment(
    kb: KnowledgeBase, profile: StudentProfile, slots: tuple[Slot, ...]
) -> tuple[str, ...] | None:
    """Best (highest-points) assignment of distinct student subjects to all
    slot positions, or None if impossible. Sizes are tiny (<=4 subjects,
    <=3 positions) so exhaustive search is fine and obviously correct."""
    positions = _positions(slots)
    subjects = list(profile.grades)
    if len(subjects) < len(positions):
        return None
    best: tuple[float, tuple[str, ...]] | None = None
    for perm in permutations(subjects, len(positions)):
        if all(_fits(kb, subj, profile.grades[subj], pos) for subj, pos in zip(perm, positions)):
            pts = sum(kb.scale.points_for(profile.grades[s]) for s in perm)
            if best is None or pts > best[0]:
                best = (pts, perm)
    return best[1] if best else None


def _points_for_basis(kb: KnowledgeBase, profile: StudentProfile, programme: Programme,
                      matched: tuple[str, ...]) -> tuple[float, str]:
    if programme.points_basis == "best_three":
        principal_pts = sorted(
            (kb.scale.points_for(g) for s, g in profile.grades.items()
             if kb.scale.is_principal_pass(g)),
            reverse=True,
        )[:3]
        return sum(principal_pts), "best three principal passes"
    pts = sum(kb.scale.points_for(profile.grades[s]) for s in matched)
    return pts, "subjects defining admission"


def _slot_description(kb: KnowledgeBase, slot: Slot) -> str:
    floor = f" at grade {slot.min_grade} or better" if slot.min_grade else ""
    if slot.subjects is None:
        return f"{slot.choose} principal pass(es) in any subject{floor}"
    names = ", ".join(sorted(kb.subjects[s] for s in slot.subjects))
    return f"{slot.choose} principal pass(es){floor} from: {names}"


def evaluate_programme(
    kb: KnowledgeBase, profile: StudentProfile, programme: Programme
) -> ProgrammeResult:
    result = ProgrammeResult(programme=programme, eligible=False)
    matched = _best_assignment(kb, profile, programme.slots)

    if matched is None:
        for slot in programme.slots:
            ok_subjects = [
                s for s, g in profile.grades.items() if _fits(kb, s, g, slot)
            ]
            result.reasons.append(
                Reason(
                    rule="subject_requirement",
                    ok=len(ok_subjects) >= slot.choose,
                    detail=f"Needs {_slot_description(kb, slot)}; "
                    f"you satisfy this with {len(ok_subjects)} subject(s)."
                    " Note: one subject cannot count twice across requirements.",
                )
            )
        result.reasons.append(
            Reason(
                rule="overall",
                ok=False,
                detail="Subject requirements not met.",
            )
        )
        return result

    matched_names = ", ".join(
        f"{kb.subjects[s]} ({profile.grades[s]})" for s in matched
    )
    result.matched_subjects = matched
    result.reasons.append(
        Reason(
            rule="subject_requirement",
            ok=True,
            detail=f"Subject requirements met with: {matched_names}.",
        )
    )

    pts, basis_desc = _points_for_basis(kb, profile, programme, matched)
    pts_ok = pts >= programme.min_points
    result.reasons.append(
        Reason(
            rule="minimum_points",
            ok=pts_ok,
            detail=f"You have {pts:g} points ({basis_desc}); "
            f"minimum required is {programme.min_points:g}.",
        )
    )

    result.eligible = pts_ok
    if result.eligible:
        n = len(matched)
        achieved = sum(kb.scale.points_for(profile.grades[s]) for s in matched)
        result.strength = achieved / (5.0 * n) if n else 0.0
        result.strength_detail = (
            f"{achieved:g} of {5 * n:g} possible points in {matched_names}"
        )
        if programme.additional_requirements:
            result.reasons.append(
                Reason(
                    rule="additional_requirements",
                    ok=True,
                    detail="Also check (not auto-verified): "
                    + " ".join(programme.additional_requirements),
                )
            )
    return result


def evaluate_all(kb: KnowledgeBase, profile: StudentProfile) -> list[ProgrammeResult]:
    """Evaluate the student against every programme in the knowledge base."""
    return [evaluate_programme(kb, profile, p) for p in kb.programmes]


def validate_profile(kb: KnowledgeBase, grades: dict[str, str]) -> list[str]:
    """Return a list of problems with a raw grades dict (empty = valid)."""
    problems = []
    if not grades:
        problems.append("no subjects given")
    for subject, grade in grades.items():
        if subject not in kb.subjects:
            problems.append(f"unknown subject: '{subject}'")
        if grade not in kb.scale.points:
            problems.append(f"unknown grade '{grade}' for subject '{subject}'")
    return problems
