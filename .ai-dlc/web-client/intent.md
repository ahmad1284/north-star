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

# North Star — Thin web client (cycle 4)

## Problem
The backend answers well but only speaks JSON. Students can't touch it; Ahmad can't put it
in front of real Form 6 graduates for feedback (the letter's own method: go talk to people).

## Solution
A single static, mobile-first HTML page served BY the backend itself (same origin — no CORS,
no build tooling, no framework: the thinnest possible client, per backend-first).
Vanilla HTML/CSS/JS calling the existing endpoints:
- combination quick-picks (PCB, PCM, …) + per-subject grade choices + optional extra subjects
- optional interests (Ideas / People / Data / Things)
- results rendered "rich, but in style": grouped (For you / Discoveries / Bridge / Other),
  ranked, collapsible detail cards with WHY-reasons, checklist, source, and a provenance
  badge on machine-parsed entries ("auto-extracted — confirm with the institution")

## Success Criteria
- [x] GET / serves the client from the API server; works on a phone-sized screen
- [x] Student flow: pick combination -> grades -> (interests) -> results, no page reload
- [x] Groups shown with counts; long groups truncated with "show all" (style discipline)
- [x] Each card shows eligibility reasons, strength, checklist fields, source, provenance
- [x] Bridge group appears when interests are sent
- [x] Tests cover the route serving the client
- [x] Whole suite passes

## Units
- unit-01 — Static client page (HTML/CSS/JS) + FastAPI route + tests
