"""FastAPI transport layer — thin by design. All logic lives in the core
modules (loader/engine/ranking), which stay importable without any web stack.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
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

# The largest legitimate request is a handful of subjects and interests —
# well under a kilobyte. Bodies are buffered in memory before validation, so
# without a ceiling one unauthenticated request can exhaust a small container.
MAX_BODY_BYTES = 64 * 1024


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    declared = request.headers.get("content-length")
    if declared is not None and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
        return JSONResponse(
            status_code=413,
            content={"detail": f"Request too large (limit {MAX_BODY_BYTES} bytes)."},
        )
    return await call_next(request)


# Results are large JSON and students are often on slow mobile connections.
app.add_middleware(GZipMiddleware, minimum_size=1000)

# The API serves public, read-only reference data and takes no credentials, so
# any client origin may call it — a client hosted apart from the API (or opened
# from disk) still works. `allow_credentials` stays off: a wildcard origin must
# never be paired with cookies.
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
        # Log the path for the operator; don't hand the filesystem layout to
        # a stranger.
        print(f"[north-star] no web client at {page} (set NORTH_STAR_WEB_DIR)")
        raise HTTPException(
            status_code=404,
            detail="No web client is deployed here. The API is documented at /docs.",
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
        # Cap the echo: every problem quotes the caller's own input back, so an
        # unbounded list turns a bad request into an amplification vector.
        if len(problems) > 20:
            problems = problems[:20] + [f"… and {len(problems) - 20} more problems"]
        raise HTTPException(status_code=422, detail=problems)
    profile = StudentProfile(grades=req.grades)
    results = evaluate_all(kb, profile)
    return rank_and_group(kb, profile, results, interests=req.interests)
