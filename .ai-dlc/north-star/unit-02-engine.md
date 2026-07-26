---
status: completed
depends_on: [unit-01-data-schema-seed]
branch: claude/tanzania-career-guidance-murut8
discipline: backend
workflow: ""
ticket: ""
---

# Unit 02: Eligibility + strength-scoring engine

## Description
Pure, channel-agnostic Python module: given a student profile (subjects + grades), evaluate
every programme's rules deterministically and produce per-programme results with
machine-readable reasons (why eligible / why not) and a strength score derived from the
student's grades in the subjects each programme values.

## Success Criteria
- [x] Pure functions, no I/O in the core; data injected
- [x] Eligibility verdict + reasons (rule-by-rule: passes, points, grade floors)
- [x] Strength score (0–1) from grades in programme's valued subjects, documented formula
- [x] Unit tests cover: eligible/ineligible on points, on passes, on grade floors,
      health rules (MD), subsidiary passes ignored, unknown subjects handled
- [x] All tests pass
