---
status: completed
depends_on: [unit-02-engine]
branch: claude/tanzania-career-guidance-murut8
discipline: backend
workflow: ""
ticket: ""
---

# Unit 03: Ranking & output shaping ("For you" / "Discoveries")

## Description
Turn raw engine results into the grouped, ranked structure clients render: "For you"
(eligible + strong fit, aligned with the student's combination focus) and "Discoveries"
(eligible + strong fit, off the student's obvious path — serendipity). Explicit, tunable
heuristic; structured JSON-ready output with reasons carried through.

## Success Criteria
- [x] Documented, single-place tunable heuristic for discovery classification
- [x] Groups: for_you, discoveries, other_eligible (rich but organized — nothing hidden)
- [x] Ranked by strength within groups; ties stable
- [x] Tests: a PCB student gets health programmes in for_you and a non-obvious
      strong-fit programme in discoveries
- [x] All tests pass
