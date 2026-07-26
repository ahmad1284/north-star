# R3 — NACTVET (vocational track): source assessment

Research date: 2026-07-25. All figures below were produced by parsing the downloaded
PDF, not read off a webpage.

**Verdict: a usable structured source exists and is already in `inputs/`.** It is
*better* structured than the TCU guidebook. The blocker is not data acquisition — it is
that the engine's eligibility model has nothing to bite on.

---

## 1. What NACTVET publishes, and where

**The correct domain is `nactvet.go.tz`.** `nacte.go.tz` still resolves (HTTP 200) and
serves NACTVET-branded content — it is the legacy name (the body was renamed from NACTE
to NACTVET), not a separate organisation. Use `nactvet.go.tz`.

The document we want:

| | |
|---|---|
| Title | *Certificate and Diploma Programmes Offered by Technical Institutions — Admission Guidebook for 2026/2027* |
| URL | `https://www.nactvet.go.tz/storage/public/files/GUIDEBOOK_FOR_ALL_2026_2027.pdf` |
| Downloaded to | `inputs/nactvet-GUIDEBOOK_FOR_ALL_2026_2027.pdf` (778,201 bytes, PDF 1.7, 200 pages) |
| Generated | 28 May 2026, 05:10 EAT (stamped on page 1) |

Prior edition also live at a parallel path — useful for R8 (detecting a new edition):
`https://www.nactvet.go.tz/storage/public/files/GUIDEBOOK_FOR_ALL_NTA_2025_2026.pdf`.
The naming is predictable enough to poll annually.

Notes on the site: `/page/downloads` returned HTTP 503 then 500 on repeated attempts —
the site is flaky, but the `/storage/public/files/` paths serve reliably. The homepage
links almost nothing; direct file URLs are the practical access route.

**No Excel, CSV, or public API was found.** The PDF's producer metadata (`cairo` via
`Mozilla Firefox`) plus the generation timestamp show it is printed from an internal
web application, so a database certainly exists behind it — but nothing public. Do not
assume an endpoint exists; none was located. The PDF is the source.

Scope caveat: this guidebook covers **NTA Levels 4–6 only** (Basic Technician
Certificate → Ordinary Diploma). No NTA 7/8 (bachelor-level technical) guidebook was
found; searches surfaced only Level 4–6 material. If NACTVET publishes a degree-level
equivalent, it was not discoverable.

---

## 2. Structure — and it parses cleanly

Unlike the TCU book, this PDF has **real ruled tables**. PyMuPDF's `page.find_tables()`
extracts them directly — no coordinate-band reconstruction needed.

**Tables were found and extracted on 200 of 200 pages.** Yield:

| Measure | Count |
|---|---|
| Institutions | **415** (234 private, 181 government) across 29 regions |
| Distinct programmes (institution × programme) | **1,599** |
| Distinct programme names | 390 |
| Entry-route rows (a programme can have several) | **2,406** |
| Rows with a duration | 2,358 (98%) |
| Rows with an admission capacity | 2,358 (98%) |
| Programmes with a tuition fee string | 1,509 / 1,599 (**94%**) |
| Rows the parser failed to attach a programme name to | 28 (1.2%) |

For scale: TCU gives us 356 programmes across 39 institutions. NACTVET is **~4.5× the
programmes and ~10× the institutions.**

Per-institution header carries: name, registration code (`REG/HAS/191`), ownership
(Private/Government), district and region. Columns are: S/N, Program Name (Award),
Admission Requirements, Program Duration (Yrs), Admission Capacity, Tuition Fees.

Two structural differences from TCU that a parser must handle:

1. **One programme, several entry routes.** 762 of 1,599 programmes have more than one
   requirement row — typically a CSEE route (3 years) and an NTA-4/ACSEE route (2
   years), each with *its own duration and capacity*. TCU's model is one row = one
   programme. Ours would need a programme to hold a list of entry routes, or each route
   modelled as a separate record.
2. **Fees are stated once per programme**, on the first route row; later rows are blank.
   A parser must carry it down rather than record `null`.

### Tuition fees are in this document — that is an R1 win

1,558 fee strings, and **all 1,558** match a clean `TSH. N,NNN,NNN/=` pattern, some with
a `Foreigner Fee: USD N` component. Examples: `Local Fee: TSH. 1,600,000/=`,
`Local Fee: TSH. 1,100,000/= , Foreigner Fee: USD 440/=`.

RESEARCH.md R1 records `cost` as empty for all 356 programmes and notes there is no
machine-readable national source. That is true for TCU. **It is not true for NACTVET** —
their guidebook carries official published fees for 94% of programmes. Whatever happens
with the vocational track, this is a sourced-cost dataset we currently do not have.

---

## 3. Can `extract_guidebook.py` be reused?

**Table extraction: no, and that is good news — it gets simpler.** The TCU extractor's
`extract_rows()` reconstructs columns from word x-coordinates against header positions,
because the TCU PDF has no usable ruling. NACTVET's has ruled cells; `find_tables()`
replaces roughly 110 lines of geometry code. None of that machinery transfers, and none
of it is needed.

**Requirement parsing: no. Measured, not estimated.** I ran the real
`parse_requirement()` from `backend/scripts/extract_guidebook.py` over all 718
ACSEE-bearing requirement texts:

```
parse_requirement() succeeded on 0/718 ACSEE rows
failure reasons: [('no pattern matched', 718)]
```

Every one fails. TCU's patterns are anchored on `"two|three principal passes in <list>"`.
NACTVET phrasing is a different grammar entirely (`"Holders of ... (ACSEE) with at least
one Principal Pass and one Subsidiary in Principal Subjects"`). A new parser is required.

The good news: the target grammar is far narrower than TCU's. **538 of 718** ACSEE
clauses are the single generic shape *"at least one principal pass and one subsidiary in
principal subjects"* (allowing for spelling/casing drift), and the remaining 180 name a
subject list. Only 12 mention a letter-grade floor. A handful of patterns would cover
nearly everything — versus the 261 unparsed shapes still quarantined from TCU (R2).

**What does transfer:**

- `infer_tags()` works out of the box on **279 of 390** distinct programme names (72%).
  The 111 misses are vocational vocabulary the keyword list has never seen — *Marine
  Operations, Lapidary and Jewellery Technology, Multimedia and Animation Technology,
  Cargo Tallying, Clearing and Forwarding, Tour Guiding, Agro Bioprocess Technology*.
  Widening `TAG_KEYWORDS` is the same cheap win R2 already identifies.
- The honesty contract (parse cleanly or quarantine), the curated-wins-on-conflict rule,
  and the output shape all carry over unchanged.
- The institution registration code embeds a subject board — `HAS` health (151 insts),
  `BTP` business/tourism/planning (87), `SAT` science & allied tech (31), `ANE` (30),
  `PWF` (29), `EOS` (25), `BMG` (23), `TLF` (8), plus 29 under generic `REG/NACTVET/`.
  This is a free, official sector signal — better than inferring tags from names, and a
  natural fill for the `sector`/`track` field R3 already proposes.

---

## 4. The entry-qualification model — this is the real finding

NACTVET does **not** use A-level points. Across all 2,406 rows, only **3** mention
"points" at all. There is no equivalent of TCU's admission-points currency, so
`min_points`, `points_basis`, and the entire ranking basis ("rank in TCU's own
currency", README principle 5) have **no counterpart here.**

Qualification types actually used (rows may cite several as alternatives):

| Qualification | Rows | What it is |
|---|---|---|
| CSEE | 2,203 | Form 4 / O-level — the dominant route |
| NTA Level 4 (Basic Technician Certificate) | 788 | Prior vocational award |
| **ACSEE** | **718** | **Form 6 / A-level — our students** |
| NVA Level III / Trade Test | 532 | Vocational award |
| NTA Level 5 | 24 | |

### What a Form 6 graduate faces

718 rows offer an ACSEE route, spanning **179 distinct programme names across 270
institutions**, with a combined stated admission capacity of **~122,000 seats**. 704 of
those 718 routes are **2 years** (versus 3 years via the CSEE route) — Form 6 buys you a
year off an Ordinary Diploma. That is a genuinely useful, concrete thing to tell a
student, and we currently tell them nothing.

But the requirement itself is, in 538 of 718 cases, exactly this:

> *at least one Principal Pass and one Subsidiary in Principal Subjects*

No subject specificity. No grade floor. No points. **Any student who passed A-levels at
all satisfies it.**

This inverts the difficulty. The engine already models A-level grades, so encoding "one
principal + one subsidiary" is trivial — a `{"choose": 1, "from": "any"}` slot plus a
subsidiary constraint, both shapes that already exist. The problem is the opposite of
hard: the rule is so permissive that **eligibility filtering does essentially nothing.**
A Form 6 student would come back "eligible" for ~1,000+ programmes across 270
institutions, undifferentiated, unranked, with no basis to order them.

That breaks two things at once:

- **Ranking has no currency.** Ordering is defined as admission points brought to a
  programme's defining subjects. NACTVET programmes have neither points nor defining
  subjects. We would have to invent an ordering — and README principle 5 exists
  specifically to forbid inventing scores.
- **"For you" / "Discoveries" / "Bridge" lose meaning.** Bridge is "what you're drawn to
  but don't qualify for" — against NACTVET, nearly nobody fails to qualify, so Bridge
  is empty and Discoveries is 1,000 items of noise. The grouping model assumes
  selectivity that does not exist here.

The 180 subject-specific ACSEE rows (e.g. *"one principal pass and one subsidiary in
Biology, Chemistry, Physics, Advanced Mathematics, Agriculture..."*) are the only ones
the current engine can meaningfully discriminate on.

---

## 5. Recommended next step

**Not blocked. Ingestion is a small, well-defined job; presentation is the open design
question.** Do them in that order, and do not let the second block the first.

**Step 1 — write `scripts/extract_nactvet.py` (new file, do not extend the TCU one).**
Sibling script, same honesty contract, different parser. `find_tables()` for geometry;
carry institution and programme name across page breaks (measured: 28 orphan rows,
1.2%); emit one record per entry route with its own duration and capacity; carry the
fee down from the programme's first row. Target the ~5 requirement shapes that cover the
718 ACSEE rows and quarantine the rest. Add `track: "vocational"` and a `sector` from
the REG-code board segment. Widen `TAG_KEYWORDS` for the 111 untagged vocational names.
This is a contained day of work with a clear ceiling, and the data supports it.

**Step 2 — filter to the ACSEE routes for the default view.** Our users are Form 6
graduates. Serving all 2,406 routes buries them; the 718 ACSEE routes are the honest
answer to "what can I do with my A-levels?" The CSEE-only routes are still worth storing
(a student who did badly at A-level may still want them) but should not be the default.

**Step 3 — settle the ranking question before shipping it to students.** This is the
genuine research item, and it is a *product* question, not an engineering one. Since
eligibility cannot discriminate and points do not exist, ordering has to come from
something else — plausible candidates, in rough order of defensibility: published
tuition fee (real, sourced, in this document, and the thing the letter actually asks
about); geography (institution in the student's region); ownership (government fees run
markedly lower); stated capacity; interest-tag match, which is the only signal we
already have that expresses student preference. **Whatever is chosen must be disclosed
in the UI as the ordering basis** — silently inventing a merit-looking ranking over
programmes that have no merit criterion would violate principle 5 more seriously than
leaving them unranked. Presenting them deliberately *unranked* — "you qualify for all of
these; here is how to narrow it down" — is a legitimate and arguably more honest option.

**One caution.** R3's premise is that vocational options rescue the student who doesn't
qualify for a degree. The data supports that generously — 122,000 ACSEE-route seats, and
a year saved. But it also means we will be handing an anxious 19-year-old a list of a
thousand things they qualify for. The RESEARCH.md success criterion ("sees real options
rather than a short list and an implied dead end") is met by the data; whether it is met
*for the student* is exactly the R4 question, and R4 should probably see this list before
we ship it.

---

## Sources

- [NACTVET official site](https://www.nactvet.go.tz/) (`nacte.go.tz` = legacy domain, same body)
- [Admission Guidebook 2026/2027 (PDF, downloaded)](https://www.nactvet.go.tz/storage/public/files/GUIDEBOOK_FOR_ALL_2026_2027.pdf)
- [Admission Guidebook 2025/2026 (PDF, prior edition, verified live)](https://www.nactvet.go.tz/storage/public/files/GUIDEBOOK_FOR_ALL_NTA_2025_2026.pdf)
- [Academic Calendar 2026/2027 (PDF, verified live)](https://www.nactvet.go.tz/storage/public/files/CALENDAR%20FOR%20THE%20ACADEMIC%20YEAR%202026-2027.pdf)
- [Daily News — NACTVET opens 2026/27 certificate, diploma admissions](https://dailynews.co.tz/nactvet-opens-2026-27-certificate-diploma-admissions/)

All counts in this document were produced by parsing the downloaded PDF; none were taken
from a secondary site.
