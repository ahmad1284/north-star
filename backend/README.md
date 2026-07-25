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
pytest                      # 30 tests
uvicorn northstar.api:app   # serves on http://127.0.0.1:8000
```

**Interactive API docs are built in** (FastAPI): with the server running, open

- http://127.0.0.1:8000/docs — Swagger UI (try requests from the browser)
- http://127.0.0.1:8000/redoc — reference-style docs

## API

### `POST /match` — the main endpoint

Request: subject ids (see `GET /subjects`) mapped to A-level grades
(`A B C D E` principal · `S` subsidiary · `F` fail).

```bash
curl -s localhost:8000/match -X POST -H 'content-type: application/json' \
  -d '{"grades": {"physics": "B", "chemistry": "A", "biology": "A"}}'
```

Response shape:

```jsonc
{
  "obvious_areas": ["health", "medicine", "science"],   // areas this combination is usually steered toward
  "groups": {
    "for_you":        [ /* eligible + strong fit, in expected areas   */ ],
    "discoveries":    [ /* eligible + strong fit, OUTSIDE the expected path */ ],
    "other_eligible": [ /* everything else they qualify for — nothing hidden */ ]
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

Known limitations (deliberate, documented):
- `additional_requirements` (O-level conditions, fitness tests) are surfaced
  to the user but not machine-evaluated — the MVP input is A-level only.
- Strength is relative to each programme's own requirements, so a programme
  asking for 2 subjects can outrank one asking for 3 for a straight-A student.
  Open tuning question, tracked in the PR discussion.
- The seed covers 22 real programmes across 5 institutions; business-heavy
  combinations (ECA) currently see few options — a data-breadth artifact, not
  the real market. More transcription widens it.

## Layout

```
backend/
  northstar/
    data/         # the knowledge base (JSON) — see data/README.md for the schema
    loader.py     # load + validate the knowledge base
    engine.py     # eligibility + strength (pure core)
    ranking.py    # For you / Discoveries grouping
    api.py        # FastAPI transport (thin)
  tests/          # loader, engine, ranking, API, and persona sanity tests
```
