---
workflow: default
git:
  change_strategy: intent
  auto_merge: false
  auto_squash: false
announcements: []
status: in_progress
epic: ""
quality_gates:
  - "cd backend && python -m pytest -q"
---

# Transcribe the guidebook completely, and prove it (cycle 9)

## Problem
`extract_guidebook.py` does two jobs at once: it **transcribes** the guidebook's tables and
it **interprets** requirement prose into rules. Conflating them hid a serious defect.

Its row detector keys on `CODE_RE = ^[A-Z]{2,4}\d{3}$`. Codes shaped `CBD01`, `SUM01`,
`CBMZ1` don't match, so `extract_rows()` hits `if not code_words: continue` and abandons the
whole page **without recording anything**. Result: 190 programme codes that are not served,
not quarantined, and not logged. Entire institutions missing — all four College of Business
Education campuses, Dar es Salaam Maritime Institute, SUMAIT, Aga Khan.

The quarantine (`extraction_review.json`, 305 rows) exists precisely so gaps stay visible.
These bypassed it. **The corpus looked healthy because the thing measuring its health was
downstream of the thing that failed.**

Ahmad: *"lets extract the pdf fully to a readable thing, whether thats a csv or json."*

## Solution
Split transcription from interpretation. Add a **transcription pass** whose only job is to
reproduce every table row in the guidebook, verbatim, into CSV and JSON — no parsing, no
judgement, no dropping. Interpretation keeps living in the existing pipeline and can later
consume this artifact instead of re-reading the PDF.

### The oracle — why this can be *proved*, not just asserted
Every institution's table numbers its rows in an **S/N column** (`1.`, `2.`, `3.` …). That
count is **independent of the code regex** — it comes from a different column entirely. So:

- detect rows by **S/N**, not by code shape;
- for each institution, assert the S/N run is contiguous `1..N`;
- any missing number is a **named, located, countable** defect rather than silence.

That is the difference between "we extracted a lot" and "we extracted all of it".

### Approaches considered (rule-filtered)
| | Follows existing patterns | New deps | Separates concerns | Independent oracle |
|---|---|---|---|---|
| **A** patch `CODE_RE` + back-stop | yes | none | no | **no** |
| **B** dedicated transcription pass | yes | none | **yes** | **yes** |
| **C** camelot / tabula | no | heavy (ghostscript / Java) | yes | no |

**B selected.** A leaves transcription and interpretation fused and still has no way to
prove completeness — it would fix these 190 and not the next class. C adds heavy runtime
dependencies against a project rule of no unnecessary dependencies. B is also what was
actually asked for: a readable full dump is a deliverable in its own right.

## Success Criteria
- [ ] Every page in the programme-table range is classified: has a table (with row count) or
      does not (with a stated reason). No page is unaccounted for.
- [ ] Rows are detected by **S/N**, never by code shape
- [ ] Per-institution S/N contiguity is checked; every gap is reported with page + institution
- [ ] Output is both **CSV** (openable in Excel/Sheets) and **JSON**, one row per programme,
      all columns verbatim — no interpretation, no normalisation that loses information
- [ ] A coverage report is emitted as a committed artifact, listing totals, per-institution
      counts, and every anomaly
- [ ] **Nothing is ever silently dropped**: a row that cannot be read cleanly is emitted with
      the problem recorded on it
- [ ] Transcribed programme count materially exceeds the current 362 + 305, and the 190
      known-invisible codes are all present
- [ ] Every code in the prior-art catalog (146 rows, independent extraction) is accounted for
- [ ] Tests cover the transcriber; whole suite passes

## Units
- unit-01 — Transcriber + coverage audit + CSV/JSON output
- unit-02 — Tests, including the prior-art catalog as a coverage fixture

## Review note (Reviewer hat)
The failure mode being fixed is *silence*. The review must therefore attack the new
completeness claim, not the happy path: does the S/N oracle itself have a blind spot (tables
with no S/N column, institutions split across pages, restarting numbering)? A transcriber
that is confidently wrong about its own coverage is worse than the one it replaces.
