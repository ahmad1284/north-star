---
workflow: default
git:
  change_strategy: intent
  auto_merge: false
  auto_squash: false
announcements: []
status: completed
epic: ""
---

# North Star — What the engine can't do, the student can (cycle 8)

## Problem
Seven cycles produced an excellent *eligibility* engine. It answers "can I get in?"
rigorously. It cannot answer the letter's other questions — what a course is really like,
what it costs, how long until work, what people already in it say — and the honest data
position is that **none of those live in any document we can parse**. Cost/salary/
time-to-employment are empty for all 362 programmes.

Treating that as a data-collection backlog has two problems: it never finishes, and it
misreads the source material. **Ahmad Sadri's letter does not answer those questions
either.** It tells the student to go and ask them.

## Solution (Ahmad's call)
> *"whatever the engine can't do, we leave the student to do it themselves"*

Stop trying to compute the un-computable. Express it as **guidance the student acts on**:

1. **`/barua` — the letter itself.** The founding document, in Swahili, as written. It is
   better than anything we would compose, and it is the reason this project exists.
2. **`/dunia-ya-kazi` — the World of Work article.** Explains Ideas / People / Data /
   Things so the interests picker means something instead of being four bare words.
3. **`/maswali` — the questions to carry.** The letter's checklist turned into something a
   student takes to a campus visit: what to ask, who to ask, why it matters.

And the key wiring: **an unknown checklist field becomes a call to action, not a gap.**
Where a card currently shows "—" for cost or salary, it links to the questions page —
*"Hatujui hili. Hivi ndivyo vya kuuliza."* That converts our biggest honest weakness into
the letter's own method.

## Why this is the right shape
- It needs **no data we don't have** and creates **no maintenance burden** — the letter
  will still be true in five years; a scraped fee will not.
- It is **more honest** than filling fields with numbers of unknown vintage.
- It makes the tool do what the letter asks: *widen the field of view and hand the
  decision back*.

## Success Criteria
- [x] Three content pages served, mobile-first, Swahili-first, self-contained (no external
      requests), consistent with the existing client's visual language
- [x] The letter is reproduced faithfully and attributed to Ahmad Sadri
- [x] The World of Work page explains all four interest areas and links back into the tool
- [x] The questions page is usable *at a campus* — screenshot/print friendly, no
      interaction needed
- [x] Results wire into it: unknown checklist fields link to the questions page rather
      than showing a bare "—"
- [x] Navigation exists between all pages and back to the tool
- [x] Routes added without introducing a static-file mount (the security review verified
      no path traversal is possible — keep that property)
- [x] Tests cover every route and the no-external-resources rule
- [x] Whole suite passes; client verified in a real browser at phone size

## Units
- unit-01 — Three content pages + routes + navigation
- unit-02 — Wire unknown checklist fields to the questions page; tests

## Review note (Reviewer hat)
Content pages are still attack surface and still user-facing text. Verify: no external
requests, no path traversal introduced, escaping intact, and that the Swahili reads
naturally to the audience rather than as translated English.
