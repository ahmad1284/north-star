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

# North Star — Interests layer + Bridge (cycle 2, backend-first)

## Problem
The MVP answers "what CAN I do?" (eligibility × strengths). It cannot yet answer
"what do I WANT?" — and, critically, "what if what I want lies outside what I studied?"
(Ahmad's bridge-the-gap requirement, deferred from cycle 1.)

## Solution
Add the third lens using the **ACT World of Work Map as-is** (no invented taxonomy):
four primary work interests — **Ideas · People · Data · Things** — which the map arranges
into regions/job families. Programmes get mapped to work areas via their existing tags.
The student may optionally send interests with their grades; the backend then:
- annotates eligible results that align with stated interests (why it fits *you*);
- adds a **"bridge"** group: programmes matching the student's interests that they are
  NOT eligible for, each carrying the engine's machine-readable reasons for what is
  missing — an honest "here's what it would take".
Interests are optional: without them, /match behaves exactly as before (no breaking change).

## Success Criteria
- [x] Interest areas (Ideas/People/Data/Things) defined in data, sourced from the ACT map
- [x] Every programme resolvable to ≥1 interest area via a tag→area mapping (validated at load)
- [x] POST /match accepts optional `interests`; omitting it preserves current behaviour
- [x] Results aligned with stated interests carry an interest_match annotation
- [x] New `bridge` group: interest-matched but ineligible programmes with failed-rule reasons
- [x] Tests: persona whose interests lie outside their combination sees a non-empty bridge
      with explanations; no-interests requests are byte-compatible with cycle-1 behaviour
- [x] All tests pass

## Units
- unit-01 — Interests data (areas + tag→area mapping) + loader validation
- unit-02 — Ranking/API extension (interest annotations + bridge group) + tests
