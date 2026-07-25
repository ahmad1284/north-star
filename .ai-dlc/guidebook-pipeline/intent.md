---
workflow: default
git:
  change_strategy: unit
  auto_merge: false
  auto_squash: false
announcements: []
status: completed
epic: ""
---

# North Star — Guidebook extraction pipeline (cycle 3)

## Problem
The knowledge base holds 30 hand-transcribed programmes out of hundreds in the TCU 2026/27
guidebook. Hand transcription doesn't scale, and thin data reads to a student as
"there are no options for me" (cycle-1 learning).

## Solution
A repeatable extraction script that parses the guidebook PDF into structured programme
records: institution, name, code, requirement text, min points, capacity, duration —
then pattern-parses the requirement text into engine slots for the common rule shapes.
**Confidence gating:** only cleanly parsed rules are auto-accepted (marked
`machine_parsed: true`, curated entries always win on conflict); anything ambiguous goes
to a review file and is NOT served. Never silently guessed.

## Success Criteria
- [x] Script extracts programme rows from the full PDF with per-page source references
- [x] Requirement parser covers the common shapes (N passes from list; required subject +
      list; per-subject grade floors; best-three points basis)
- [x] Auto-accepted entries load alongside curated data (curated wins on code conflict);
      every loaded entry still resolves to ≥1 interest area
- [x] Ambiguous entries land in a review file with their raw text — excluded from serving
- [x] Extraction stats reported honestly (accepted vs needs-review)
- [x] Whole test suite passes with the enlarged dataset

## Units
- unit-01 — PDF row extraction + requirement-text parser + review gating (script)
- unit-02 — Loader integration (merged dataset, provenance flags) + tests
