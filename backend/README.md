# North Star — backend

Course eligibility & fit engine for Tanzanian Form 6 graduates. A student
submits their NECTA subject combination and grades; the API returns a ranked,
grouped, **explained** set of degree programmes they actually qualify for.

Deterministic, explainable expert system — no AI in the core. Data transcribed
from the TCU 2026/27 Bachelor's Degree Admission Guidebook (each programme
carries its source page).

## Run it

```bash
cd backend
pip install -e .[dev]
pytest                      # full suite
uvicorn northstar.api:app   # serves on http://127.0.0.1:8000
```

The API also serves the reference web client at **http://127.0.0.1:8000/** as a
convenience. That client is a **separate deliverable** living in [`web/`](../web/)
— the API is complete without it, and `/` returns 404 (with the path it looked
in) if no client is present. Set `NORTH_STAR_WEB_DIR` to serve one from
elsewhere.

CORS is permissive (`*`): the API serves public, read-only data and accepts no
credentials, so a client hosted on another origin works without configuration.

**Interactive API docs are built in** (FastAPI): with the server running, open

- http://127.0.0.1:8000/docs — Swagger UI (try requests from the browser)
- http://127.0.0.1:8000/redoc — reference-style docs

## API

### `POST /match` — the main endpoint

Request: subject ids (see `GET /subjects`) mapped to A-level grades
(`A B C D E` principal · `S` subsidiary · `F` fail), plus optional
`interests` — ACT World of Work areas (`ideas` / `people` / `data` / `things`,
see `GET /interests`).

```bash
curl -s localhost:8000/match -X POST -H 'content-type: application/json' \
  -d '{"grades": {"physics": "B", "chemistry": "A", "biology": "A"}}'

# with interests → adds annotations + the "bridge" group
curl -s localhost:8000/match -X POST -H 'content-type: application/json' \
  -d '{"grades": {"history": "B", "kiswahili": "A", "literature_in_english": "C"},
       "interests": ["things"]}'
```

Response shape:

```jsonc
{
  "obvious_areas": ["health", "medicine", "science"],   // areas this combination is usually steered toward
  "groups": {
    "for_you":        [ /* eligible + strong fit, in expected areas   */ ],
    "discoveries":    [ /* eligible + strong fit, OUTSIDE the expected path */ ],
    "other_eligible": [ /* everything else they qualify for — nothing hidden */ ],
    "bridge":         [ /* only when interests sent: programmes matching what the
                           student WANTS but is not eligible for, with reasons
                           spelling out exactly what it would take */ ]
  },
  "counts": { "eligible": 13, "for_you": 8, "discoveries": 5, "other_eligible": 0, "not_eligible": 9 }
}
```

Each programme result:

```jsonc
{
  "programme": {
    "id": "suza-doctor-of-medicine",
    "name": "Doctor of Medicine",
    "institution": "State University of Zanzibar (SUZA)",
    "location": "Zanzibar",
    "requirement_text": "Three principal passes in Physics, Chemistry and Biology ...",
    "additional_requirements": [],        // conditions we can't auto-check (e.g. O-level) — shown, not hidden
    "capacity": 50,
    "duration_years": 5,
    "checklist": {                        // the letter's due-diligence checklist
      "what_is_it": "Trains medical doctors (clinical medicine).",
      "cost": null,                       // null = data not yet available — never invented
      "time_to_employment": null,
      "salary": null,
      "insider_notes": null
    },
    "source": "TCU 2026/27 guidebook, p.237 (SUZA)"
  },
  "eligible": true,
  "conditional": false,                   // true = "you qualify IF …" (see below)
  "unverified_conditions": [],            // conditions we cannot check from A-level grades
  "reasons": [                            // machine-readable explanation, always present
    { "rule": "subject_requirement", "ok": true, "detail": "Subject requirements met with: Chemistry (A), Biology (A), Physics (B)." },
    { "rule": "minimum_points",      "ok": true, "detail": "You have 14 points (subjects defining admission); minimum required is 6." }
  ],
  "strength": 0.9333,                     // avg grade quality in the subjects this programme asks for (1.0 = all A)
  "strength_detail": "14 of 15 possible points in Chemistry (A), Biology (A), Physics (B)",
  "matched_subjects": ["chemistry", "biology", "physics"]
}
```

Errors: invalid input → `422` with a list of problems
(e.g. `["unknown subject: 'alchemy'"]`).

### Reference endpoints (for building clients)

| Endpoint | Returns |
|---|---|
| `GET /subjects` | Subject ids + display names, and the valid grade letters |
| `GET /combinations` | Common combinations (PCB, PCM, EGM, …) with their subjects |
| `GET /interests` | ACT World of Work interest areas (Ideas / People / Data / Things) |
| `GET /programmes` | The full programme catalogue with requirements & checklists |
| `GET /health` | Liveness + programme count |

## How matching works (short version)

1. **Eligibility** — each programme's requirement is a set of *slots*
   (e.g. MD: Chemistry ≥D + Biology ≥D + Physics ≥D, total ≥6 points).
   Slots must be filled by distinct principal passes; the engine tries all
   assignments and always reads the rules in the student's favour.
2. **Strength** — points achieved in the matched subjects ÷ points possible.
   A measure of how strongly the student meets *that programme's own ask*.
3. **Grouping** — programmes in areas typical for the student's combination →
   **For you**; strong fits outside those areas → **Discoveries**; the rest →
   **Other eligible**. Thresholds are tunables at the top of `ranking.py`.
4. **Ranking within groups** — by `matched_points`, the admission points the
   student brings to that programme's defining subjects (TCU's own currency):
   14 points into Medicine outranks 10 points into a two-subject programme.
   Strength breaks ties.

**Three verdicts, not two.** `eligible: true, conditional: false` is a plain yes.
`eligible: true, conditional: true` means the student meets everything we can
check, but the guidebook states conditions we cannot verify from A-level grades
(O-level results, fitness tests) — listed in `unverified_conditions`. Clients
must render this as "you qualify **if** …". `eligible: false` is a no, with the
failing rule in `reasons`.

Known limitations (deliberate, documented):
- `additional_requirements` (O-level conditions, fitness tests) are surfaced
  to the user but not machine-evaluated — the MVP input is A-level only. These
  now drive `conditional`, so eligibility is never overstated.
- 13 programmes still carry an *A-level* condition in prose that we could in
  principle encode (conjunctive subsidiary rules, "if not X then Y" shapes,
  multi-subject grade-floor lists, and PDF-truncated sentences). They surface
  as `conditional`, so the student is warned rather than misled.
- The knowledge base holds 356 programmes across 39 institutions: 30
  human-curated plus 326 machine-extracted from the guidebook by
  `scripts/extract_guidebook.py` (flagged `machine_parsed` in the API so
  clients can show provenance). ~311 guidebook rows whose requirement text
  didn't parse cleanly sit in `data/extraction_review.json` — kept with raw
  text and page refs for human review, never served as fact.

## Layout

```
backend/
  northstar/
    data/         # the knowledge base (JSON) — see data/README.md for the schema
    loader.py     # load + validate the knowledge base
    engine.py     # eligibility + strength (pure core)
    ranking.py    # For you / Discoveries / Bridge grouping
    api.py        # FastAPI transport (thin)
  scripts/        # extract_guidebook.py — PDF → structured programme data
  tests/          # loader, engine, ranking, interests, pipeline, API, client,
                  # and six student personas as regressions
```

Clients live outside this directory (`web/`). Project overview and the open
research agenda are in the repo root: `README.md` and `RESEARCH.md`.
