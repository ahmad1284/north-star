# North Star knowledge base

Structured data the expert system reasons over. Editable by non-developers;
the loader validates everything at startup and fails loudly on mistakes.

| File | Contents |
|---|---|
| `grading.json` | Canonical NECTA A-level grade→points scale (A=5 … S=0.5, F=0). Principal pass = E or above. |
| `subjects.json` | Subject registry. `id` values are the only identifiers used elsewhere. |
| `combinations.json` | Common A-level combinations (PCB, PCM, …) with `obvious_tags` — the programme areas such students are typically steered toward. Used to separate "For you" from "Discoveries". |
| `programmes.json` | Real programmes transcribed from the TCU 2026/27 guidebook (see `source` per entry). |

## Programme rule schema

```jsonc
{
  "slots": [                      // ALL slots must be satisfied by DISTINCT subjects
    { "choose": 1, "from": ["chemistry"], "min_grade": "C" },   // grade floor
    { "choose": 2, "from": ["physics", "biology"] },            // pick 2 from set
    { "choose": 1, "from": "any" }                              // any subject
  ],
  "min_points": 6.0,              // over slot subjects, or best three (see below)
  "points_basis": "slots",        // "slots" | "best_three"
  "additional_requirements": []   // shown to users; NOT machine-evaluated (e.g. O-level conditions)
}
```

Rules of the data:
- Unknown checklist values are `null` ("data not yet available") — **never invented**.
- Every programme carries a `source` (guidebook page) so claims are auditable.
- `additional_requirements` keeps conditions we can't evaluate from A-level input
  (O-level grades, fitness tests) visible instead of silently dropped.
