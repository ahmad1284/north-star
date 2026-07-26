# REVIEW COMPLETE — cycle 7 (delegated, 4 agents)

**Decision:** REQUEST CHANGES → **all blocking findings fixed and re-verified**
**Unit:** finish-engine-and-ship (16 files changed → SOP requires delegation)
**Criteria:** 8/10 satisfied, 2 explicitly partial (prose count 5 not 4; image build unverified)
**Tests:** 89/89 passing (was 63)
**Findings:** 4 High · 9 Medium · 9 Low
**Anti-patterns:** none (no TODO/FIXME, stubs, debug prints, or bare excepts)
**Gate integrity:** PASS — test functions rose monotonically 24→30→31→37→43→45→48→58→63→89
across all seven cycles; no gate ever removed or weakened, no intent criteria deleted
(the two unmet ones were marked `[~]`, not dropped).

## Why this pass happened
Cycles 1–6 were reviewed by me alone. The Reviewer SOP requires delegation at 3+ modified
files; cycle 7 touched 16 and was the highest-risk diff in the project (engine semantics +
deploy config). Four agents ran in parallel: Correctness, Test Quality, Security,
Deployment Safety.

## High-confidence findings — all fixed

| # | Agent | Finding | Fix |
|---|---|---|---|
| 1 | Correctness | **Live false positive on ZU024.** *"A minimum of D grades in Chemistry and Biology"* parsed as a CHOICE, so a student with Biology at E was told they qualified. | Conjunctive detection extracted into one shared `list_semantics()` used by **both** parser branches — the cycle-7 fix had been applied to one branch only. Regression test on real data. |
| 2 | Security | **Unauthenticated CPU DoS.** 27 subjects → 296 ms/request; 20 connections (~2 KB/s) degraded a real student 340×, and could trip the healthcheck into a restart loop. | `MAX_SUBJECTS = 8`. Measured: 27 subjects now rejected in 2.2 ms; worst legitimate case 29 ms. |
| 3 | Security | **No body-size limit.** 300 MB body → 616 MB RSS → OOM on a 256/512 MB tier from ONE request. | 64 KB `Content-Length` guard middleware. Measured: 2 MB → 413 in 2 ms. |
| 4 | Test Quality | **Parser had zero tests** — 702 lines deciding 332 programmes' rules. All 4 parser mutations survived the suite, and CI never re-runs extraction. | New `tests/test_parser.py` (17 tests) covering name protection, and/or semantics, choice markers, multi-clause floors, conditional rules, O-level escapes. |

## Medium — fixed
- **Real-data anchors missing**: stripping every `subsidiary_all`/`if_not_matched` constraint from the live knowledge base left 63/63 green. Added ZU024, AR031, DM006 anchors (DM006 is the only multi-trigger case in the corpus).
- **Loader validation untested** — both new checks were deletable with the suite green. Added two tests.
- **`min_grade` dead on both new kinds**; **`_holds` accepted grade F**. Both now tested.
- **`test_unencodable_conditions` under-asserted** its own docstring (passed with 4 of 5 programmes deleted). Tightened to exact-set + "never silently enforced".
- Security: gzip (335 KB → **18 KB** on the wire for a student), capped 422 echo, CI `permissions: contents: read`, healthcheck now probes `$PORT` with a timeout.
- Correctness: explicit choice markers now beat the separator; O-level guard made global (it protected 3 of 6 branches).

## Low — fixed
Deterministic tie-break in `_best_assignment` (same student, same explanation regardless
of key order); `\b` anchor on the O-level regex; generic 404 (no filesystem path leak);
client escapes all API-sourced strings (`innerHTML` safety previously rested on the source
PDF happening to contain no angle brackets); `idna` 3.11→3.18; `.dockerignore` secret
patterns; `norm()` now canonicalises `O-LEVEL`.

## Accepted, not fixed
- **`/docs` and `/openapi.json` public** — deliberate; the API is read-only reference data.
- **`requirements.txt` is a name-allowlisted freeze, not a hash-locked file** — three
  transitive deps still float. Documented in the file; a real deployment should use
  `pip-compile --generate-hashes`.
- **Correctness #2** (failure path lists non-blocking constraints as failed) — latent: no
  served programme carries ≥2 assignment-kind constraints. Logged in RESEARCH.md.
- **Base image / actions on mutable tags** — first-party only; digest pinning deferred.

## What this pass proves about the methodology
The delegated review found a **live student-facing false positive** and **two remotely
triggerable HIGH security issues** that my solo reviews across six cycles did not. The
mutation testing was the sharpest instrument: 23 mutations, **16 survived** — meaning most
of what I called "tests" for the new code could not have failed. Cycle 6's lesson was
"separate the reviewer from the builder"; cycle 7's is "one reviewer is not a review".
