---
status: completed
depends_on: []
branch: claude/tanzania-career-guidance-murut8
discipline: backend
workflow: ""
ticket: ""
---

# Unit 01: Data schema + seed dataset

## Description
Define the structured data files (JSON) for subjects, combinations, the canonical grade→points
scale, and programmes (defining subjects, min principal passes, min total points, per-subject
grade floors, institutions, duration, checklist fields, strength weights). Transcribe a
representative subset of REAL programmes from the TCU 2026/27 guidebook
(`inputs/tcu-undergraduate-admission-guidebook-2026-2027.pdf`) covering health + non-health
rules, common combinations (PCB, PCM, EGM, HGE, HKL), and Zanzibar + mainland institutions.

## Success Criteria
- [x] JSON data files with a documented schema (README in data dir)
- [x] Canonical grade scale A=5 B=4 C=3 D=2 E=1 S=0.5 (F=0, fail)
- [x] ≥20 real programmes spanning every rule shape (defining-subjects points rule,
      per-subject grade floors, health harmonised rules)
- [x] Checklist fields present per programme; unknown values explicitly marked, never invented
- [x] Data loads and validates via a loader module with clear errors
