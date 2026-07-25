"""FastAPI transport layer — thin by design. All logic lives in the core
modules (loader/engine/ranking), which stay importable without any web stack.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .engine import evaluate_all, validate_profile
from .loader import load_knowledge_base
from .models import StudentProfile
from .ranking import rank_and_group

kb = load_knowledge_base()

app = FastAPI(
    title="North Star API",
    description="Course eligibility & fit for Tanzanian Form 6 graduates. "
    "Deterministic, explainable expert system over TCU guidebook data.",
    version="0.1.0",
)


class MatchRequest(BaseModel):
    grades: dict[str, str] = Field(
        ...,
        description="subject_id -> A-level grade (A..E principal, S subsidiary, F fail)",
        examples=[{"physics": "C", "chemistry": "B", "biology": "A"}],
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "programmes": len(kb.programmes)}


@app.get("/subjects")
def subjects() -> dict:
    return {
        "subjects": [{"id": sid, "name": name} for sid, name in kb.subjects.items()],
        "grades": sorted(kb.scale.points, key=lambda g: -kb.scale.points[g]),
    }


@app.get("/combinations")
def combinations() -> dict:
    return {
        "combinations": [
            {"code": c.code, "name": c.name, "subjects": list(c.subjects)}
            for c in kb.combinations.values()
        ]
    }


@app.get("/programmes")
def programmes() -> dict:
    return {
        "programmes": [
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "institution": p.institution,
                "location": p.location,
                "tags": sorted(p.tags),
                "requirement_text": p.requirement_text,
                "min_points": p.min_points,
                "capacity": p.capacity,
                "duration_years": p.duration_years,
                "checklist": p.checklist,
                "source": p.source,
            }
            for p in kb.programmes
        ]
    }


@app.post("/match")
def match(req: MatchRequest) -> dict:
    problems = validate_profile(kb, req.grades)
    if problems:
        raise HTTPException(status_code=422, detail=problems)
    profile = StudentProfile(grades=req.grades)
    results = evaluate_all(kb, profile)
    return rank_and_group(kb, profile, results)
