# Reflection — cycle 10

## What changed
The guidebook actually reaches students, and the answer can be navigated.

| | before | after |
|---|---|---|
| Programmes served | 362 | **539** |
| Eligible for a PCM B/C/C student | 275 | **441** |
| Ways to narrow that list | none | search + institution + region |
| Collapsed card's headline number | `nguvu 80%` (invented) | `pointi 9 · inahitajika 4` (TCU's) |
| Tests | 145 | **152** |

## Learnings

**We had already done the work and not handed it over.** Cycle 9 proved the transcription
complete and then left 508 of 870 programmes sitting in a JSON file the engine never read.
A completeness proof one stage upstream of what students see is not completeness. Worth
watching for: the metric we celebrated (870 transcribed, 0 lost) was true and still not the
number that mattered (362 served).

**Deleting the buggy code beat fixing it.** `extract_guidebook.py`'s row finder is gone
rather than patched. Transcription is proved complete against an independent oracle, so
re-deriving rows there could only add a second way to be wrong. The narrow `CODE_RE` did not
need a wider regex; it needed to not exist.

**42 programmes were missing for a reason nobody would guess.** They parsed their
requirements perfectly and were quarantined because no tag could be inferred from names like
*Bachelor of Theology* or *Development Planning* — whole fields the keyword list never
named. The quarantine reason string is what made this findable in a minute. Reasons on
rejected rows earn their keep.

**Fixing the backend broke the frontend's premise.** 275 results was already too many; 441
is worse. Serving more data made the UI a blocker rather than a polish item — which is why
both were one cycle. Shipping unit-01 alone would have made the product worse.

**The prototype's worst bug is a good spec.** KaziKijana's filter used
`subjects.some(s => requirementText.includes(s))` and showed Doctor of Medicine to PCM
students. Ours filters an already-verified set and says so in the UI. Knowing exactly how
the other implementation lied made the honest version easy to specify.

## Honest status
- Both units met their criteria; every criterion was verified rather than assumed.
- 331 rows remain quarantined, 322 of them for "requirement not cleanly parsed". That is
  the honesty contract working, not a backlog item to clear carelessly — each one served
  wrongly is a student told they qualify when they do not.
- The 360px overflow fixed here was pre-existing and had never been caught, because no test
  asserts layout. Browser checks found it; the suite would not have.

## Next
Design system (type scale, colour triad, elevation) — measured cause of the flat look is 20
font sizes, 10 radii, 0 shadows. Then `dunia-ya-kazi` depth: 26 family one-liners and entry
by combination, which supplies the missing premise for our own "Discoveries" group.
Still zero student evidence. That remains the largest untested assumption in the project.
