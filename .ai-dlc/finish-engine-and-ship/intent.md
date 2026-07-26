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

# North Star — Finish the engine, then ship it (cycle 7)

## Problem
Two blockers stand between the tool and a real student, in this order (Ahmad: *"finish
the engine first"*):

1. **Engine incomplete.** 13 programmes still carry A-level conditions the engine displays
   but cannot enforce. They surface as `conditional`, so nobody is misled — but the rule
   isn't checked.
2. **Nowhere to run it.** Operational-readiness review found no Dockerfile, no pinned
   dependencies, no CI. Today it only runs on a laptop; a student cannot reach a URL.

## Solution

### Part A — finish the engine
Encode the three remaining shapes; leave only what is genuinely unencodable.

| Shape | Programmes | Approach |
|---|---|---|
| Conjunctive subsidiary — *"subsidiary in Physics **and** Mathematics"* | AR031, AR033 | new `subsidiary_all` constraint |
| Conditional — *"if one of the principal passes is **not** Adv Maths, need a subsidiary in it"* | SJ016, DM004, DM006 | new `if_not_matched_subsidiary`, evaluated **during** assignment search so a student who can satisfy it by choosing a different valid assignment is not wrongly rejected |
| Multi-subject floors — *"C in Chemistry **and** D in Biology **and** E in Physics"* | RU007, DM002, ZU024 | decompose into several holding constraints with floors |
| Choice-list subsidiary | SU038 | map remaining subject variant |

**Deliberately NOT encoded (4):** AR003, AR026, DM045 — sentences truncated by the PDF, so
the rule literally isn't there to encode; JC007 — has an O-level escape clause we cannot
check. These stay `conditional`, which is the honest answer.

### Part B — ship it
Dockerfile, pinned dependencies, CI running the suite, and deployment documentation, so the
API + client can be hosted anywhere that runs a container.

## Success Criteria
- [x] `subsidiary_all` and `if_not_matched_subsidiary` in schema, validated at load, documented
- [x] `if_not_matched_subsidiary` is applied during assignment search (no false negatives
      when another valid assignment satisfies it)
- [x] Multi-floor sentences decompose correctly (RU007, DM002, ZU024 enforce their floors)
- [~] A-level constraints left in prose drops to **4** → **actually 5** (AR003, AR026,
      DM045 truncated by the PDF; JC007, DM041 have O-level escape clauses). Each is
      unencodable for a stated reason; number reported rather than rounded down.
- [x] No false positives: a student failing a newly-encoded rule is rejected with a reason
- [x] No false negatives: for every constraint, a student who satisfies it still passes
      (verified programmatically across the whole knowledge base)
- [x] Dockerfile builds and the container serves both API and client → **VERIFIED in
      cycle 8** on a real daemon (Docker 29.3.1). Built clean, ran, and checked: `/health`
      reports 362 programmes; all four routes return 200; `/../Dockerfile` still 404s;
      the process runs as uid 10001 (non-root); `POST /match` returns a full result
      (234 eligible) from inside the container; `.dockerignore` keeps `tests/`,
      `scripts/`, `inputs/`, `.git/` and `.ai-dlc/` out of the image (227 MB).
      `PORT=9999` is honoured and the HEALTHCHECK follows it — healthy on 9999 with
      nothing listening on 8000. Negative test: killing uvicorn inside the container
      flips it to `unhealthy`, so the check can actually fail.
- [x] Dependencies pinned; CI runs the test suite on push
- [x] Deployment documented in README
- [x] Whole suite passes

## Units
- unit-01 — New constraint kinds + engine evaluation + parser + tests
- unit-02 — Deployment: Dockerfile, pinned deps, CI, docs

## Review note (Reviewer hat, do not skip)
Verify programmatically, both directions. Cycle 6's reviewer caught a false negative from
confusing a *holding* requirement with an *assignment* requirement — the same trap exists in
`if_not_matched_subsidiary`. Sweep the entire knowledge base for both error directions.
