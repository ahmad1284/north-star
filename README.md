# 🌟 North Star

A tool to help **Tanzanian Form 6 graduates choose what to study** — not by telling
them the answer, but by showing them the real landscape of what they qualify for,
what their strengths open up, and what it would take to reach what they want.

> *"Ushauri wangu kwako, kuwa ni mtu ambaye unapenda kuuliza maswali."*
> — Ahmad Sadri, letter to Form 6 graduates (`inputs/letter-to-form-6-graduates.txt`)

The letter is the product spec. A student is told "study X, it has jobs; avoid Y" by
people who often don't know. The letter's answer is to **ask better questions and go
find out**. North Star operationalises that: every answer it gives is explained, every
fact is sourced, and anything it doesn't know it marks as unknown rather than inventing.

---

## What it does today

A student enters their **NECTA subject combination and grades**, and optionally what
kind of work draws them. They get back:

| Group | Meaning |
|---|---|
| **For you** | Eligible, strong grade fit, in areas their combination normally leads to |
| **Discoveries** | Eligible and a strong fit, but **outside** their obvious path — doors they never considered |
| **Bridge** | What they're drawn to but *don't* qualify for — with exactly what's missing |
| **Other eligible** | Everything else they qualify for; nothing is hidden |

Each programme carries: why they qualify (rule by rule), how strongly, the institution,
duration, capacity, the guidebook page it came from, and a provenance badge if the entry
was machine-extracted rather than human-verified.

**Knowledge base:** 362 programmes across 39 institutions (Zanzibar + mainland), from the
TCU 2026/27 Bachelor's Degree Admission Guidebook.

## Run it

```bash
cd backend
pip install -e ".[dev]"
pytest                                  # 101 tests
uvicorn northstar.api:app               # http://127.0.0.1:8000
```

- **http://127.0.0.1:8000/** — the tool (mobile-first, Swahili + English)
- **/barua** — Ahmad Sadri's letter, the founding document
- **/maswali** — the questions to carry to a campus visit
- **/dunia-ya-kazi** — the four work-interest areas explained
- **/docs** — interactive API documentation

No database, no build step, no API keys. One process.

## Deploy it

```bash
docker build -t northstar .
docker run -p 8000:8000 northstar        # API + client on :8000
```

One container, one process, no database, no secrets, no outbound calls at
runtime — so it runs on the cheapest tier of anything that takes a container
(Fly, Render, Railway, a $5 VPS). It listens on `$PORT` (default 8000), runs as
a non-root user, and its healthcheck fails if the knowledge base doesn't load —
a North Star serving zero programmes should look broken, not fine.

Dependencies are pinned in `backend/requirements.txt`; CI (`ci/github-workflow-tests.yml`,
see `ci/README.md` to activate) runs the suite and separately re-validates the knowledge base on every push, so
a corrupt rule file fails the build instead of reaching a student.

Before putting it in front of strangers, read the limitations below — the
engine is ready, the *course information* is not.

## Repository map

```
inputs/          Source material: the letter, the TCU guidebook PDF, reference links
backend/         The product: engine + API  (see backend/README.md for the API reference)
  northstar/
    data/        The knowledge base as editable JSON (see data/README.md for the schema)
    loader.py    Loads + validates the knowledge base; fails loudly on bad data
    engine.py    Eligibility + strength scoring — pure, no I/O, no framework
    ranking.py   Grouping into For you / Discoveries / Bridge / Other
    api.py       FastAPI transport (thin — no logic lives here)
  scripts/       extract_guidebook.py — PDF → structured programme data
  tests/         101 tests, including six student personas as regressions
web/             The client + guidance pages: barua (the letter), maswali (questions to
                 carry to a campus), dunia-ya-kazi (the four work areas). See web/README.md
RESEARCH.md      What's left: the open research questions and how to attack them
.ai-dlc/         How this was built: intents, discovery, reflections (AI-DLC method)
```

## Architecture in one paragraph

The core is a **deterministic expert system**, not AI: TCU's published admission rules
encoded as data (`slots`: which subjects, how many, what grade floors, how many points),
evaluated by pure functions that produce a verdict *plus machine-readable reasons*. This
was a deliberate choice — eligibility must be correct, explainable, and free to run, and
an LLM cannot promise any of those. The engine knows nothing about HTTP; `api.py` is a
thin transport over it, and clients (`web/`, and one day WhatsApp) are thin layers over
the API. That layering is why the web client was added in a single commit without
touching the engine.

## Principles that shaped it (don't undo these by accident)

1. **Never invent data.** Unknown fields are `null` and shown as unknown. A machine-parsed
   rule is flagged as such. Anything the extractor couldn't parse cleanly is quarantined
   in `data/extraction_review.json` and **never served**.
2. **Always explain.** Every result carries the rules it passed or failed. A student
   should be able to check our reasoning against the guidebook.
3. **Read rules in the student's favour.** Where subjects can be assigned to requirement
   slots in several ways, the engine picks the best one for the student.
4. **Widen the horizon, in style.** Show the full landscape (Ahmad: *"it's ok to
   overwhelm, just do it in style"*) — but grouped, ranked, and progressively disclosed.
5. **Rank in TCU's own currency.** Ordering uses the admission points a student brings to
   a programme's defining subjects — not an invented score.
6. **What the engine can't compute, hand back to the student.** An unknown fact is not a
   broken field; it is the thing they must go and ask. Say so, and say who to ask.

## Where the project stands

- **The engine is finished.** Every requirement shape the guidebook uses is now enforced
  data, not prose: subject slots, grade floors, points thresholds, and cross-slot
  constraints (`must_include`, `subsidiary_from`, `subsidiary_all`,
  `if_not_matched_subsidiary`). Swept in both error directions; audited by four
  independent review agents (see `.ai-dlc/finish-engine-and-ship/review.md`).
- **It ships.** Dockerfile, pinned dependencies, CI, healthcheck.
- **Five conditions remain unencodable** — three sentences the PDF truncated mid-clause,
  two offering an O-level alternative we can't see. They surface as `conditional`
  ("you qualify *if* …"), never as a plain yes.
- **The course information is not a gap we try to fill.** Cost, time-to-employment,
  salary and insider notes are unknown for almost every programme, and none of them exist
  in any document we can parse. Rather than invent them or wait on a data-collection
  project that never finishes, the tool **says so and tells the student how to find out** —
  `/maswali` turns the letter's checklist into questions they carry to a campus. That is
  the letter's own method, and it needs no data we don't have.

**Honest readiness call:** ready for a student *with you sitting beside them* (that's
R4 — validation). It answers "can I get in?" itself, and for "should I go?" it does what
the letter does: hands the student the questions and points them at the people who can
answer.

## Picking this up later

Read in this order: this file → `RESEARCH.md` (what's next and why) →
`.ai-dlc/north-star/discovery.md` (the full domain analysis behind every decision) →
`backend/README.md` (API reference). The `.ai-dlc/*/intent.md` files record what each
build cycle committed to and what it deliberately left out.
