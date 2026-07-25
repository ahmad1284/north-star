# North Star — web client

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
   Map. Sending these adds the **Bridge** group
4. **Results** — grouped (For you · Discoveries · Bridge · Other eligible), ranked,
   long groups collapsed behind "show all". Each card expands to show why the student
   qualifies (or what's missing), the programme's own requirement text, duration,
   capacity, the checklist fields, and the guidebook page it came from

Entries extracted automatically from the guidebook carry an **auto-extracted** badge
telling the student to confirm with the institution. Unknown facts render as "—", never
as a guess.

## Conventions worth preserving

- **Swahili first, English alongside** — the audience is Tanzanian Form 6 graduates
- **Mobile-first** — most students will open this on a phone
- **Dark mode** comes free via `prefers-color-scheme`; keep both themes working
- **No third-party requests** — enforced by a test in `backend/tests/test_client.py`
- **Nothing hidden** — long lists are collapsed, never truncated away

## Editing

It's one file, deliberately: `index.html` (~350 lines — styles, then markup, then
script). The script has three parts: `boot()` loads reference data from the API,
`render()` lays out the groups, `card()` renders one programme. Changing presentation
should never require touching the backend.
