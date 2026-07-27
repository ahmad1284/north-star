# Prior art — "KaziKijana / Tanzania University & Career Guide"

An earlier attempt at this problem, built in Google AI Studio (React 19 + Vite + Tailwind +
Express + Gemini). Imported verbatim into `kazikijana/` so it can be read and mined. **It is
not wired into anything and does not build here** — it is reference material, not a
dependency.

This file is the assessment: what we take, what we leave, and why.

---

## The headline finding: it exposed a real bug in our extractor

This is worth more than any code in the zip.

The prior project's `tcu_catalog.json` has 146 programmes. Ours has 362. So it should be a
strict subset — except **96 of its codes were missing from ours**, and 59 of those were not
even in our quarantine file. They were simply *absent*.

Root cause, in `backend/scripts/extract_guidebook.py`:

```python
CODE_RE = re.compile(r"^[A-Z]{2,4}\d{3}$")     # requires exactly three digits
```

Programme codes shaped `CBD01`, `SUM01`, `AKU01`, `DMI01`, `CFR01`, `CBMZ1`, `CBMB01` —
three-to-five letters followed by **one or two** digits — never match. `extract_rows()`
then hits `if not code_words: continue` and abandons the whole page without a word.

Sweeping the guidebook with a loosened pattern, anchored on the same code-column x-range:

| | count |
|---|---|
| Distinct codes the strict regex rejects | **190** |
| …already served or quarantined by our pipeline | **0** |
| …**invisible: not served, not quarantined, not logged** | **190** |

Whole institutions are missing: College of Business Education (all four campuses, ~43
programmes), Dar es Salaam Maritime Institute, Eastern Africa Statistical Training Centre,
Dr. Salim Ahmed Salim Centre for Foreign Relations, Aga Khan University, SUMAIT, Institute
of Social Work, Water Institute. A student from Zanzibar looking for SUMAIT is told nothing
exists.

**Why this is worse than a missed row.** Our honesty contract says ambiguous rows get
quarantined and never shown — the 305 rows in `extraction_review.json` are that promise
working. These 190 bypassed it. A page that yields no codes is skipped silently, so the
quarantine count looked healthy while a fifth of the corpus was never seen at all. The gap
was invisible to the very mechanism built to make gaps visible.

**Fix (not applied here — see "What happens next").** Widen `CODE_RE`, and add a
back-stop: a page with a `Code` header, a `Points` header and zero matched code cells
should be **recorded as a failure**, not `continue`d past. The regex will need care against
false positives, and re-extraction changes the served knowledge base, so it wants its own
cycle with a re-run of the parser tests.

---

## What we take

### 1. The World of Work sector content — the strongest asset here
`src/components/WorldOfWork.tsx` carries editorial depth our `/dunia-ya-kazi` lacks. For
each of the six ACT clusters it has `tanzanianContext`, `keyTasks`, `professions`,
`fields`, and a mapping from **A-level combinations** (`HKL`, `ECA`, `EGM`, …) to sectors:

> *Business Operations* — "Operating within banks (like NMB, CRDB), managing ports &
> container shipments, auditing tax declarations, or handling supply chains."

Our map names all 26 ACT families correctly but says nothing about what any of them looks
like *in Tanzania*. This fills exactly that hole, and the combination→sector mapping is a
second, independent route into the same taxonomy.

**Caveat that must not be skipped:** this text is LLM-generated. Employer names, licensing
boards (ERB, AQRB, MCT, CPA) and sector claims need checking against reality before they go
in front of a student. Take it as a **drafting aid**, not as sourced content — and treat
anything numeric in it as unverified.

### 2. The combination descriptions
`tcu_data.ts` has plain-language descriptions per combination (PCM, PCB, CBG, CBA, EGM,
ECA, HGE, HKL…). Ours are bare subject lists. Same caveat — written by a model, needs a
pass — but a good starting draft, and directly useful on the grades screen.

### 3. Its catalog as an independent extraction check
146 rows pulled by a different tool from the same PDF. Cross-checking two independent
extractions is how the bug above surfaced. Worth keeping as a **regression fixture**: our
pipeline should account for every code in it, either served or explicitly quarantined.

### 4. UI ideas, not UI code
Tabbed sections, per-card sector colour coding, and the roadmap's stage layout are decent
patterns. Worth stealing as *ideas*.

---

## What we leave

### 1. The Forum — reject outright
`server.ts` invents a mentor and presents it as a person:

```js
"authorName": "Full Name of simulated mentor",
"authorTitle": "Realistic job title and organization + university alumnus info
                (e.g. Software Engineer at Vodacom | UDSM Alumna)"
```

The reply is stored with `isMentor: true`, given a `likes` count, and rendered beside the
seeded ones — which are also fabricated ("Erick John, Senior Software Engineer at Selcom",
12 likes). The no-API-key fallback tells the student *"Our mentoring panel has been
notified"*. There is no panel.

This is the exact inverse of the project's purpose. The letter's whole instruction is **go
and ask real people** — a plausible fake alumnus at a real named company is worse than
silence, because it satisfies the urge to ask without any of the truth. `/maswali` exists
because we decided not to do this. A real mentor forum with real humans would be excellent;
this is not that.

### 2. Gemini in the decision path
`/api/chat` and `/api/roadmap` generate advice, and `/api/roadmap` produces the plan
itself. We chose a deterministic expert system for eligibility on purpose: a student is
told *why* they qualify, from encoded rules, with no chance of a fluent wrong answer. An
LLM is defensible for open-ended conversation later; it is not going near "can I get in?".

### 3. The stack
React 19 + Vite + Tailwind + Express + a build step, versus one self-contained HTML file
with no dependencies that opens on a slow phone. Our constraint is the audience's
connection, and the prior stack loses on it. Nothing here justifies the switch.

### 4. Its catalog as a data source
146 rows of **unparsed prose** requirements (`"Two principal passes in the following
subjects: History, English, Geography…"`) — the raw text we already extract and then
*encode*. Its value is as a cross-check, not as input. Its institution field also carries
extraction damage (one row reads `College of Business Education (CBE), Thâm Quy`).

---

## What happened next

1. ✅ **The extractor was replaced, not patched.** `transcribe_guidebook.py` now reads the
   PDF's own ruled table cells and produces all **870** programmes verbatim, checked against
   an oracle independent of code shape (each institution's S/N column). `CODE_RE` and the
   row-finder are deleted. `extract_guidebook.py` only interprets requirement prose now.
2. ✅ **The 146-row catalog is a coverage fixture** in `test_transcription.py`. 145 of its
   codes are accounted for; the one absence, `ZU009`, is genuinely not in this edition —
   that catalog cites pages up to 392 in a **376-page** document, so it came from a
   different edition.
3. ✅ **Served programmes went 362 → 539**, and the results became navigable (search,
   institution and region filters, pagination, real admission points on the card).
4. ⬜ **The sector content for `/dunia-ya-kazi`** — still to do, and the section below is
   the brief. Structure adopted as-is; Tanzania claims blocked on verification.
5. Forum, Gemini paths and the stack stay where they are.

---

## How KaziKijana structured the World of Work — adopt this, don't redesign it

Read `kazikijana/src/components/WorldOfWork.tsx` before touching `web/dunia-ya-kazi.html`.
Its *content* has problems (see below) but its **information architecture is better than
ours and should be taken as-is**. Three decisions, in order of importance:

**1. Selection happens at cluster level, not family level.** Six clickable wedges
(`lines 411-463`), never 26 letters. The cluster is the unit of exploration; the families
are its payload. Our page currently shows all 26 families as a static picture with no
selection at all, which is why it reads as a diagram rather than something to explore.

**2. A fixed six-slot template renders for whichever cluster is selected** (`lines 560-632`).
Same slots, same order, every time — which is what lets a student compare clusters instead
of re-reading each one:

| Their slot | Ours becomes | Evidence status |
|---|---|---|
| Sector Overview | `Ni nini` | ACT cluster definition — **verified** |
| Reality in Tanzania | `Hapa Tanzania` | **their text is LLM-generated — do not copy** |
| Example Tasks (numbered card grid) | `Siku yako ingekuwaje` | ACT family descriptors — safe |
| Ideal A-Level Streams (pills) | `Combination zinazoelekea hapa` | derive from our `combinations.json` |
| Popular Careers (pills) | generic occupation names | dictionary facts — safe |
| Recommended TCU Degrees | link into the tool | **their version substring-matches — reject** |

Add one slot they don't have and we can compute: **`Mahali` — where the cluster sits on the
map** ("Takwimu + Watu"). We derive it from ACT geometry, so it is verified for free.

**3. A six-tile legend grid sits directly under the wheel** (`lines 511-532`), duplicating
the wedges as full-size labelled buttons. This is the single best mobile decision in the
file: nothing depends on hitting a small SVG shape with a thumb. Steal it literally.

Also worth copying: **selection state is triple-encoded** — `fill`, `stroke` and
`strokeWidth` all change together (`lines 413-415`), so the active cluster is legible at a
glance and survives colour-blindness.

### The one constraint that changes the implementation
`test_client.py::test_guidance_pages_load_no_external_resources` asserts `"<script"` is
absent from `/barua`, `/maswali` and `/dunia-ya-kazi`. **Those pages must stay
JavaScript-free**, so their `useState` selection model becomes CSS: `<details>` for the
dossiers, `:target` with SVG `<a>` anchors for the wheel. Only `index.html` may run JS.

### What not to carry over
- **`tanzanianContext`** — every employer, licensing board and salary in it is
  LLM-generated. Keep the *slot*, render it as an honest unknown pointing at `/maswali`
  until Ahmad supplies verified text. The tool already says it doesn't know what a course
  costs; the map must not suddenly become confident about who is hiring.
- **Their `fields` arrays** — wrong against ACT (`administration` claims "Personal
  Services", which is family Z / Social Service; `technical` omits M and N; `stem` omits S).
  Our family→cluster mapping is correct. Import the shape, never the taxonomy.
- **The Likert quiz and its `X: {x.toFixed(1)}` readout** — false precision from eight
  self-report answers. If a quiz is ever built it outputs a *region* and a set of letters,
  never a number.
