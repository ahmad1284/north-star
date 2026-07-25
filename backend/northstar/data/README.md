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
  "constraints": [                // conditions ACROSS slots — enforced by the engine
    { "kind": "must_include", "subjects": ["physics", "chemistry", "biology"],
      "source_text": "One of the two principal passes must be in Physics or Chemistry or Biology." },
    { "kind": "subsidiary_from", "subjects": ["advanced_mathematics"], "min_grade": "E" }
  ],
  "additional_requirements": []   // shown to users; NOT machine-evaluated (e.g. O-level conditions)
}
```

### Constraints — and the distinction that matters

Two kinds, and picking the wrong one is a real bug (it happened once, see below):

| Kind | Meaning | Test |
|---|---|---|
| `must_include` | At least one of the subjects **counted toward the slots** must come from this set. The subject still fills a slot — this filters the assignment, it does not add a position. | *"One of the two principal passes must be in Physics or Chemistry."* |
| `subsidiary_from` | The student must **hold** one of these subjects at `min_grade` (default: any pass, i.e. subsidiary `S` or better). It need **not** count toward the slots. | *"Must have at least a subsidiary pass in Advanced Mathematics."* · *"A minimum of 'E' grade in either Chemistry or Geography."* |
| `subsidiary_all` | The student must hold **every** subject listed (not a choice). | *"A subsidiary pass in Physics **and** Mathematics."* |
| `if_not_matched_subsidiary` | Fires **only** when none of `trigger_subjects` were used to fill the slots; then one of `subjects` must be held. Evaluated during assignment search. | *"If one of the principal passes is not Advanced Mathematics, an applicant must have a subsidiary pass in it."* |

Getting this backwards makes a rule unsatisfiable: encoding a *holding* requirement as
`must_include` rejects every student whenever the named subject isn't in the slot list —
a false negative. Regression test: `tests/test_constraints.py::test_holding_requirement_is_not_an_assignment_requirement`.

**Only encode a constraint when every alternative it names is a subject we model.**
Enforcing a partial alternatives list rejects students who satisfy the real rule. This is
why *"subsidiary in Advanced Mathematics **or** Basic Applied Mathematics"* could only be
encoded once Basic Applied Mathematics existed in `subjects.json`.

`must_include` and `if_not_matched_subsidiary` are applied **during** the assignment
search, not after it — picking the highest-scoring assignment first and then testing the
constraint would reject a student who has a valid, lower-scoring one. (A student holding
Advanced Mathematics at D must not be failed just because Chemistry A + Biology A scored
higher and left it out.)

**"and" inside a subject name is not a conjunction.** *"Science and Practice of
Agriculture"* and *"Food and Human Nutrition"* are single subjects; the parser protects
those names before splitting a list, otherwise a choice-list reads as conjunctive and the
rule silently becomes stricter than the guidebook.

### Conditional eligibility

Anything left in `additional_requirements` is, by definition, not evaluated. The loader
splits it: advisory phrasing ("preference will be given to…") affects chances, not
eligibility; everything else becomes `unverified_conditions`, which makes a result
`conditional: true`. Clients must render that as **"you qualify *if* …"**, never a
plain yes.

Rules of the data:
- Unknown checklist values are `null` ("data not yet available") — **never invented**.
- Every programme carries a `source` (guidebook page) so claims are auditable.
- `additional_requirements` keeps conditions we can't evaluate from A-level input
  (O-level grades, fitness tests) visible instead of silently dropped.
