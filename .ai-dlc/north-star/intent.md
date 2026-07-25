---
workflow: default
git:
  change_strategy: unit
  auto_merge: false
  auto_squash: false
announcements: []
status: active
epic: ""
---

# North Star — Course Eligibility Matcher (MVP)

## Problem
Tanzanian Form 6 graduates must choose what to apply for as a high-stakes, one-shot decision
made under social noise and low information. Many don't know which programs they are even
*eligible* for given their NECTA subject combination and grades, across university (TCU) and
vocational/technical (NACTVET) tracks. See `discovery.md` for full domain synthesis.

## Solution
A mobile-first web app where a student enters their NECTA subject combination and grades and
immediately sees a **small, ranked** set of programs — not a data dump — organized as
**"For you"** (eligible + a strong grade-based fit) and **"Discoveries"** (eligible programs
their strengths open up that they likely never considered). Each program shows the letter's
due-diligence checklist, with **HESLB loan availability/priority** treated as a first-class
factor. Eligibility and strength-scoring are computed by a **deterministic, explainable rules
engine** (expert-system style) running client-side over curated data — no AI, no server. Core
logic is channel-agnostic so a WhatsApp layer and an LLM+RAG chat layer can wrap it later.

See `discovery.md` for the three-lens model (Eligibility / Strengths / Interests) and the
anti-analysis-paralysis output rule.

Scope boundaries for THIS intent (MVP):
- IN: eligibility matching; **strength scoring derived from NECTA grades**; **"Discoveries"**
  (serendipitous strong-fit programs); **disciplined ranked output** (small sets, progressive
  disclosure — the anti-paralysis rule); per-program due-diligence checklist with **HESLB
  loan availability/priority** as a first-class dimension; explainable "why you qualify /
  why this fits" reasons; mobile-first web UI.
- OUT (deferred to the NEXT intent — the World of Work interests layer, which unlocks the
  "Bridge" for interests beyond a student's subjects): interests capture, interest-based
  "Bridge" recommendations, LLM+RAG chat, WhatsApp channel, CareerVillage-style Q&A,
  "still-in-school" (Newport) track.

## Success Criteria
- [ ] A student can enter a NECTA A-level subject combination and grades in a simple mobile UI.
- [ ] The app computes eligibility from curated seed data covering at least the common
      combinations (PCB, PCM, EGM, HGE, …).
- [ ] The app derives a **strength score** per program from the student's NECTA grades
      (e.g. grades in subjects the program values), used for ranking — not just pass/fail.
- [ ] Results are presented as a **small ranked set**, split into **"For you"** and
      **"Discoveries"** (eligible strong-fit programs likely outside the student's radar),
      never a full undifferentiated dump (anti-paralysis rule).
- [ ] Each result explains WHY (which requirement was met) and WHY IT FITS (which strengths).
- [ ] Each program shows the letter's checklist fields (duration, cost, institutions offering
      it, indicative time-to-employment, indicative salary) and **HESLB loan
      availability/priority** — filled where data exists, clearly marked where it doesn't.
- [ ] The eligibility + scoring logic is separated from the UI (channel-agnostic core module)
      so it can be reused by a future WhatsApp/chat layer.
- [ ] Data (combinations, grade points, programs, requirements, HESLB flags) lives in
      structured files (JSON/YAML) so non-developers can update it and real TCU/NACTVET data
      can slot in.
- [ ] Runs with no backend server (static hosting / opens from a link) and works on a phone.
- [ ] All tests for the rules + scoring engine pass (decisions covered by unit tests).

## Open dependencies / risks
- Real eligibility rules require the **TCU undergraduate handbook** (PDF not yet uploaded) and
  **NECTA grading** details. MVP starts with a small hand-curated, clearly-labeled seed dataset
  and a schema built to absorb the official data later.
- Salary / time-to-employment / loan-% data is sparse locally — shown as "indicative" and
  clearly sourced, never invented.

## Units
- unit-01 — Data schema + seed dataset (combinations, grade points, programs, requirements,
  strength-weighting per program, HESLB flags)
- unit-02 — Eligibility + strength-scoring engine (channel-agnostic core) + tests
- unit-03 — Ranking & output shaping ("For you" / "Discoveries", anti-paralysis small sets)
- unit-04 — Mobile-first web UI (input → explained, ranked results)
- unit-05 — Program detail view with the letter's checklist + HESLB dimension
