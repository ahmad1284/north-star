"""Core domain models for the North Star eligibility engine.

Plain dataclasses, no framework dependencies: the engine core stays pure and
channel-agnostic (usable from an API, a CLI, a WhatsApp webhook, tests...).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GradeScale:
    """Canonical NECTA A-level grade scale."""

    points: dict[str, float]
    principal_pass_grades: frozenset[str]

    def points_for(self, grade: str) -> float:
        return self.points[grade]

    def is_principal_pass(self, grade: str) -> bool:
        return grade in self.principal_pass_grades

    def at_least(self, grade: str, floor: str) -> bool:
        """True if `grade` meets or beats `floor` (e.g. B meets floor C)."""
        return self.points[grade] >= self.points[floor]


@dataclass(frozen=True)
class Slot:
    """One requirement slot: choose `choose` distinct subjects from `subjects`
    (None = any subject), each a principal pass meeting `min_grade` if set."""

    choose: int
    subjects: frozenset[str] | None  # None means "any subject"
    min_grade: str | None = None


@dataclass(frozen=True)
class Constraint:
    """A condition that applies across the whole requirement, not to one slot.

    - ``must_include``: at least one of the subjects satisfying the slots must
      come from this set (e.g. "one of the two principal passes must be in
      Physics or Chemistry or Biology"). The subject still counts toward the
      slots — this is a filter on the assignment, not an extra position.
    - ``subsidiary_from``: the student must hold a subsidiary (S) pass or better
      in one of these subjects.

    Only encode a constraint when every alternative it names is a subject we
    model. If any alternative is unknown to us we cannot fairly enforce it —
    enforcing a partial list would reject students who satisfy the real rule.
    """

    kind: str  # "must_include" | "subsidiary_from"
    subjects: frozenset[str]
    source_text: str = ""
    # Optional grade floor: the qualifying subject must also meet this grade
    # (e.g. "a minimum of 'E' grade in either Chemistry or Geography").
    min_grade: str | None = None


@dataclass(frozen=True)
class Programme:
    id: str
    code: str
    name: str
    institution: str
    location: str
    tags: frozenset[str]
    requirement_text: str
    slots: tuple[Slot, ...]
    min_points: float
    points_basis: str  # "slots" | "best_three"
    additional_requirements: tuple[str, ...]
    capacity: int | None
    duration_years: float | None
    checklist: dict[str, str | None]
    source: str
    machine_parsed: bool = False  # extracted by script (vs human-curated)
    constraints: tuple[Constraint, ...] = ()
    # Conditions the guidebook states that we cannot check from A-level input
    # (O-level grades, fitness tests, interviews). Never silently dropped:
    # they make a result `conditional` rather than plainly eligible.
    unverified_conditions: tuple[str, ...] = ()


@dataclass(frozen=True)
class Combination:
    code: str
    name: str
    subjects: tuple[str, ...]
    obvious_tags: frozenset[str]


@dataclass(frozen=True)
class StudentProfile:
    """What the student gives us: their subjects and grades. Nothing else."""

    grades: dict[str, str]  # subject_id -> grade letter


@dataclass
class Reason:
    """One machine-readable, human-explainable check outcome."""

    rule: str
    ok: bool
    detail: str

    def to_dict(self) -> dict:
        return {"rule": self.rule, "ok": self.ok, "detail": self.detail}


@dataclass
class ProgrammeResult:
    programme: Programme
    eligible: bool
    reasons: list[Reason] = field(default_factory=list)
    strength: float = 0.0
    strength_detail: str = ""
    matched_subjects: tuple[str, ...] = ()
    matched_points: float = 0.0
    # True when the student meets everything we CAN check, but the guidebook
    # states further conditions we cannot verify from A-level grades. Clients
    # should say "you qualify IF …", not "you qualify".
    conditional: bool = False
    unverified_conditions: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        p = self.programme
        return {
            "programme": {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "institution": p.institution,
                "location": p.location,
                "tags": sorted(p.tags),
                "requirement_text": p.requirement_text,
                "additional_requirements": list(p.additional_requirements),
                "capacity": p.capacity,
                "duration_years": p.duration_years,
                "checklist": p.checklist,
                "source": p.source,
                "machine_parsed": p.machine_parsed,
            },
            "eligible": self.eligible,
            "reasons": [r.to_dict() for r in self.reasons],
            "strength": round(self.strength, 4),
            "strength_detail": self.strength_detail,
            "matched_subjects": list(self.matched_subjects),
            "matched_points": self.matched_points,
            "conditional": self.conditional,
            "unverified_conditions": list(self.unverified_conditions),
        }
