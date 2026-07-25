# Reflection — cycle 7 (finish the engine, then ship)

## Delivered
**Part A — engine finished.** A-level conditions left in prose: **13 → 5**, and all five
are unencodable for stated reasons (3 sentences truncated by the PDF; 2 offering an
O-level alternative we cannot see). Two new constraint kinds — `subsidiary_all`
(conjunctive) and `if_not_matched_subsidiary` (conditional, evaluated *during* assignment
search) — plus multi-clause grade-floor decomposition. Reviewer swept the whole knowledge
base in both directions: **0 false positives, 0 false negatives**. 63 tests (was 58).

**Part B — shippable.** Dockerfile (non-root, `$PORT`, healthcheck that fails when the
knowledge base doesn't load), pinned `requirements.txt` from actually-installed versions,
CI running the suite *and* separately re-validating the knowledge base.

## Learnings
- **"and" is ambiguous in this domain.** *"Science and Practice of Agriculture"* is one
  subject; *"Physics and Mathematics"* is two. Splitting on "and" before protecting known
  multi-word names made a choice-list read as conjunctive — silently *stricter* than the
  guidebook. Fixing it also unlocked 6 more programmes (326 → 332 accepted).
- **A guard that works by accident is a bug waiting.** DM041 says "ordinary level", which
  the `o-level` guard didn't match; it stayed unencoded only because its subject list
  failed to parse. Made the O-level escape-clause guard explicit rather than lucky.
- **Verify the runtime contract even when you can't verify the artifact.** No Docker
  daemon in this environment, so the image build is **unverified** — but the container's
  exact CMD, env and healthcheck were run directly and pass. Said so plainly rather than
  ticking the criterion.

## Honest status
- Criterion "A-level constraints drop to 4" → **5**, each unencodable for a documented
  reason. Recorded as met-in-substance with the number stated, not rounded down.
- Criterion "Dockerfile builds" → **unverified** (no daemon). Everything it depends on is
  verified. Needs one `docker build` on a machine with Docker before trusting it.

## Next
The engine and the shipping path are done. What stands between this and a student is no
longer code: it is **R1** (course descriptions, fees) and **R4** (sit with real students).
Two research agents were dispatched during this cycle for R1 and R3 (NACTVET).
