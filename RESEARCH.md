# North Star — research agenda

The code is at a natural stopping point: the engine, the knowledge base, the API and a
reference client all work and are test-covered. **What remains is mostly not
programming — it is research**: finding facts that exist in the world but not in any
machine-readable file, and checking whether the tool actually helps a real student.

This file is the handover. Each item states *why it matters*, *what is blocking it*,
*how to attack it*, and *how we'd know it's done*.

---

## Where the data actually stands

Numbers as of the last extraction run — regenerate with
`cd backend && python3 scripts/extract_guidebook.py`.

| | Count |
|---|---|
| Programmes served | **356** across **39** institutions |
| — human-curated (verified against the guidebook by hand) | 30 |
| — machine-extracted (flagged `machine_parsed`) | 326 |
| Guidebook rows found in total | 666 |
| Rows quarantined, never served (`data/extraction_review.json`) | **311** |
| Programmes missing a plain-language description (`what_is_it`) | 326 |
| Programmes missing cost / time-to-employment / salary / insider notes | **356 (all)** |

The last row is the important one. The tool currently answers *"can I get in?"* very
well and *"what is this course actually like?"* not at all.

---

## R1 — The letter's questions (highest value)

The letter asks: *How long is it? What does it cost? How long until I'm employed? What
does it pay? What do people already in it say?* Every one of these fields is empty for
every programme. Duration and capacity come from the guidebook; the rest does not exist
in any single document.

**Blocking:** no machine-readable national source. Fees live on individual university
websites and change yearly; salary and time-to-employment data for Tanzania is sparse
and unevenly reliable; insider experience is by definition not in a document.

**How to attack, cheapest first:**
1. **Fees** — start with the largest institutions by capacity (UDSM, UDOM, SUZA, MUHAS,
   SUA, IFM, Mzumbe). Fee schedules are usually published PDFs; a per-institution
   scraper is plausible but they are not standardised, so hand-entry of the top ~40
   programmes may beat automation.
2. **Employment and pay** — look for NBS (National Bureau of Statistics) labour force
   surveys, TCU tracer studies, and sector wage data. Treat any figure as *indicative*,
   record its source and year in the field, and never present a single number as fact.
3. **Insider notes** — the letter's own method: ask students currently in the course.
   Even 2–3 sentences per popular programme would transform the cards. This is where a
   CareerVillage-style Q&A layer eventually belongs (see R7).

**Done when:** the top ~40 programmes by admission capacity have at least `what_is_it`
and `cost` populated with a cited source, and the UI stops showing "—" for the courses
most students actually consider.

**Rule to keep:** if we can't source it, it stays `null`. A wrong fee is worse than a
blank one — a student may choose a life path on it.

---

## R1b — Finish encoding the constraints still in prose

Cycle 6 moved cross-slot conditions out of prose and into enforced data
(`must_include`, `subsidiary_from`), fixing a false-positive class where students were
told they qualified when they did not. **13 programmes still carry an A-level condition
in prose** (down from 25). They now surface as `conditional: true`, so nobody is misled —
but they are not enforced. The remaining shapes:

| Shape | Example | Why it's still prose |
|---|---|---|
| Conjunctive subsidiary | *"subsidiary pass in Physics **and** Mathematics"* | Needs an ALL variant; encoding as a choice would be too permissive |
| Conditional rule | *"if one of the principal passes is not Advanced Mathematics, must have a subsidiary in it"* | Genuinely different logic: a rule that fires based on the assignment |
| Multi-subject floors | *"C in Chemistry **and** D in Biology **and** E in Physics"* | One sentence, several different floors |
| PDF-truncated | *"…subsidiary level pass in"* (sentence cut off) | Can't encode what isn't there — fix extraction first |

**Careful:** each new shape must ship with a test proving it rejects the right students
*and* accepts the right ones. The reviewer pass on cycle 6 caught a false negative where
a *holding* requirement was encoded as an *assignment* requirement — see
`data/README.md` for the distinction.

## R2 — Triage the 311 quarantined rows

`data/extraction_review.json` holds every guidebook row whose requirement text did not
parse cleanly. They are excluded from results, so students silently don't see them.

Breakdown of why:

| Reason | Rows | Notes |
|---|---|---|
| Requirement text didn't match a known pattern | 261 | Many are one-off phrasings; some are PDF text-order damage |
| No tags inferrable from the programme name | 37 | Keyword list in `extract_guidebook.py` needs widening |
| Missing institution or programme name | 13 | Table geometry edge cases |

**How to attack:** the 37 tag failures are the cheapest win (extend `TAG_KEYWORDS`). For
the 261, cluster them by their opening phrase and see which *new* requirement shapes
would unlock the most rows per pattern added — a handful of patterns likely covers most.
Anything genuinely ambiguous should be promoted by hand into `programmes.json` (curated
entries always win) rather than guessed at by the parser.

**Done when:** quarantine is under ~100 rows and every remaining one has a note saying
why it needs a human.

**Careful:** loosening the parser to accept more is exactly how a wrong eligibility rule
gets shipped. Every new pattern needs a test.

---

## R3 — NACTVET (the vocational track)

The original intent covered **both** university (TCU) and technical/vocational
(NACTVET) pathways. Only TCU shipped. This is a real gap in the product's promise, not
a nice-to-have: many Form 6 graduates are better served by a technical path, and the
tool currently behaves as if that world doesn't exist.

**Blocking:** no NACTVET admission document in hand. Needed: their equivalent of the TCU
guidebook (programmes, entry requirements, institutions).

**How to attack:** obtain the source, then assess whether its structure is close enough
to reuse `extract_guidebook.py` or needs its own parser. The data schema already
supports it — a NACTVET programme is just a programme with different tags. Add a
`sector`/`track` field so clients can distinguish university from vocational.

**Done when:** a student who doesn't qualify for a degree programme still sees real
options, rather than a short list and an implied dead end.

---

## R4 — Does this actually help a student? (validation)

Untested assumption: that a long, grouped, explained list is genuinely useful to an
anxious 19-year-old rather than overwhelming. We have design principles ("rich, but in
style") but zero evidence.

**How to attack:** the letter's method — sit with 5–10 real Form 6 graduates, watch them
use it without help, and note where they hesitate. Questions worth answering: Do they
understand "Discoveries"? Does the Bridge feel encouraging or discouraging? Do they trust
it? Do they read the reasons at all? Is the Swahili natural?

**Done when:** we have notes from real sessions and a short list of changes they imply.
This should probably happen **before** any further feature work — it may reorder
everything below.

---

## R5 — Is the interests model the right one?

We use the ACT World of Work Map's four primary interests (Ideas / People / Data /
Things) and map programme *tags* onto them (`data/interests.json`). Two open questions:

1. **Granularity** — the real map has 12 regions and ~26 job families. Four areas may be
   too coarse to produce a meaningful Bridge (currently a "Things" interest matches a
   very wide set).
2. **Fidelity** — our tag→area mapping is a judgement call, and machine-inferred tags on
   326 programmes were derived from programme *names*. Sampling their accuracy is a
   contained, worthwhile study.

Also unexamined: we never ask students what they enjoy in any richer way (a short
interest inventory), which is what the map is designed to sit behind.

---

## R6 — Ranking and discovery quality

Within groups we rank by admission points brought to a programme's defining subjects —
TCU's own currency. Open questions: should selectivity (capacity vs demand) or programme
prestige influence order? Are "Discoveries" actually surprising *and* plausible, or just
statistically off-path? Thresholds live in one place (`ranking.py`,
`DISCOVERY_MIN_STRENGTH` / `FOR_YOU_MIN_STRENGTH`) and are cheap to tune once R4 gives
real feedback.

---

## R7 — Channels and layers (deliberately deferred)

| Item | What it needs before any code |
|---|---|
| **WhatsApp** (Ahmad's preferred channel for this audience) | A Meta Business account, a phone number, API credentials. Also a design question: the current output is rich and visual; a chat channel needs a genuinely different, conversational presentation — that's a research task, not a port. |
| **LLM + RAG chat** | An API key and hosting decision. The design is settled: the engine stays the source of truth for eligibility, and the model only answers open questions grounded in retrieved documents. Never let a model decide eligibility. |
| **CareerVillage-style Q&A** | The real blocker is people, not code: recruiting students and professionals willing to answer. This is the natural home for R1's insider notes. |
| **Hosting** | Any box that runs `uvicorn`. Single process, no database. |

---

## R8 — Keeping it true over time

The guidebook is republished annually (ours is 2026/27) and admission rules change. Two
questions to settle before this is used for a real application cycle: how do we detect a
new edition and re-run extraction, and how do we show students the data's vintage so
nobody applies on stale rules? A visible "data from the 2026/27 guidebook" line in the
client is the minimum.

---

## A note on responsibility

This tool sits at a genuinely consequential moment in someone's life. Two commitments
worth keeping deliberately, because both are easy to erode one small change at a time:

- **Never present an unsourced number as fact.** Blank beats wrong.
- **Never narrow the picture on the student's behalf.** The letter's whole argument is
  that being told what to study by people who don't know is the problem. North Star
  should always be widening the field of view and handing back the decision.
