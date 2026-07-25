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
from .models import Constraint, Programme, ProgrammeResult, Reason, Slot, StudentProfile


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


def _holds(kb: KnowledgeBase, profile: StudentProfile, subject: str, floor: str | None) -> bool:
    """Student holds `subject` at `floor` or better (any pass if floor is None)."""
    grade = profile.grades.get(subject)
    if grade is None:
        return False
    return kb.scale.at_least(grade, floor) if floor else grade != "F"


def _satisfies_assignment_constraints(
    kb: KnowledgeBase,
    profile: StudentProfile,
    assignment: tuple[str, ...],
    constraints: tuple[Constraint, ...],
) -> bool:
    """Constraints whose truth depends on WHICH subjects filled the slots.

    Checked inside the assignment search so that a student who could satisfy
    them by choosing a different valid assignment is never wrongly rejected.
    """
    for c in constraints:
        if c.kind == "must_include":
            if not any(
                s in c.subjects
                and (c.min_grade is None or kb.scale.at_least(profile.grades[s], c.min_grade))
                for s in assignment
            ):
                return False
        elif c.kind == "if_not_matched_subsidiary":
            # rule only fires if none of the trigger subjects were used
            if set(assignment) & c.trigger_subjects:
                continue
            if not any(_holds(kb, profile, s, c.min_grade) for s in c.subjects):
                return False
    return True


def _best_assignment(
    kb: KnowledgeBase,
    profile: StudentProfile,
    slots: tuple[Slot, ...],
    constraints: tuple[Constraint, ...] = (),
) -> tuple[str, ...] | None:
    """Best (highest-points) assignment of distinct student subjects to all slot
    positions that ALSO satisfies the must_include constraints, or None if no
    such assignment exists. Sizes are tiny (<=4 subjects, <=3 positions) so
    exhaustive search is fine and obviously correct.

    Constraints are applied during the search, not after it: picking the
    highest-points assignment first and then testing the constraint would
    wrongly reject a student who has a valid — if lower-scoring — assignment.
    """
    positions = _positions(slots)
    subjects = list(profile.grades)
    if len(subjects) < len(positions):
        return None
    best: tuple[float, tuple[str, ...]] | None = None
    for perm in permutations(subjects, len(positions)):
        if not all(
            _fits(kb, subj, profile.grades[subj], pos) for subj, pos in zip(perm, positions)
        ):
            continue
        if not _satisfies_assignment_constraints(kb, profile, perm, constraints):
            continue
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
    matched = _best_assignment(kb, profile, programme.slots, programme.constraints)

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
        # Distinguish "slots unfillable" from "slots fillable but a
        # must_include constraint blocks every valid assignment" — the student
        # deserves to know which wall they hit.
        if programme.constraints and _best_assignment(kb, profile, programme.slots):
            for c in programme.constraints:
                names = ", ".join(sorted(kb.subjects[s] for s in c.subjects))
                floor = f" at grade {c.min_grade} or better" if c.min_grade else ""
                if c.kind == "must_include":
                    result.reasons.append(
                        Reason(
                            rule="must_include",
                            ok=False,
                            detail=f"At least one of your qualifying passes must be in: "
                            f"{names}{floor}. " + (c.source_text or ""),
                        )
                    )
                elif c.kind == "if_not_matched_subsidiary":
                    triggers = ", ".join(
                        sorted(kb.subjects[s] for s in c.trigger_subjects)
                    )
                    result.reasons.append(
                        Reason(
                            rule="conditional_subsidiary",
                            ok=False,
                            detail=f"Because none of your qualifying passes is in {triggers}, "
                            f"you also need at least a subsidiary pass in: {names}. "
                            + (c.source_text or ""),
                        )
                    )
        result.reasons.append(
            Reason(rule="overall", ok=False, detail="Subject requirements not met.")
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

    constraints_ok = True
    for c in programme.constraints:
        names = ", ".join(sorted(kb.subjects[s] for s in c.subjects))
        if c.kind == "must_include":
            # guaranteed by _best_assignment, recorded so the student sees it
            result.reasons.append(
                Reason(
                    rule="must_include",
                    ok=True,
                    detail=f"One of your qualifying passes is in {names}, as required.",
                )
            )
        elif c.kind == "subsidiary_from":
            # A holding requirement: the student must HAVE one of these
            # subjects at the required grade. It need not be one of the
            # passes counted toward the slots.
            held = sorted(s for s in c.subjects if _holds(kb, profile, s, c.min_grade))
            ok = bool(held)
            constraints_ok = constraints_ok and ok
            need = f"grade {c.min_grade} or better" if c.min_grade else "at least a subsidiary pass"
            result.reasons.append(
                Reason(
                    rule="subsidiary_requirement",
                    ok=ok,
                    detail=(
                        f"You have {kb.subjects[held[0]]} ({profile.grades[held[0]]}), "
                        f"which satisfies the requirement of {need}."
                        if ok
                        else f"Requires {need} in: {names}."
                    ),
                )
            )
        elif c.kind == "subsidiary_all":
            # ALL of these subjects are required (e.g. "Physics AND Mathematics")
            missing = sorted(
                kb.subjects[s] for s in c.subjects if not _holds(kb, profile, s, c.min_grade)
            )
            ok = not missing
            constraints_ok = constraints_ok and ok
            need = f"grade {c.min_grade} or better" if c.min_grade else "at least a subsidiary pass"
            result.reasons.append(
                Reason(
                    rule="subsidiary_all_requirement",
                    ok=ok,
                    detail=(
                        f"You hold all the required subjects ({names}) at {need}."
                        if ok
                        else f"Requires {need} in ALL of: {names}. "
                        f"You are missing: {', '.join(missing)}."
                    ),
                )
            )
        elif c.kind == "if_not_matched_subsidiary":
            # Guaranteed by _best_assignment; recorded so the student sees why.
            triggers = ", ".join(sorted(kb.subjects[s] for s in c.trigger_subjects))
            used_trigger = bool(set(matched) & c.trigger_subjects)
            result.reasons.append(
                Reason(
                    rule="conditional_subsidiary",
                    ok=True,
                    detail=(
                        f"One of your qualifying passes is in {triggers}, so the extra "
                        f"subsidiary requirement does not apply."
                        if used_trigger
                        else f"You hold the subsidiary pass in {names} required when none "
                        f"of your qualifying passes is in {triggers}."
                    ),
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

    result.eligible = pts_ok and constraints_ok
    if result.eligible:
        n = len(matched)
        achieved = sum(kb.scale.points_for(profile.grades[s]) for s in matched)
        result.matched_points = achieved
        result.strength = achieved / (5.0 * n) if n else 0.0
        result.strength_detail = (
            f"{achieved:g} of {5 * n:g} possible points in {matched_names}"
        )
        # Conditions we cannot check from A-level grades make this a
        # qualified yes, not a plain one.
        result.unverified_conditions = programme.unverified_conditions
        result.conditional = bool(programme.unverified_conditions)
        if result.conditional:
            result.reasons.append(
                Reason(
                    rule="unverified_condition",
                    ok=False,
                    detail="You meet everything we can check, but this programme also "
                    "requires (we cannot verify from A-level grades): "
                    + " ".join(programme.unverified_conditions),
                )
            )
        advisory = [
            s for s in programme.additional_requirements
            if s not in programme.unverified_conditions
        ]
        if advisory:
            result.reasons.append(
                Reason(
                    rule="additional_notes",
                    ok=True,
                    detail="Also note: " + " ".join(advisory),
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
