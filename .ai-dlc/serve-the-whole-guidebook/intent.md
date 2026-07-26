---
workflow: default
git:
  change_strategy: intent
  auto_merge: false
  auto_squash: false
announcements: []
status: in_progress
epic: ""
quality_gates:
  - "cd backend && python -m pytest -q"
---

# Serve the whole guidebook, and make the answer navigable (cycle 10)

## Problem

Two projects, one product. North Star built the engine; KaziKijana explored the
experience. Judged as what it was — an AI Studio prototype — KaziKijana's placeholder
logic is not a defect, it is what a prototype is for. What it established is the *shape*
of the experience, and North Star has never had one.

Meanwhile North Star has developed the opposite failure. Cycle 9 transcribed **870
programmes**. The engine serves **362**. A student today is shown **42% of the guidebook**
and told it is the answer. We did the work and did not hand it over.

And what we do serve is unnavigable. Measured against the live engine:

| Profile | eligible | for_you |
|---|---|---|
| PCM B/C/C | **275** | 130 |
| PCB C/C/D | 233 | 73 |

275 results with no search, no institution filter, no region filter and no sort is not a
result — it is a refusal to answer. *"Naweza kusoma nini Mwanza?"* is unanswerable in our
tool, though `location` sits on every card. The one affordance, `Onyesha zote 130…`,
synchronously builds 124 `<details>` nodes on a budget Android phone.

These are the same cycle. Serving 870 makes navigation mandatory; navigating 362 is
polishing a partial answer.

## Solution

Close both gaps, in that order, keeping the honesty contract intact throughout.

1. **Serve the whole guidebook.** Feed the cycle-9 transcription through the requirement
   parser. Rules that parse cleanly are served; anything ambiguous is quarantined and
   visible, exactly as now. Curated entries still win on conflict. The transcription is
   already proved complete — this is interpretation, and it inherits cycle 9's rule that
   nothing may be dropped in silence.
2. **Make the answer navigable.** Search, institution and region filters, pagination, real
   admission points on the collapsed card, and a visible affordance that a card opens.

### Two things we are deliberately NOT doing

- **No substring matching presented as matching.** KaziKijana's combination filter used
  `subjects.some(s => requirementText.includes(s))`, which showed Doctor of Medicine to PCM
  students because the word "Chemistry" appeared. Our filters narrow an **already-verified
  eligible set** and are labelled as search, never as match.
- **No invented units.** The collapsed card currently reads `nguvu 80%` — a measure we
  invented — while `matched_points` and `min_points` sit unused in the payload. Points are
  the national currency of this decision. Replace ours with theirs.

## Success Criteria

### unit-01 — Serve the whole guidebook
- [ ] The transcription feeds the rules pipeline; the served knowledge base grows well
      beyond 362 toward the 870 transcribed
- [ ] The honesty contract holds: only cleanly-parsed rules served, everything else
      quarantined **and countable**; no page or row lost in silence
- [ ] Curated entries still win over machine-parsed on conflict
- [ ] `machine_parsed` provenance is preserved and still badged in the client
- [ ] No false positives introduced: spot-checked against known-hard programmes
- [ ] The count served, quarantined and rejected is reported and reconciles to 870

### unit-02 — Navigate the answer
- [ ] Text search over programme name, institution, location and requirement text
- [ ] Institution filter and region filter, built from the returned data with counts
- [ ] Filters narrow an already-computed eligible set and are labelled as search
- [ ] Collapsed card shows real points (`pointi 12 · inahitajika 6`), not `nguvu %`
- [ ] `min_points` exposed in the programme payload
- [ ] Cards visibly indicate they open
- [ ] Results paginate rather than building the whole list at once
- [ ] Empty groups explain themselves; a reset clears all filters
- [ ] Works at 360px, both themes, no new dependencies, no external requests

## Units
- unit-01 — Serve the whole guidebook (rules from the transcription)
- unit-02 — Navigate the answer (filters, points, affordance, pagination)

## Deferred to their own cycles, with reasons
- **Design system** (5-step type scale, colour triad via `color-mix`, elevation, shared
  page-header with provenance). Measured cause of the flat look: 20 font sizes, 10 radii,
  0 shadows. High value, cheap — but it is presentation, and it should follow the content
  it presents.
- **`dunia-ya-kazi` depth** — 26 family one-liners, wheel letters as anchors, entry by
  combination. The combination entry point supplies the missing premise for our own
  "Discoveries" group, so it is the strongest of these.
- **`ratiba.html`** — an admission calendar. Blocked on sourcing real TCU dates; if we
  cannot cite them we do not ship it. That is the entire difference between our page and
  the prototype's hardcoded `"January 2033"`.

## Review note (Reviewer hat)
unit-01 changes **what students are told they qualify for**, which is the highest-stakes
change this project can make. The review must hunt false positives specifically: a
programme newly served with a mis-parsed rule tells a student they qualify when they do
not, and they find out after applying. Quarantining too much is a cost; serving one wrong
rule is a harm. Verify the asymmetry was respected.
