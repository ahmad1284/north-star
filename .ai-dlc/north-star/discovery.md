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
