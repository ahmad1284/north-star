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
immediately sees the programs they qualify for — each shown with the letter's due-diligence
checklist (duration, cost, where offered, time-to-employment, salary, HESLB loan %, insider
notes). Eligibility is computed by a **deterministic, explainable rules engine** (expert-system
style) running client-side over curated data — no AI, no server. Core logic is kept
channel-agnostic so a WhatsApp layer and an LLM+RAG chat layer can wrap it later.

Scope boundaries for THIS intent (MVP):
- IN: eligibility matching, program results with the due-diligence checklist, explainable
  "why you qualify / why not" reasons, mobile-first web UI.
- OUT (deferred, tracked for later intents): World of Work interests explorer, LLM+RAG chat,
  WhatsApp channel, CareerVillage-style Q&A, "still-in-school" (Newport) track.

## Success Criteria
- [ ] A student can enter a NECTA A-level subject combination and grades in a simple mobile UI.
- [ ] The app returns the set of programs they are eligible for, from curated seed data
      covering at least the common combinations (PCB, PCM, EGM, HGE, …).
- [ ] Each result explains WHY the student qualifies (which rule/requirement was met).
- [ ] Each program shows the letter's checklist fields (duration, cost, institutions offering
      it, indicative time-to-employment, indicative salary, HESLB loan note) — filled where
      data exists, clearly marked where it doesn't.
- [ ] The eligibility logic is separated from the UI (channel-agnostic core module) so it can
      be reused by a future WhatsApp/chat layer.
- [ ] Data (combinations, grade points, programs, requirements) lives in structured files
      (JSON/YAML) so non-developers can update it and real TCU/NACTVET data can slot in.
- [ ] Runs with no backend server (static hosting / opens from a link) and works on a phone.
- [ ] All tests for the rules engine pass (eligibility decisions covered by unit tests).

## Open dependencies / risks
- Real eligibility rules require the **TCU undergraduate handbook** (PDF not yet uploaded) and
  **NECTA grading** details. MVP starts with a small hand-curated, clearly-labeled seed dataset
  and a schema built to absorb the official data later.
- Salary / time-to-employment / loan-% data is sparse locally — shown as "indicative" and
  clearly sourced, never invented.

## Units
- unit-01 — Data schema + seed dataset (combinations, grade points, programs, requirements)
- unit-02 — Eligibility rules engine (channel-agnostic core) + tests
- unit-03 — Mobile-first web UI (input → explained results)
- unit-04 — Program detail view with the letter's due-diligence checklist
