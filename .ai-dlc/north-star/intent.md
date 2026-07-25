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

# North Star — Course Eligibility Matcher (MVP: backend-first)

## Problem
Tanzanian Form 6 graduates must choose what to apply for as a high-stakes, one-shot decision
made under social noise and low information. Many don't know which programs they are even
*eligible* for given their NECTA subject combination and grades, across university (TCU) and
vocational/technical (NACTVET) tracks. See `discovery.md` for full domain synthesis.

## Solution
A **headless backend** (the "expert system") that, given a student's NECTA subject combination
and grades, returns a **ranked, grouped** set of programmes — **"For you"**
(eligible + strong grade-based fit) and **"Discoveries"** (eligible programmes their strengths
open up that they likely never considered) — each with the letter's due-diligence checklist.
Eligibility and strength scoring are computed by a **deterministic, explainable rules engine**
over curated data. The backend is exercised via API calls + tests (fast dev loop, no UI to
babysit). Clients — a web/mobile UI and a Meta (WhatsApp) integration — come later as thin
layers over the same API; the core stays channel-agnostic.

See `discovery.md` for the three-lens model (Eligibility / Strengths / Interests), the
"rich but in style" presentation principle, and the backend-first architecture decision.

Scope boundaries for THIS intent (MVP = the backend):
- IN: the data model + seed dataset; the **eligibility + strength-scoring engine**;
  **"Discoveries"** (serendipitous strong-fit programmes); **ranked, grouped output** the UI
  can render richly; explainable "why you qualify / why this fits" reasons; a **backend API**
  that returns this as structured JSON; tests.
- OUT (deferred): any **UI**; **WhatsApp/Meta** integration; the World of Work **interests**
  layer and the interest-based **"Bridge"**; LLM+RAG chat; CareerVillage-style Q&A;
  "still-in-school" (Newport) track. Loan boards (ZHELB/HESLB) are explicitly **not modeled**.

## Success Criteria
- [ ] The API accepts a request with the student's NECTA subject combination and grades and
      returns structured JSON (single canonical grade→points scale; A-level year not required).
- [ ] The engine computes eligibility from curated seed data covering at least the common
      combinations (PCB, PCM, EGM, HGE, …), using the real TCU rule structure (defining
      subjects, min principal passes, min points, per-subject grade floors).
- [ ] The engine derives a **strength score** per programme from the student's NECTA grades
      (grades in the subjects the programme values), used for ranking — not just pass/fail.
- [ ] Output is **ranked and grouped** — **"For you"** and **"Discoveries"** (eligible
      strong-fit programmes likely outside the student's radar) — structured so a future client
      can present it richly ("rich, but in style"), not as a flat list.
- [ ] Each result carries machine-readable reasons: WHY eligible (which requirement was met)
      and WHY IT FITS (which strengths) — so any client can explain the recommendation.
- [ ] Each programme includes the letter's checklist fields (duration, cost, institutions
      offering it, indicative time-to-employment, indicative salary) — filled where data
      exists, clearly marked where it doesn't. (Loan boards are NOT modeled.)
- [ ] The engine is a pure, channel-agnostic core module, separate from the API/transport, so
      the same logic backs a future web UI and WhatsApp client.
- [ ] Data (combinations, grade points by year, programmes, requirements) lives in structured
      files (JSON/YAML) so non-developers can update it and more TCU/NACTVET data can slot in.
- [ ] All tests for the rules + scoring engine pass (decisions covered by unit tests); the API
      is runnable locally and callable (e.g. via curl) without any UI.

## Open dependencies / risks
- **TCU handbook acquired:** `inputs/tcu-undergraduate-admission-guidebook-2026-2027.pdf`
  (376pp) gives the real rule format (grade→points by year cohort; general vs health entry;
  per-programme "defining subjects", points, grade floors, capacity, duration). See
  `discovery.md`. Seed dataset can now be transcribed from real data rather than invented.
  Transcribing all programmes is large — MVP seeds a representative subset (incl. Zanzibar
  institutions) with the schema built to absorb the rest.
- **NACTVET** (vocational) data still to source.
- Salary / time-to-employment / loan-% data is sparse locally — shown as "indicative" and
  clearly sourced, never invented.

## Units
- unit-01 — Data schema + seed dataset (combinations; single canonical grade→points scale; programmes
  with defining subjects, min passes, min points, grade floors, capacity, duration; per-
  programme strength weighting; checklist fields)
- unit-02 — Eligibility + strength-scoring engine (pure, channel-agnostic core) + tests
- unit-03 — Ranking & output shaping ("For you" / "Discoveries") as structured JSON
- unit-04 — Backend API exposing the engine (request → grouped, ranked JSON; runnable + curl-able)

Deferred to later intents (clients & layers): web/mobile UI · WhatsApp/Meta integration ·
World of Work interests + "Bridge" · LLM+RAG chat · CareerVillage-style Q&A.
