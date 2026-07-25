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

## R1b — Constraints in prose — ✅ DONE (cycle 7)

Cycles 6–7 moved every encodable cross-slot condition out of prose and into enforced
data. **25 → 5 programmes**, and the remaining five are unencodable for stated reasons,
not for want of effort:

| Programme | Why it cannot be encoded |
|---|---|
| AR003, AR026, DM045 | The PDF truncated the sentence mid-clause — the rule literally isn't in the document |
| JC007, DM041 | Offer an O-level alternative ("…or a D in ordinary level Mathematics"). We never see O-level results, so enforcing only the A-level half would reject students who satisfy the real rule |

All five surface as `conditional: true`. Constraint kinds now enforced: `must_include`,
`subsidiary_from` (with optional floor), `subsidiary_all`, `if_not_matched_subsidiary`.
Verified by sweeping the whole knowledge base in both error directions: **0 false
positives, 0 false negatives**.

**If you revisit this:** the O-level cases become encodable the day the tool collects
O-level grades — which would be a product decision (more typing for the student) as much
as an engineering one. The truncated ones need better PDF extraction first (R2).

## R1c — Two latent engine issues (not currently reachable)

Found by the cycle-7 delegated review, deliberately not fixed because neither can affect a
student today. Fix them before the conditions that make them latent change:

1. **The failure path lists non-blocking constraints as failed.** When no valid assignment
   exists, `engine.py` reports *every* `must_include` / `if_not_matched_subsidiary`
   constraint with `ok=False` without re-testing which one actually blocked — so a student
   could be told to go and get Geography when the real gap is Advanced Mathematics. That
   violates "always explain". **Latent because** no served programme carries two or more
   assignment-kind constraints. Fix: re-run `_best_assignment` with each constraint singly
   and report only those that admit no assignment.
2. **Bare "Mathematics" maps to Advanced Mathematics only.** Newly load-bearing now that
   AR031/AR033/AR035's constraints are enforced rather than prose: a student whose maths is
   *Basic Applied* Mathematics is rejected. Needs a deliberate decision, not a silent map.

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

**Source: FOUND** (researched 2026-07-25 — full assessment in
`inputs/research/nactvet-findings.md`). The 2026/27 guidebook is downloaded to
`inputs/nactvet-GUIDEBOOK_FOR_ALL_2026_2027.pdf` (200 pages, from nactvet.go.tz —
`nacte.go.tz` is the legacy domain for the same body). It has **real ruled tables**, so
extraction is *easier* than TCU: 415 institutions, 1,599 programmes, 2,406 entry routes.
No public API/CSV exists; the PDF is the source.

**The blocker moved — and it is now a product question, not an engineering one.**
NACTVET has no admission points (3 rows in 2,406 mention them), and 538 of the 718
A-level (ACSEE) routes require only *"one Principal Pass and one Subsidiary"*. Encoding
that is trivial with existing slot shapes. The consequence is the problem:

- **Every A-level passer qualifies for almost everything** → eligibility filtering
  discriminates nothing.
- **Ranking has no currency.** Our ordering is "admission points brought to the
  programme's defining subjects". Neither exists here. Inventing a merit-looking score
  would breach principle 5 harder than leaving the list unranked.
- **For you / Discoveries / Bridge collapse** — Bridge would be empty (nobody fails to
  qualify), Discoveries would be ~1,000 items of noise.

**Two findings beyond the brief:**
1. **The NACTVET guidebook contains official tuition fees** — 1,558 fee strings covering
   94% of programmes, all in a clean `TSH. N,NNN,NNN/=` format. R1 below says no
   machine-readable cost source exists; that is true for TCU and **false for NACTVET**.
2. Institution registration codes embed an official subject board (`REG/HAS/…` = health,
   `BTP` = business/tourism, …) — a free, reliable sector signal, better than tags
   inferred from names.

**How to attack:** (1) write `scripts/extract_nactvet.py` as a *sibling* script — the TCU
requirement parser scores **0/718** on NACTVET phrasing (measured, not estimated), so it
needs its own grammar, but a much narrower one; (2) default the view to the 718 ACSEE
routes, since those are our users'; (3) **settle ordering before shipping** — candidates:
published fee, region, ownership, interest match — and disclose the basis in the UI.

**Done when:** a student who doesn't qualify for a degree sees real options — *and* those
options are presented in a way that helps rather than burying them. Worth noting: the
Form 6 route is generous (179 programme names, ~122,000 seats, and 704 of 718 routes take
**2 years instead of 3**). R4 should probably see this list before it ships.

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
