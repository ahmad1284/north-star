# Reflection — cycle 8 (guidance pages)

## The idea, and why it matters
Ahmad: *"whatever the engine can't do, we leave the student to do it themselves."*

Seven cycles had been spent making the engine answer more. Cycle 8 accepted that some
questions are not ours to answer — and that the letter already knew this. Sadri never
tells anyone what to study; he tells them what to ask and to go ask it.

The reframe that made it work: **an unknown fact stopped being a gap and became the call
to action.** `cost: null` used to render "—", which reads as a broken feature. It now
renders *"hatujui — uliza"* linking to a page of questions to take to a campus. Same data,
opposite meaning: a failure became the letter's method.

## Delivered
- `/barua` — the letter, in Swahili as written, attributed
- `/maswali` — the checklist as questions a student carries: grouped by who to ask, each
  with *why* it matters, screenshot- and print-friendly, works with no connection
- `/dunia-ya-kazi` — the four ACT work areas explained with Tanzanian examples, so the
  interests picker means something instead of being four bare words
- Wiring: unknown checklist fields prompt instead of dashing; nav between all pages
- Routes declared explicitly, not a `StaticFiles` mount — preserves the no-traversal
  property the cycle-7 security review verified (tested)
- 101 tests (was 89); verified in Chromium at phone size, zero JS errors

## Learnings
- **The cheapest feature in the project may be the most valuable.** No data gathering, no
  maintenance burden, no infrastructure. The letter will still be true in five years; a
  scraped fee will not.
- **Content is a feature with the same review needs as code.** These pages are user-facing
  text and attack surface: they got route tests, a no-external-resources test, and a
  path-traversal test.
- **A doc pass caught real drift.** README claimed 48 tests / 356 programmes / a CI path
  that moved, and principle 1 ("unknown renders as —") now contradicted the product.
  Cheap to fix, misleading to leave.

## What this changes about the roadmap
R1 (gather cost/salary/insider data) is no longer a blocker for shipping — it is an
enhancement. The tool is now honest and useful without it. The researched fee proposals
in `inputs/research/checklist-proposals.json` remain worth merging, but nothing waits on
them. The next real question is still **R4: sit with students and watch.**
