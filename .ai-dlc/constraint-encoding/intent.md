---
workflow: default
git:
  change_strategy: intent
  auto_merge: false
  auto_squash: false
announcements: []
status: completed
epic: ""
high_stakes: true
---

# North Star — Encode the constraints still living in prose (cycle 6)

## Problem
`additional_requirements` holds 141 guidebook sentences the engine **displays but never
evaluates**. Most are O-level conditions outside our input scope, but ~25 programmes carry
**A-level** constraints in that prose — e.g. ARU AR026: *"One of the two principal passes
must be in Physics or Chemistry or Biology."*

Consequence (verified, not theoretical): a student with Advanced Mathematics B + Geography B
is reported **eligible, strength 0.80** for AR026 when the guidebook says they are not.
False positives are the worst error direction here — a student applies, pays, is rejected.

Found by Ahmad reading the API output. A Reviewer-hat pass would have caught it; cycles 1–5
ran Builder-only. This cycle runs planner → builder → reviewer as distinct passes.

## Solution
Move enforceable conditions out of prose and into data the engine checks, and stop reporting
a flat "eligible" when unverifiable conditions remain:

1. **`must_include` constraint** — at least one matched subject must come from set X.
   Evaluated across the whole assignment (it is not a separate slot: the subject also
   counts toward the existing slots).
2. **`subsidiary_from` constraint** — requires a subsidiary (S) pass or better in one of a
   set. We already collect S grades, so this is checkable today.
3. **`conditional` verdict** — where genuinely uncheckable conditions remain (O-level
   grades, fitness tests, interviews), the result reports `conditional: true` plus the
   unverified conditions, so a client can say "you qualify **if** …" instead of "you qualify".
   `eligible` keeps its meaning for existing clients (no breaking change).
4. **Parser support** — extract these shapes into constraints instead of dropping them into
   `additional_requirements`; re-run extraction over the guidebook.

## Success Criteria
- [x] `must_include` and `subsidiary_from` constraints exist in the schema, are validated at
      load, and are documented in `data/README.md`
- [x] The engine evaluates them, and a failure produces a machine-readable reason
- [x] AR026 regression: Advanced Mathematics B + Geography B is **not** eligible
- [x] No false negatives introduced: a student who genuinely satisfies a constraint still
      passes (tested with the constraint's own subjects)
- [x] Results expose `conditional` + the unverified conditions; a programme with no
      unverifiable conditions reports `conditional: false`
- [~] Extraction parses these shapes into constraints; count of A-level constraints left
      unencoded in `additional_requirements` drops to ~0 (report the number honestly)
      → **PARTIAL: 25 → 13 programmes, not ~0.** The remaining four shapes (conjunctive
      subsidiary, "if not X then Y", multi-subject floor lists, PDF-truncated sentences)
      each need their own logic and tests. Not eligibility-unsafe: all 13 now surface as
      `conditional: true`, so students are warned rather than misled. Carried to
      RESEARCH.md R1b rather than silently ticked.
- [x] Web client distinguishes conditional from unconditional eligibility
- [x] Whole suite passes; persona regressions unchanged except where the fix is correct

## Units
- unit-01 — Constraint model + engine evaluation + conditional verdict (+ tests)
- unit-02 — Parser support, re-extraction, curated data backfill, client display (+ tests)

## Review note (Reviewer hat, do not skip)
Verify criterion-by-criterion **programmatically**, not by reading the diff. Specifically:
count the remaining unencoded A-level constraints from the live knowledge base, and prove
the AR026 case both ways (fails without Phy/Chem/Bio, passes with it).
