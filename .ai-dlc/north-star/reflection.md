# Reflection — cycle 1 (backend MVP)

## What was delivered
All four units complete; intent success criteria met. 30 real programmes across 8
institutions; pure engine + ranking + API; 31 tests as backpressure; draft PR #1.

## What worked
- **Elaboration paid off**: inputs → three-lens model → clean unit DAG; no rework.
- **Real data early**: transcribing the actual guidebook (not inventing samples)
  surfaced the true rule shapes (slots, floors, best-three basis) before the engine
  was designed — schema fit reality on the first try.
- **Personas as tests**: encoding "sensible answers" as regression tests caught the
  ranking quirk (fill-ratio favoured 2-subject programmes) immediately.

## Learnings / decisions made in flight
- Ranking currency = **TCU's own admission points** in the matched subjects
  ("don't reinvent the wheel" — Ahmad), tiebreak by strength.
- Seed breadth is a live UX variable: thin data reads as "no options for me."
  ECA persona fixed by adding IFM/Mzumbe. Rule of thumb: every common combination
  must see a real landscape (test-enforced: eligible ≥ 8 for ECA).
- Run pytest from `backend/` (repo-root collection fails).

## Next intent (queued): interests layer
Use the **ACT World of Work Map as-is** (Ideas/People/Data/Things → job families —
existing wheel, input from Ahmad) to capture interests, then:
- tag programmes with map regions;
- add the **"Bridge"**: interested-but-not-eligible → what it would take;
- keep backend-first: interests endpoints before any UI.
Also queued after that: wider guidebook transcription (scripted extraction),
NACTVET data, thin web client, WhatsApp channel, RAG chat.
