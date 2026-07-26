# Reflection — cycle 6 (constraint encoding) — the first cycle run with hats

## What happened
Ahmad, reading the API output, spotted that subject conditions like *"must pass in
Physics or Chemistry"* were sitting in `additional_requirements` as prose the engine never
evaluated. Verified as a real false-positive class: ARU AR026 reported a student with
Advanced Mathematics B + Geography B as **eligible, strength 0.80** when the guidebook
says otherwise. False positives are the worst error direction here — a student applies,
pays, and is rejected.

## Delivered
- `must_include` and `subsidiary_from` constraints: schema, load-time validation, engine
  enforcement, machine-readable reasons. `must_include` applied *during* assignment
  search so a valid lower-scoring assignment is never missed.
- **Three-state verdict**: `eligible` + `conditional` + `unverified_conditions`. Where a
  guidebook condition is outside A-level input (O-level, fitness, interview) the answer
  is now "you qualify **if** …" instead of a plain yes. Advisory phrasing ("preference
  will be given to") correctly does *not* make a result conditional.
- Extraction upgraded: new patterns, level-reference normalisation ("O - Level" /
  "O'level" / "A- level"), Basic Applied Mathematics added as a modelled subject.
  A-level conditions left in prose: **25 → 13 programmes**.
- Client shows a conditional badge and an explicit "we cannot verify this" block.
- 58 tests (was 48).

## The methodology finding — hats matter
Cycles 1–5 ran **Builder-only**: I planned implicitly, built, wrote tests, and ticked my
own criteria. This cycle ran planner → builder → **reviewer as a distinct pass**, and the
difference was immediate and measurable:

- The reviewer pass (verify each criterion *programmatically*, per the hat's SOP and its
  Chain-of-Verification rule) **caught a false negative I had just introduced**: I encoded
  *"must have a minimum of 'E' in either Chemistry or Geography"* as `must_include`, but
  that is a **holding** requirement, not an **assignment** requirement. Where the subject
  wasn't in the slot list the rule became unsatisfiable — DM015/DM080 rejected students
  with Chemistry A. Builder-me would have shipped it: the tests I had written all passed.
- It also forced me to distinguish a genuine defect from a flawed check: two apparent
  failures (AR009/AR014) turned out to be my verification harness downgrading the very
  subject the constraint needed. "Verify, don't assume" cuts both ways.

**The original bug is itself the argument.** A reviewer asking the goal-backward question
— *"what must be TRUE for eligibility to be correct?"* — would have enumerated "every
stated condition is either evaluated or the verdict is qualified" back in cycle 3, and
found prose conditions displayed but unenforced. Ahmad did the reviewer's job instead.

**Rule going forward: no unit ships without a reviewer pass that verifies criteria
programmatically, separately from the build.** Still not adopted: ephemeral state
(`iteration.json`), branch-per-unit, `/clear` bolt cycles — deliberate, given a single
short-lived session, but worth revisiting if this repo gets more contributors.

## Follow-up
Remaining prose constraints and their shapes are catalogued in `RESEARCH.md` (R1b).
