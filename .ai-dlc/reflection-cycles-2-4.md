# Reflection — cycles 2–4 (interests+bridge · extraction pipeline · web client)

## Delivered
- **Cycle 2 — interests layer:** ACT World of Work areas (used as-is), optional
  `interests` on /match, `interest_match` annotations, and the **bridge** group
  (want-but-not-yet-eligible, with what's missing). Backward compatible.
- **Cycle 3 — extraction pipeline:** `scripts/extract_guidebook.py`; knowledge base
  30 → **356 programmes / 39 institutions**. Honesty contract: 326 cleanly parsed and
  served (flagged `machine_parsed`), 311 ambiguous rows quarantined in
  `extraction_review.json`, curated always wins on conflict.
- **Cycle 4 — thin web client:** single self-contained mobile-first page (Swahili+English)
  served by the API at `/`. Verified in real Chromium at phone size: full student flow,
  groups render, reasons render, zero JS errors. 45 tests green.

## Learnings
- PDF table geometry: center-aligned headers make left-edge anchoring wrong; the CODE
  column (regular short codes) is the reliable datum — derive boundaries from data, not headers.
- "Serve only what parsed cleanly" turned a risky auto-extraction into a safe one; the
  review file makes the residual work visible instead of invisible.
- A same-origin static page is the thinnest possible client: no CORS, no build, no deps —
  and it forced no changes to the backend (the channel-agnostic bet paid off).

## Remaining work — needs things only Ahmad can provide (all externally blocked)
| Item | Why blocked |
|---|---|
| Review-file triage | Human judgement: promote/correct the 311 quarantined rows into curated data (can be done gradually; the app works without them) |
| NACTVET vocational data | No machine-readable NACTVET source in this environment; needs the equivalent NACTVET admission document |
| Checklist enrichment (cost, salary, time-to-employment, insider notes) | Real local data collection — exactly the letter's "ask people in the course" step; a CareerVillage-style Q&A layer is the future home |
| WhatsApp channel | Needs a Meta Business account, phone number, and API credentials |
| LLM+RAG chat | Needs an API key decision + hosting; the engine core is ready to be its grounded tool |
| Deployment | Needs a hosting choice (any box that runs `uvicorn` works; single process, no DB) |
