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

## Anti-analysis-paralysis principle (hard design rule)
Widening horizons (the letter's "exposure") must NOT overwhelm. The lever is disciplined
OUTPUT, not fewer inputs:
- Never dump the full eligible list. Show a small ranked set: a few "For you", 2–3
  "Discoveries", an optional "Stretch/Bridge".
- Progressive disclosure — details on demand, one clear primary action.
- Sensible defaults; full list only if explicitly requested.

## HESLB as a first-class dimension (not just a repayment %)
In Tanzania, HESLB loan **availability and priority** often decides whether a student can
afford a program at all. Treat per program:
- `loan_available` / priority tier (some programmes are prioritized for government loans),
- indicative coverage (full / partial),
- indicative repayment burden (% of salary) — shown as indicative, never invented.
Affordability is frequently the real constraint, so this can act as both an attribute and a
signal in ranking.

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

## Delivery channel (open decision)
- **WhatsApp** — lowest friction for the audience; but needs WhatsApp Business API, Meta
  approval, hosting, a number → real infra + cost + approval lead time.
- **Web app** — fastest to prototype/iterate, shareable by link, mobile-first; no approval gate.
- **Constraint (hard):** *simplify for the end user regardless of backend complexity.*
- Working recommendation: **build the core logic channel-agnostic; ship web first;
  wrap WhatsApp later.**

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
