"""Load and validate the JSON data files into domain models.

All data problems fail loudly at load time with a clear message — an expert
system is only trustworthy if its knowledge base is validated.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Combination, GradeScale, Programme, Slot

DATA_DIR = Path(__file__).parent / "data"


class DataError(ValueError):
    """A problem in the knowledge-base data files."""


def _read(name: str) -> dict:
    path = DATA_DIR / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise DataError(f"missing data file: {path}")
    except json.JSONDecodeError as e:
        raise DataError(f"invalid JSON in {path}: {e}")


def load_grade_scale() -> GradeScale:
    raw = _read("grading.json")
    return GradeScale(
        points=dict(raw["points"]),
        principal_pass_grades=frozenset(raw["principal_pass_grades"]),
    )


def load_subjects() -> dict[str, str]:
    """subject_id -> display name."""
    raw = _read("subjects.json")
    subjects = {s["id"]: s["name"] for s in raw["subjects"]}
    if len(subjects) != len(raw["subjects"]):
        raise DataError("duplicate subject ids in subjects.json")
    return subjects


def load_combinations(known_subjects: set[str]) -> dict[str, Combination]:
    raw = _read("combinations.json")
    combos: dict[str, Combination] = {}
    for c in raw["combinations"]:
        for s in c["subjects"]:
            if s not in known_subjects:
                raise DataError(f"combination {c['code']}: unknown subject '{s}'")
        combos[c["code"]] = Combination(
            code=c["code"],
            name=c["name"],
            subjects=tuple(c["subjects"]),
            obvious_tags=frozenset(c["obvious_tags"]),
        )
    return combos


def _parse_slot(raw: dict, prog_id: str, known_subjects: set[str], grades: set[str]) -> Slot:
    subjects_raw = raw["from"]
    if subjects_raw == "any":
        subjects = None
    else:
        for s in subjects_raw:
            if s not in known_subjects:
                raise DataError(f"programme {prog_id}: unknown subject '{s}' in slot")
        subjects = frozenset(subjects_raw)
    min_grade = raw.get("min_grade")
    if min_grade is not None and min_grade not in grades:
        raise DataError(f"programme {prog_id}: unknown min_grade '{min_grade}'")
    choose = int(raw["choose"])
    if choose < 1:
        raise DataError(f"programme {prog_id}: slot choose must be >= 1")
    if subjects is not None and choose > len(subjects):
        raise DataError(f"programme {prog_id}: slot chooses {choose} from {len(subjects)} subjects")
    return Slot(choose=choose, subjects=subjects, min_grade=min_grade)


def load_programmes(known_subjects: set[str], scale: GradeScale) -> list[Programme]:
    raw = _read("programmes.json")
    grades = set(scale.points)
    programmes: list[Programme] = []
    seen_ids: set[str] = set()
    for p in raw["programmes"]:
        pid = p["id"]
        if pid in seen_ids:
            raise DataError(f"duplicate programme id: {pid}")
        seen_ids.add(pid)
        if p["points_basis"] not in ("slots", "best_three"):
            raise DataError(f"programme {pid}: bad points_basis '{p['points_basis']}'")
        slots = tuple(_parse_slot(s, pid, known_subjects, grades) for s in p["slots"])
        if not slots:
            raise DataError(f"programme {pid}: no requirement slots")
        checklist = p.get("checklist", {})
        programmes.append(
            Programme(
                id=pid,
                code=p["code"],
                name=p["name"],
                institution=p["institution"],
                location=p["location"],
                tags=frozenset(p["tags"]),
                requirement_text=p["requirement_text"],
                slots=slots,
                min_points=float(p["min_points"]),
                points_basis=p["points_basis"],
                additional_requirements=tuple(p.get("additional_requirements", [])),
                capacity=p.get("capacity"),
                duration_years=p.get("duration_years"),
                checklist=checklist,
                source=p.get("source", ""),
            )
        )
    return programmes


class KnowledgeBase:
    """Everything the engine knows, loaded and validated once."""

    def __init__(self) -> None:
        self.scale = load_grade_scale()
        self.subjects = load_subjects()
        self.combinations = load_combinations(set(self.subjects))
        self.programmes = load_programmes(set(self.subjects), self.scale)


def load_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase()
