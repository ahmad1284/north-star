"""FastAPI transport layer — thin by design. All logic lives in the core
modules (loader/engine/ranking), which stay importable without any web stack.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

# The API serves public, read-only reference data and takes no credentials, so
# any client origin may call it — a client hosted apart from the API (or opened
# from disk) still works.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    grades: dict[str, str] = Field(
        ...,
        description="subject_id -> A-level grade (A..E principal, S subsidiary, F fail)",
        examples=[{"physics": "C", "chemistry": "B", "biology": "A"}],
    )
    interests: list[str] | None = Field(
        default=None,
        description="Optional ACT World of Work interest areas the student is "
        "drawn to (see GET /interests). Adds interest annotations and a "
        "'bridge' group: interest-matched programmes they are not eligible "
        "for, with reasons for what it would take.",
        examples=[["things", "ideas"]],
    )


# Clients live outside this package (see web/). The API is complete without
# them; serving the bundled one is a convenience for local use and demos.
# NORTH_STAR_WEB_DIR overrides the location (e.g. when deployed separately).
_WEB_DIR = Path(
    os.environ.get("NORTH_STAR_WEB_DIR", Path(__file__).resolve().parents[2] / "web")
)


@app.get("/", include_in_schema=False)
def client() -> FileResponse:
    """Serve the bundled web client, if one is present next to the backend."""
    page = _WEB_DIR / "index.html"
    if not page.is_file():
        raise HTTPException(
            status_code=404,
            detail="No web client found. The API itself is at /docs. "
            f"Looked in {_WEB_DIR} (override with NORTH_STAR_WEB_DIR).",
        )
    return FileResponse(page, media_type="text/html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "programmes": len(kb.programmes)}


@app.get("/subjects")
def subjects() -> dict:
    return {
        "subjects": [{"id": sid, "name": name} for sid, name in kb.subjects.items()],
        "grades": sorted(kb.scale.points, key=lambda g: -kb.scale.points[g]),
    }


@app.get("/interests")
def interests() -> dict:
    return {"areas": list(kb.interest_areas.values())}


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
    if req.interests:
        problems += [
            f"unknown interest area: '{a}'"
            for a in req.interests
            if a not in kb.interest_areas
        ]
    if problems:
        raise HTTPException(status_code=422, detail=problems)
    profile = StudentProfile(grades=req.grades)
    results = evaluate_all(kb, profile)
    return rank_and_group(kb, profile, results, interests=req.interests)
