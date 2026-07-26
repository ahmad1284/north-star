# North Star knowledge base

Structured data the expert system reasons over. Editable by non-developers;
the loader validates everything at startup and fails loudly on mistakes.

| File | Contents |
|---|---|
| `grading.json` | Canonical NECTA A-level grade→points scale (A=5 … S=0.5, F=0). Principal pass = E or above. |
| `subjects.json` | Subject registry. `id` values are the only identifiers used elsewhere. |
| `combinations.json` | Common A-level combinations (PCB, PCM, …) with `obvious_tags` — the programme areas such students are typically steered toward. Used to separate "For you" from "Discoveries". |
| `programmes.json` | Curated, human-verified programmes. Always win over machine-parsed on code conflict. |
| `programmes_extracted.json` | Machine-parsed rules derived from the transcription. Badged `machine_parsed`. |
| `extraction_review.json` | Quarantine: rows whose requirements did not parse cleanly. **Never served.** |
| `guidebook_programmes.csv` / `.json` | **Full verbatim transcription** of every programme table in the guidebook — 870 rows, 94 institutions. Not rules; the guidebook's own words. |
| `guidebook_coverage.json` | The completeness audit for the above: every page classified, every anomaly named. |

## The transcription layer (`guidebook_*`)

`scripts/transcribe_guidebook.py` reproduces the guidebook's tables **verbatim** into CSV
and JSON. It does no interpretation — that stays in `extract_guidebook.py`. Splitting the
two is the point.

**Why it exists.** The extractor found rows by matching codes against
`^[A-Z]{2,4}\d{3}$`. Codes shaped `CBD01`, `SUM01`, `CBMZ1` never matched, so
`extract_rows()` hit `if not code_words: continue` and abandoned whole pages **in
silence** — 190 programmes neither served, nor quarantined, nor logged. The corpus looked
healthy because the thing measuring its health sat downstream of the thing that failed.

Two rules follow, and both matter more than tidy output:

1. **Rows come from the PDF's own ruled cells** (`page.find_tables()`), not from guesses
   about column positions or code shape. The structure was already in the file; inferring
   it was the mistake.
2. **Nothing is ever dropped in silence.** Every page is classified, every table is
   classified, and a row that cannot be read cleanly is emitted with its problem attached.

**How completeness is proved.** Each institution numbers its rows in an S/N column — a
signal *independent* of how rows are found, so it catches a systematic detection failure
instead of agreeing with it. The audit separates two very different things: a number the
guidebook never printed (its gap) from a number it printed and we lack (**our** lost row).
Conflating them would either hide our bugs or invent ones we don't have. Current state:
**0 rows lost**; 9 findings, all guidebook numbering skips verified against the PDF text.

**Regenerate:**

```bash
cd backend && python scripts/transcribe_guidebook.py
```

The guidebook's real malformations are recorded as tests in `tests/test_transcription.py`
— `S/ N` split headers, 9-column grids with empty sub-divisions, stacked
`Minimum / Institutional / Admission / Points` labels, institution names split across
cells, and page 280, whose header omits the word "Programme" entirely and so hid an entire
institution. Treat those as a regression fence, not trivia.

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


## How the two passes fit together

```
guidebook PDF
   └─ transcribe_guidebook.py   →  guidebook_programmes.{csv,json}   (870 rows, verbatim)
        └─ extract_guidebook.py →  programmes_extracted.json          (509 served, rules)
                                →  extraction_review.json             (331 quarantined)
        programmes.json                                               (30 curated, wins)
```

**Transcription is proved complete; interpretation is allowed to refuse.** Those are
different jobs with different standards, which is why they are different scripts.
`extract_guidebook.py` no longer opens the PDF — re-deriving rows there would only add a
second way to be wrong.

Every transcribed row lands in exactly one bucket, and the three reconcile to 870. That
invariant is a test (`test_pipeline_output_reconciles_to_the_transcription`): a row in no
bucket has been lost in silence, which is the failure this pipeline was rebuilt to prevent.

**The refusal is deliberate.** Quarantining a programme costs a student an option they
might have had. Serving a mis-parsed rule tells them they qualify when they don't, and
they learn otherwise after applying. Those are not equally bad, so unclear rules are
refused.
