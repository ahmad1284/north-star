"""Load and validate the JSON data files into domain models.

All data problems fail loudly at load time with a clear message — an expert
system is only trustworthy if its knowledge base is validated.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Combination, Constraint, GradeScale, Programme, Slot

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


CONSTRAINT_KINDS = (
    "must_include",
    "subsidiary_from",
    "subsidiary_all",
    "if_not_matched_subsidiary",
)

# A prose condition that is advisory rather than a hard rule: it changes a
# student's chances, not their eligibility, so it must not make a result
# "conditional".
_ADVISORY = ("preference", "priority", "given high", "may be considered")


def _parse_constraint(
    raw: dict, prog_id: str, known_subjects: set[str], grades: set[str] | None = None
) -> Constraint:
    kind = raw.get("kind")
    if kind not in CONSTRAINT_KINDS:
        raise DataError(f"programme {prog_id}: unknown constraint kind '{kind}'")
    subjects = raw.get("subjects") or []
    if not subjects:
        raise DataError(f"programme {prog_id}: constraint '{kind}' has no subjects")
    for s in subjects:
        if s not in known_subjects:
            raise DataError(f"programme {prog_id}: constraint references unknown subject '{s}'")
    min_grade = raw.get("min_grade")
    if min_grade is not None and grades is not None and min_grade not in grades:
        raise DataError(f"programme {prog_id}: constraint has unknown min_grade '{min_grade}'")
    triggers = raw.get("trigger_subjects") or []
    for s in triggers:
        if s not in known_subjects:
            raise DataError(f"programme {prog_id}: constraint trigger has unknown subject '{s}'")
    if kind == "if_not_matched_subsidiary" and not triggers:
        raise DataError(f"programme {prog_id}: if_not_matched_subsidiary needs trigger_subjects")
    return Constraint(
        kind=kind,
        subjects=frozenset(subjects),
        source_text=raw.get("source_text", ""),
        min_grade=min_grade,
        trigger_subjects=frozenset(triggers),
    )


def _unverified(additional: tuple[str, ...]) -> tuple[str, ...]:
    """Which stated conditions we cannot check from A-level grades alone.

    Everything left in `additional_requirements` is by definition unevaluated,
    so the only question is whether it is a *condition* (affects eligibility)
    or advice (affects chances). Notes we wrote about the data itself are not
    guidebook conditions and are excluded.
    """
    out = []
    for s in additional:
        low = s.lower()
        if any(a in low for a in _ADVISORY):
            continue
        if low.startswith(("guidebook lists", "requirement text truncated")):
            continue
        out.append(s)
    return tuple(out)


def _parse_programme(p: dict, known_subjects: set[str], grades: set[str]) -> Programme:
    pid = p["id"]
    if p["points_basis"] not in ("slots", "best_three"):
        raise DataError(f"programme {pid}: bad points_basis '{p['points_basis']}'")
    slots = tuple(_parse_slot(s, pid, known_subjects, grades) for s in p["slots"])
    if not slots:
        raise DataError(f"programme {pid}: no requirement slots")
    additional = tuple(p.get("additional_requirements", []))
    return Programme(
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
        additional_requirements=additional,
        capacity=p.get("capacity"),
        duration_years=p.get("duration_years"),
        checklist=p.get("checklist", {}),
        source=p.get("source", ""),
        machine_parsed=bool(p.get("machine_parsed", False)),
        constraints=tuple(
            _parse_constraint(c, pid, known_subjects, grades)
            for c in p.get("constraints", [])
        ),
        unverified_conditions=_unverified(additional),
    )


def load_programmes(known_subjects: set[str], scale: GradeScale) -> list[Programme]:
    """Curated programmes plus machine-extracted ones (if present). Curated
    entries always win on programme-code conflict — human judgement over
    machine parsing."""
    grades = set(scale.points)
    programmes: list[Programme] = []
    seen_ids: set[str] = set()
    seen_codes: set[str] = set()
    for source_file in ("programmes.json", "programmes_extracted.json"):
        if source_file != "programmes.json" and not (DATA_DIR / source_file).exists():
            continue
        for p in _read(source_file)["programmes"]:
            if p["id"] in seen_ids:
                raise DataError(f"duplicate programme id: {p['id']}")
            if p["code"] in seen_codes:
                if source_file == "programmes.json":
                    raise DataError(f"duplicate programme code: {p['code']}")
                continue  # curated version already loaded; skip extracted twin
            prog = _parse_programme(p, known_subjects, grades)
            seen_ids.add(prog.id)
            seen_codes.add(prog.code)
            programmes.append(prog)
    return programmes


def load_interests() -> tuple[dict[str, dict], dict[str, frozenset[str]]]:
    """Returns (areas by id, programme-tag -> interest areas)."""
    raw = _read("interests.json")
    areas = {a["id"]: a for a in raw["areas"]}
    tag_areas: dict[str, frozenset[str]] = {}
    for tag, area_ids in raw["tag_areas"].items():
        for a in area_ids:
            if a not in areas:
                raise DataError(f"interests.json: tag '{tag}' maps to unknown area '{a}'")
        tag_areas[tag] = frozenset(area_ids)
    return areas, tag_areas


class KnowledgeBase:
    """Everything the engine knows, loaded and validated once."""

    def __init__(self) -> None:
        self.scale = load_grade_scale()
        self.subjects = load_subjects()
        self.combinations = load_combinations(set(self.subjects))
        self.programmes = load_programmes(set(self.subjects), self.scale)
        self.interest_areas, self.tag_areas = load_interests()
        for p in self.programmes:
            if not self.programme_areas(p.tags):
                raise DataError(
                    f"programme {p.id}: tags {sorted(p.tags)} resolve to no interest area"
                )

    def programme_areas(self, tags: frozenset[str]) -> frozenset[str]:
        """Interest areas (ACT World of Work) a set of programme tags maps to."""
        out: set[str] = set()
        for t in tags:
            out |= self.tag_areas.get(t, frozenset())
        return frozenset(out)


def load_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase()
