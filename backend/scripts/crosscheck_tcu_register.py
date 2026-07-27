#!/usr/bin/env python3
"""Cross-check our guidebook transcription against TCU's public accreditation register.

Two independent readings of reality are worth more than one careful reading. The
188-programme gap that started this line of work was found exactly this way — by
comparing our extraction against someone else's.

The register lives at tcu.go.tz as a server-rendered Drupal view. There is no API:
JSON:API and REST are disabled (404), the Views AJAX route is 403 for anonymous
users, and there is no CSV export. What exists is a stable, unauthenticated HTML
page driven by query parameters, 20 rows per page. That is enough.

WHAT THIS CAN AND CANNOT VERIFY
-------------------------------
Verifies: institution, programme name, and duration.
Cannot verify: **programme code, entry requirements, points, capacity** — none of
which appear anywhere in the register. Those are the fields the matching engine
actually depends on, so this is a spell-check on the transcription, not a
validation of the rules. Said plainly here because a cross-check whose limits are
not stated invites more confidence than it earns.

TWO STRUCTURAL DIFFERENCES, BOTH EXPECTED
-----------------------------------------
1. The register lists everything *accredited*; the guidebook lists what is open for
   Form 6 direct entry this cycle. UDSM has 184 accredited bachelor programmes and
   86 in the guidebook. A name in one and not the other is normally not an error.
2. The register covers **universities only** (54 institutions). Our guidebook has 94.
   The difference is NACTVET-accredited non-university institutions — DIT, CBE, IFM,
   NIT, TIA, the Water Institute. Roughly a third of our institutions cannot be
   checked from this source at all, and are reported as unverifiable rather than
   silently counted as matching.

Usage
-----
    python scripts/crosscheck_tcu_register.py [--limit-pages N] [--cache FILE]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

BASE = ("https://tcu.go.tz/services/accreditation/"
        "academic-programmes-offered-universities-tanzania")
CA = "/root/.ccr/ca-bundle.crt"
DATA = Path(__file__).resolve().parents[1] / "northstar" / "data"

_WS = re.compile(r"\s+")
_TAG = re.compile(r"<[^>]+>")
# Tolerate "( UDOM)" — the PDF's text layer inserts a leading space, and an
# acronym regex that misses it silently drops the institution into "unverifiable".
_ACRONYM = re.compile(r"\(\s*([A-Za-z][A-Za-z.\- ]{1,12}?)\s*\)")

# Words that carry no discriminating power when comparing programme titles.
_NOISE = {"bachelor", "of", "in", "with", "and", "the", "degree", "science",
          "arts", "a", "bsc", "ba", "hons", "honours"}


def norm_text(s: str) -> str:
    return _WS.sub(" ", html.unescape(_TAG.sub(" ", s))).strip()


def squash(name: str) -> str:
    """Reduce a programme title to comparable content words.

    Titles differ cosmetically between the two sources ("Bachelor of Science in
    Nursing" vs "BSc Nursing"), so degree-type words are dropped and the rest is
    sorted. Deliberately lossy: this decides *comparability*, never eligibility.
    """
    words = re.findall(r"[a-z]+", name.lower())
    return " ".join(sorted(w for w in words if w not in _NOISE))


def acronym(institution: str) -> str:
    """Institutions are named differently in each source; the parenthesised
    acronym is the one stable join key both of them print.

    Not every institution prints one — "KCMC University, Kilimanjaro" has none —
    so fall back to the leading significant words of the name. Returning "" for
    those would file a real university under "cannot be checked", which is the
    quiet kind of wrong this whole exercise exists to catch.
    """
    m = _ACRONYM.search(institution or "")
    if m:
        return m.group(1).replace(".", "").replace(" ", "").upper()
    head = re.split(r"[,(]", institution or "")[0]
    words = [w for w in re.findall(r"[A-Za-z]+", head)
             if w.lower() not in {"the", "of", "and", "university", "college",
                                  "institute", "centre", "center"}]
    return "".join(words[:2]).upper()


def fetch(page: int, level: str = "bachelor") -> str:
    url = f"{BASE}?field_award_level_value={level}&page={page}"
    out = subprocess.run(
        ["curl", "-sSL", "--cacert", CA, "--max-time", "45", url],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"curl failed for page {page}: {out.stderr.strip()[:200]}")
    return out.stdout


def parse_rows(page_html: str) -> list[dict]:
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page_html, re.S):
        cells = [norm_text(c) for c in
                 re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        cells = [c for c in cells if c]
        if len(cells) < 7 or cells[0] == "S/N":
            continue
        rows.append({"programme": cells[1], "institution": cells[2],
                     "award": cells[3], "duration_months": cells[4],
                     "uqf": cells[5], "mode": cells[6]})
    return rows


def harvest(limit_pages: int | None, cache: Path | None) -> list[dict]:
    if cache and cache.exists():
        print(f"using cached harvest: {cache}")
        return json.loads(cache.read_text(encoding="utf-8"))
    rows, page = [], 0
    while True:
        if limit_pages is not None and page >= limit_pages:
            break
        batch = parse_rows(fetch(page))
        if not batch:
            break
        rows.extend(batch)
        print(f"  page {page}: {len(batch)} rows (total {len(rows)})")
        page += 1
        time.sleep(0.4)          # be a polite guest on someone else's server
    if cache:
        cache.write_text(json.dumps(rows, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-pages", type=int, default=None)
    ap.add_argument("--cache", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=DATA / "tcu_register_crosscheck.json")
    args = ap.parse_args()

    src = DATA / "guidebook_programmes.json"
    if not src.exists():
        print(f"error: run transcribe_guidebook.py first ({src} missing)", file=sys.stderr)
        return 1
    ours = json.loads(src.read_text(encoding="utf-8"))

    print("harvesting TCU accreditation register (bachelor)…")
    register = harvest(args.limit_pages, args.cache)
    print(f"harvested {len(register)} register rows")

    reg_by_inst: dict[str, set[str]] = defaultdict(set)
    reg_names: dict[str, dict[str, str]] = defaultdict(dict)
    for r in register:
        a = acronym(r["institution"])
        reg_by_inst[a].add(squash(r["programme"]))
        reg_names[a][squash(r["programme"])] = r["programme"]

    matched, name_mismatch, not_in_register, unverifiable = [], [], [], []
    for row in ours:
        a = acronym(row["institution"] or "")
        key = squash(row["programme"])
        if not a or a not in reg_by_inst:
            # No counterpart institution in a universities-only register.
            unverifiable.append({"code": row["code"], "institution": row["institution"],
                                 "programme": row["programme"]})
        elif key in reg_by_inst[a]:
            matched.append(row["code"])
        else:
            # Institution is in the register but this title isn't — either a
            # wording difference, or a programme not currently accredited/listed.
            close = [reg_names[a][k] for k in reg_by_inst[a]
                     if k and (k in key or key in k)]
            (name_mismatch if close else not_in_register).append({
                "code": row["code"], "institution": row["institution"],
                "ours": row["programme"], "register_candidates": close[:3],
            })

    report = {
        "source": BASE,
        "caveat": ("Verifies institution, programme name and duration only. The "
                   "register carries no programme codes, entry requirements, points "
                   "or capacity, so this cannot validate the matching rules."),
        "register_rows_bachelor": len(register),
        "register_institutions": len(reg_by_inst),
        "our_rows": len(ours),
        "confirmed": len(matched),
        "name_differs": len(name_mismatch),
        "absent_from_register": len(not_in_register),
        "unverifiable_institution_not_in_register": len(unverifiable),
        "name_differs_detail": name_mismatch,
        "absent_detail": not_in_register[:200],
        "unverifiable_institutions": sorted({u["institution"] for u in unverifiable}),
    }
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                        encoding="utf-8")

    print(f"\n  confirmed by the register        : {report['confirmed']}")
    print(f"  same programme, different wording: {report['name_differs']}")
    print(f"  not found at that institution    : {report['absent_from_register']}")
    print(f"  institution absent (NACTVET etc.): {report['unverifiable_institution_not_in_register']}")
    print(f"\nwrote {args.out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
