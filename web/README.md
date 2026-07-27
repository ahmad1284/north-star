# North Star — web client + guidance pages

## The pages

| File | Route | What it is |
|---|---|---|
| `index.html` | `/` | The tool: combination → grades → interests → grouped results |
| `barua.html` | `/barua` | Ahmad Sadri's letter — the founding document, in Swahili as written |
| `dunia-ya-kazi.html` | `/dunia-ya-kazi` | The whole ACT World of Work Map: both axes, all 26 job families |
| `maswali.html` | `/maswali` | The questions to carry to a campus visit (print/screenshot friendly) |

**The journey is ordered: `barua` → `dunia-ya-kazi` → `maswali`.** The letter says *go and
ask*; the map shows the student the full field of work before they narrow it; only then do
the questions make sense. Each page ends by pointing at the next one, and the nav on every
page lists them in this order. If you add a page, decide where it sits in that sequence.

**Why the guidance pages exist.** The engine answers "can I get in?". It cannot answer what
a course is really like, what it costs, or what people in it say — and those facts are in no
document we can parse. So the tool does what the letter does: it says it doesn't know, and
hands the student the questions. In the results, an unknown fact renders as
*"hatujui — uliza"* linking to `/maswali`, not as a bare dash.

Routes are declared explicitly in `api.py` (not a `StaticFiles` mount) so no request can
traverse the filesystem — a property the security review verified; keep it.

## The client

One self-contained HTML file. No framework, no build step, no dependencies, no external
requests: everything (styles, script, favicon) is inline, so the page works on a slow
phone connection and can be hosted anywhere — or opened straight from disk.

It is a **client of the API, not part of it**. The backend serves it at `/` as a
convenience, but the API is complete without it and other clients (WhatsApp, a native
app) are meant to sit alongside this one.

## Run it

**With the backend (simplest):**

```bash
cd backend && uvicorn northstar.api:app
# open http://127.0.0.1:8000/
```

**Standalone** — open `web/index.html` directly, or host it anywhere, and point it at an
API by setting `window.NORTH_STAR_API` before the page's script runs:

```html
<script>window.NORTH_STAR_API = "https://your-api-host";</script>
```

The API sends permissive CORS headers (it serves public, read-only data and takes no
credentials), so a client on a different origin works without extra configuration. If the
API is unreachable the page says so rather than failing silently.

To serve the client from a different directory than `web/`, set `NORTH_STAR_WEB_DIR`
for the backend process.

## What the page does

1. **Combination** — tap PCB / PCM / EGM / …, or add subjects individually
2. **Grades** — tap A–E, S, or F per subject
3. **Interests** (optional) — Ideas / People / Data / Things, from the ACT World of Work
   Map (see `/dunia-ya-kazi` for the whole map). Sending these adds the **Bridge** group
4. **Results** — grouped (For you · Discoveries · Bridge · Other eligible), ranked, and
   **filterable**: free-text search over name/institution/location/requirement text, plus
   institution and region selects built from the returned data with counts. Groups paginate
   20 at a time. Each card expands to show why the student qualifies (or what's missing),
   the programme's own requirement text, duration, capacity, the checklist fields, and the
   guidebook page it came from

**Two rules about the filters.** They narrow a set the engine has *already* ruled eligible —
they never re-decide anything — and the UI says so (*"havibadilishi majibu"*). The prior-art
app filtered with `subjects.some(s => requirementText.includes(s))` and showed Doctor of
Medicine to PCM students on the word "Chemistry"; that is matching wearing a filter's
clothes. Ours is search, and is labelled as search.

The collapsed card shows **`pointi 9 · inahitajika 4`**, not a percentage. `nguvu 80%` was a
unit we invented and displayed with the authority of a number while the guidebook's own
admission points sat unused in the payload. Students and TCU both reason in points.

Entries extracted automatically from the guidebook carry an **auto-extracted** badge
telling the student to confirm with the institution. Unknown facts render as
*"hatujui — uliza"* linking to `/maswali` — never as a dash, and never as a guess.

## Design tokens

Every page defines the **same** token block in its own `:root` — six type steps, four radii,
one elevation token, one display font:

```css
--fs-xs:.78rem; --fs-sm:.86rem; --fs-md:.94rem;
--fs-lg:1.02rem; --fs-xl:1.12rem; --fs-2xl:1.45rem;
--r-sm:8px; --r-md:12px; --r-lg:16px; --r-pill:999px;
--shadow: …;  --font-display:Georgia,"Times New Roman",serif;
```

Before this there were **20 distinct font sizes and zero box-shadows** across the four
pages. That, not the palette, is what made them read as unconsidered. Radius decreases as
you nest inward (container → item → chip), and `--shadow` is redefined for dark mode, where
a light drop shadow is invisible.

Georgia is used for headings only: it ships on effectively every device, so it buys
editorial character for **zero bytes and no external request**.

**The block is duplicated on purpose.** A shared stylesheet would be one more round trip on
the slow connection this audience actually has. Duplication needs a guard, so four tests in
`test_client.py` enforce it — including one that fails if a page uses any `var(--x)` it does
not define. That is not hypothetical: `dunia-ya-kazi.html` shipped for one commit with every
`font-size` referencing tokens its `:root` never declared, because its CSS is written more
compactly and a find-and-replace missed it. **Undefined custom properties fail silently** —
the text simply had no size and nothing errored.

## Conventions worth preserving

- **Swahili first, English alongside** — the audience is Tanzanian Form 6 graduates
- **Mobile-first** — most students will open this on a phone
- **Dark mode** comes free via `prefers-color-scheme`; keep both themes working
- **No third-party requests** — enforced by a test in `backend/tests/test_client.py`
- **Nothing hidden** — long lists are collapsed, never truncated away

## The World of Work wheel (`dunia-ya-kazi.html`)

The wheel is hand-written inline SVG — no library, no image, so it scales on any phone and
loads with the page. Two things about it are load-bearing:

- **The axes are opposites, per ACT:** Ideas ↔ Data on one axis, People ↔ Things on the
  other. Do not re-pair them; the whole map's meaning rests on those two contrasts.
- **The 26 letters run counter-clockwise from `start = 31°`, `step = 360/26`.** That offset
  is not decorative — it is what puts each of the six clusters beside the interest it
  actually belongs to (Technical next to *Vifaa*, not *Mawazo*). Change the offset and the
  map starts lying. Cluster labels sit *inside* the ring (radius 78) so they never collide
  with the axis labels.

Family names come from ACT's published A–Z list, kept as-is with a Swahili gloss rather
than renamed — the same "don't reinvent the wheel" rule the backend follows for TCU points.

## Editing

It's one file, deliberately: `index.html` (~350 lines — styles, then markup, then
script). The script has three parts: `boot()` loads reference data from the API,
`render()` lays out the groups, `card()` renders one programme. Changing presentation
should never require touching the backend.
