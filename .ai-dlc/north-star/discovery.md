# Discovery — North Star (career guidance for Tanzanian Form 6 graduates)

> AI-DLC Elaboration-phase domain notes. Synthesis of all inputs in `inputs/`.
> This is understanding, not committed scope. Scope lives in `intent.md` (to be written after key decisions).

## The user & the moment
A Tanzanian Form 6 graduate (Zanzibar/mainland), just finished A-levels with a subject
combination (PCB, PCM, EGM, HGE, …) and NECTA grades in hand. They must now choose what to
apply for — a high-stakes, low-information, one-shot decision made under social noise
("study X, it has jobs; avoid Y") from people who often don't actually know. Many literally
do not yet know what they want. Emotional state: pressure + uncertainty.

## The philosophy (from the letter, 80,000 Hours, Cal Newport, Al-Suwaidan)
The through-line across every input is **inquiry + exposure, not prescription**:
- **The letter (Ahmad Sadri):** don't be told the answer — *ask better questions* and go
  *talk to people already in the course*. It hands us a ready-made due-diligence checklist.
- **80,000 Hours, but local priorities:** evidence-based career thinking, re-grounded in
  Tanzanian realities (local job market, HESLB loans, local institutions) — not Western defaults.
- **Cal Newport:** *So Good They Can't Ignore You* (career capital / skills > passion) and
  *How to Be a High School Superstar* (a possible track for students *still in school*).
- **Dr. Tareq Al-Suwaidan:** career-choice advice (to be summarized).

Design implication: the tool should **widen and inform** the decision, not spit out one answer.

## The three jobs to be done
1. **ORIENT the lost student** — "I don't know what I want."
   → interests-first exploration. **World of Work Map (ACT)** is the perfect front door:
   4 interest areas (**Ideas / People / Data / Things**) → 12 regions → 25 job families.
   Turns "thousands of options" into a navigable few.
2. **MATCH & CHECK ELIGIBILITY** — "what can I actually apply for?"
   → given NECTA subject combination + grades, which programs is this student *eligible* for,
   across **university (TCU)** and **vocational/technical (NACTVET)** tracks. This is
   **deterministic, rule-based** logic — the natural home of an expert system.
3. **DUE-DILIGENCE each option** — "is this course right for me?"
   → answer the letter's checklist per program, grounded in official data + real voices.

## The three lenses (core conceptual model)
A student's best-fit options are the intersection of three lenses — the product's value is in
the OVERLAPS and GAPS, not any single lens:
- **Eligibility** — what TCU / NECTA / NACTVET rules permit.
- **Strengths / aptitude** — what the student is demonstrably good at. Inferable directly from
  their **NECTA subject grades** (e.g. strong Chemistry + Biology). A signal, not just a filter.
- **Interests** — what genuinely draws them (World of Work), *including interests beyond the
  subjects they studied*.

Regions that matter:
| Region | Meaning | Feature |
|--------|---------|---------|
| Eligible ∩ Strong ∩ Interested | confident best-fit | **"For you"** lead recommendations |
| Eligible ∩ Strong, low prior awareness | strength opens an unconsidered course | **"Discoveries"** (serendipity) |
| Interested but NOT eligible / outside combination | wants it but can't (yet) | **"Bridge"** — foundation programs, alt combinations, honest "what it'd take" |
| Eligible but neither strong nor interested | filler | **downranked / hidden** (anti-paralysis) |

## "Rich, but in style" — the presentation principle (updated)
Ahmad's steer: *"it's ok to overwhelm, just do it in style."* So the goal is NOT to hide
options — it's to make even a large, wide-horizon result set feel like exploration, not chaos.
The lever is PRESENTATION quality, not fewer options:
- It's fine to surface many eligible programmes AND discoveries AND stretches — provided the
  UI organizes them (grouped: "For you" / "Discoveries" / "Stretch–Bridge"), ranks them,
  and uses layering/progressive disclosure so the student is never hit with an undifferentiated
  wall of text.
- Beautiful, calm, well-structured density > artificial scarcity. Widen horizons (the letter's
  "exposure") with a presentation that carries the weight.

## Loan boards (ZHELB / HESLB) — OUT OF SCOPE for our logic
Decision (Ahmad): the government loan boards have **no input whatsoever** into this project.
They are just loan boards — ZHELB (Zanzibar) and HESLB (mainland) — with different mechanics,
but we do NOT model them, do NOT take region as an input for them, and do NOT use them as a
ranking or eligibility signal. Not a dimension. (Left here only as a note so we don't
re-introduce it.)

## TCU eligibility rule structure (from the 2026/27 handbook — now in `inputs/`)
Source: `inputs/tcu-undergraduate-admission-guidebook-2026-2027.pdf` (376pp, direct-entry /
Form Six pathway — our audience). A separate handbook covers Diploma/equivalent entry.
Rule model to encode:
- **Entry schemes:** direct entry (Form Six holders — our target) vs equivalent (diploma, etc.).
- **Grade → points map depends on the student's A-level YEAR cohort** (this is the NECTA
  grading input):
  - Before 2014 AND 2016-onwards: A=5, B=4, C=3, D=2, E=1, S=0.5
  - 2014–2015: A=5, B+=4, B=3, C=2, D=1, E=0.5
- **General minimum (non-health, Table 1):** two principal passes ('E' and above) totalling
  **≥ 4.0 points** in the **two subjects "defining admission"** to the specific programme.
- **Health/allied (harmonised, Table 2):** stricter per-programme rules, e.g. MD/MBBS = three
  principal passes in Physics, Chemistry, Biology, **≥ 6 points**, minimum **'D'** in each.
- Therefore each programme record needs: defining subject(s)/combinations, min principal
  passes, min total points, optional per-subject grade floors, plus capacity & duration
  (the handbook also lists programme capacities and durations per institution).
- Institutions include Zanzibar ones (e.g. SUMAIT, IPA Zanzibar) alongside mainland — good
  audience coverage.

## The letter's checklist = the per-program data model
For any course/program the student weighs:
- What *is* this course, really?  ·  Duration (years)  ·  Where offered (TCU unis + abroad;
  NACTVET institutions)  ·  Time from graduation → employment  ·  Typical salary  ·  % of
  salary going to HESLB loan repayment  ·  Cost to study  ·  What insiders say it's like.

## Data sources to ingest
- **TCU** undergraduate admission guidebook (eligibility rules, programs, combinations).
- **NECTA** A-level grading system (subject combinations, grade points).
- **NACTVET** — technical/vocational programs and pathways.
- **World of Work Map** — interest taxonomy for orientation.
- (Later) crowdsourced insider answers — **CareerVillage-style** ask-a-professional Q&A,
  which directly operationalizes the letter's "talk to people in the course."

## Architecture: BACKEND-FIRST (decided)
Decision (Ahmad): build the **backend first** for a fast dev cycle, then extend with clients.
- **MVP = a headless backend** housing the engine, exercised via API calls + tests (no UI to
  babysit → tight loop).
- **Then extend** with thin clients over the same API: a web/mobile UI, and/or a **Meta
  (WhatsApp)** integration. WhatsApp needs a server webhook anyway, so a backend is the shared
  foundation for both.
- Core stays **channel-agnostic**; channels are just clients.
- **Constraint (hard):** *simplify for the end user regardless of backend complexity.*
- Stack (to confirm at execution): lean toward one language end-to-end (e.g. TypeScript —
  shared types for a future web UI + easy JSON/Meta webhooks; Python also viable, esp. for
  data work + future RAG). Final call at start of Execution.

## Backend approach (open decision — user raised this explicitly)
Two philosophies the user named — best treated as **layers, not either/or**:
- **Rules-based expert system (AI-less)** — Kendall & Kendall *Systems Analysis & Design*.
  Ideal for the **eligibility/matching** core: accurate, explainable, cheap, no hallucination.
- **LLM + RAG** — Retrieval-Augmented Generation: ground an LLM in the TCU/NECTA/NACTVET
  documents so free-form questions ("what's MD actually like?") get local, factual answers.
  Best for the **conversational due-diligence** layer.
- Working recommendation: **deterministic core first (expert system), add LLM+RAG chat later.**

## Reference products
- **CareerVillage.org** — students post career questions, real professionals answer
  (near-peer / practitioner advice at scale). Model for the "insider voices" layer.
- **davetgc.com** — host of the World of Work Map resource.

## Audience scope (open decision)
- Primary: **Form 6 graduates choosing a course** (the core ask).
- Possible extension: **students still in school** (Newport "Superstar" track) — bigger
  audience, but a different job. Recommend deferring to keep MVP sharp.
