#!/usr/bin/env python3
"""Extract programme records from the TCU 2026/27 admission guidebook PDF.

Column-aware table extraction (via PyMuPDF word coordinates) + pattern-based
parsing of requirement text into engine slots.

HONESTY CONTRACT
----------------
Only requirement texts that parse CLEANLY against known patterns are accepted
(marked machine_parsed=true). Anything ambiguous — truncated lists, unknown
subjects, unmatched grade-floor sentences, unparseable points — goes to the
review file with its raw text and is NOT served to students. Curated entries
in programmes.json always win over extracted ones on programme-code conflict.

Usage:  python3 scripts/extract_guidebook.py  (from backend/)
Writes: northstar/data/programmes_extracted.json  (accepted entries)
        northstar/data/extraction_review.json    (rejected, with reasons)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

PDF = Path(__file__).resolve().parents[2] / "inputs" / "tcu-undergraduate-admission-guidebook-2026-2027.pdf"
DATA = Path(__file__).resolve().parents[1] / "northstar" / "data"

CODE_RE = re.compile(r"^[A-Z]{2,4}\d{3}$")

# ---- subject vocabulary (longest-match-first) -------------------------------
SUBJECT_VARIANTS: dict[str, str] = {
    "advanced mathematics": "advanced_mathematics",
    "advance mathematics": "advanced_mathematics",
    "advanced mathematic": "advanced_mathematics",
    "mathematics": "advanced_mathematics",
    "computer science": "computer_science",
    "computer studies": "computer_science",
    "physics": "physics",
    "chemistry": "chemistry",
    "biology": "biology",
    "geography": "geography",
    "history": "history",
    "fasihi ya kiswahili": "kiswahili",
    "kiswahili": "kiswahili",
    "english language": "english_language",
    "english": "english_language",
    "literature in english": "literature_in_english",
    "literature": "literature_in_english",
    "economics": "economics",
    "commerce": "commerce",
    "accountancy": "accountancy",
    "accounting": "accountancy",
    "accounts": "accountancy",
    "agriculture": "agriculture",
    "food and human nutrition": "nutrition",
    "food and nutrition": "nutrition",
    "nutrition": "nutrition",
    "fine arts": "fine_arts",
    "fine art": "fine_arts",
    "arabic language": "arabic",
    "arabic": "arabic",
    "french": "french",
    "chinese": "chinese",
    "islamic knowledge": "divinity",
    "divinity": "divinity",
    "physical education": "physical_education",
    "general studies": "general_studies",
    "education": "education",
    "music": "music",
    "theatre arts": "theatre_arts",
    "business studies": "business_studies",
    "business": "business_studies",
}
# tokens that invalidate a principal-pass list if they appear inside it
POISON = ("basic applied mathematics", "basic mathematics", "o-level", "o level")

# ---- tag inference from programme name --------------------------------------
TAG_KEYWORDS = [
    (r"educat", "education"),
    (r"engineer", "engineering"),
    (r"\blaw", "law"),
    (r"medicine|medical|pharma|nursing|midwif|radiograph|clinical|optometry|"
     r"physiotherap|dental|anaesthes|health|prosthetic|laborator", "health"),
    (r"computer|informatic|information tech|software|cyber|\bict\b|data science|"
     r"digital", "ict"),
    (r"account|financ|bank|market|procure|insur|business|entrepreneur|"
     r"human resource|taxation|logistic|supplies|commerce|administration", "business"),
    (r"economic", "economics"),
    (r"agricultur|horticultur|animal|veterinar|food|aquacultur|forestry|fisher|"
     r"irrigat|crop|livestock|agronom|soil", "agriculture"),
    (r"environment|wildlife|conservation", "environment"),
    (r"tourism|hospitality", "business"),
    (r"statistic|actuarial", "ict"),
    (r"language|literature|kiswahili|music|theatre|film|art\b|archaeolog|heritage|"
     r"history|translation|journalism|communication", "arts"),
    (r"sociolog|social|community|development studies|political|public admin|"
     r"gender|psycholog|counsel", "social"),
    (r"science", "science"),
]


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"').replace("''", '"')
    return re.sub(r"\s+", " ", text).strip()


def map_subject(item: str) -> str | None:
    item = norm(item).lower().strip(" .;:")
    item = re.sub(r"\bat a[- ]level\b", "", item).strip()
    for variant in sorted(SUBJECT_VARIANTS, key=len, reverse=True):
        if item == variant:
            return SUBJECT_VARIANTS[variant]
    return None


def parse_subject_list(text: str) -> list[str] | None:
    """Parse 'History, Geography, Kiswahili or English Language' -> ids.
    Returns None if any item is unrecognized."""
    low = norm(text).lower()
    if any(p in low for p in POISON):
        return None
    parts = re.split(r",|\bor\b|\band\b|/", low)
    out: list[str] = []
    for p in parts:
        p = p.strip(" .;:")
        if not p:
            continue
        sid = map_subject(p)
        if sid is None:
            return None
        if sid not in out:
            out.append(sid)
    return out or None


GRADE_FLOOR_RE = re.compile(
    r"(?:minimum of|at least|not below)\s*a?\s*[\"']([A-E])[\"']?\s*grade\s+(?:or above\s+)?in\s+([^.]+)",
    re.IGNORECASE,
)
PTS_IN_TEXT_RE = re.compile(r"minimum of\s+(\d+(?:\.\d+)?)\s+points", re.IGNORECASE)
WORDNUM = {"two": 2, "three": 3, "one": 1}


def parse_requirement(text: str) -> tuple[list[dict] | None, float | None, list[str], str]:
    """Returns (slots, min_points_from_text, additional_sentences, fail_reason)."""
    text = norm(text)
    sentences = [s.strip() for s in re.split(r"(?<=[.])\s+", text) if s.strip()]
    if not sentences:
        return None, None, [], "empty requirement text"
    first = sentences[0].rstrip(".")
    rest = sentences[1:]

    pts = None
    m = PTS_IN_TEXT_RE.search(first)
    if m:
        pts = float(m.group(1))
        first = PTS_IN_TEXT_RE.sub("", first).strip(" ,;")
        first = re.sub(r"\bwith a?\s*$", "", first).strip(" ,;")

    slots: list[dict] | None = None
    low = first.lower()
    # parenthetical floor: "two principal passes (d grade and above) in ..."
    paren_floor = None
    pm = re.search(r"\(\s*[\"']?([a-e])[\"']?\s*grade\s*(?:and|or)\s*above\s*\)", low)
    if pm:
        paren_floor = pm.group(1).upper()
        low = low[: pm.start()].rstrip() + " " + low[pm.end():].lstrip()
    low = re.sub(r"\bat a[- ]levels?\b", "", low)
    low = re.sub(r"\s+", " ", low).strip()

    # Shape B1: "N principal passes[,] one (of which must be|in) [grade] LIST [+ one in LIST2]"
    m = re.match(
        r"^(two|three) principal(?: level)? passes?,? one (?:of which must be|in)\s*"
        r"(?:at\s*)?(?:a\s*)?(?:minimum of\s*)?(?:[\"']([a-e])[\"']?\s*grade\s*)?(?:or above\s*)?"
        r"(?:in\s+)?(?:the following subjects?:?\s*)?(?P<l1>.+?)"
        r"(?:\s+and (?:a principal pass\s+)?(?:in\s+)?one (?:of|in)\s+(?:the following subjects?:?\s*)?(?P<l2>.+))?$",
        low,
    )
    if m:
        n = WORDNUM[m.group(1)]
        l1 = parse_subject_list(m.group("l1"))
        if l1:
            s1 = {"choose": 1, "from": l1}
            if m.group(2):
                s1["min_grade"] = m.group(2).upper()
            slots = [s1]
            if m.group("l2"):
                l2 = parse_subject_list(m.group("l2"))
                if not l2:
                    return None, pts, rest, f"unparsed second list: {m.group('l2')!r}"
                slots.append({"choose": n - 1, "from": l2})
            else:
                slots.append({"choose": n - 1, "from": "any"})

    # Shape B2: "N principal passes in X[/Y] and [in] one of the following: LIST"
    if slots is None:
        m = re.match(
            r"^(two|three) principal(?: level)? passes? in (?P<req>[^,]+?) and\s+"
            r"(?:in\s+)?(?:a principal pass from\s+)?one of (?:the following(?: subjects)?:?\s*)?(?P<l2>.+)$",
            low,
        )
        if m:
            n = WORDNUM[m.group(1)]
            req_list = parse_subject_list(m.group("req"))
            l2 = parse_subject_list(m.group("l2"))
            if req_list and l2:
                slots = [{"choose": 1, "from": req_list}, {"choose": n - 1, "from": l2}]

    # Shape C: "three principal passes in A, B and (either) C or D or E"
    if slots is None:
        m = re.match(
            r"^three principal(?: level)? passes? in (?P<a>[^,]+?),\s*(?P<b>[^,]+?),?\s+and\s+(?:either\s+)?(?P<c>.+)$",
            low,
        )
        if m:
            a, b = map_subject(m.group("a")), map_subject(m.group("b"))
            c = parse_subject_list(m.group("c"))
            if a and b and c:
                slots = [
                    {"choose": 1, "from": [a]},
                    {"choose": 1, "from": [b]},
                    {"choose": 1, "from": c},
                ]

    # Shape B3: "N principal passes in SUBJ and either LIST" (or-list)
    if slots is None:
        m = re.match(
            r"^(two|three) principal(?: level)? passes? in (?P<req>[^,]+?) and (?:either\s+)?(?P<l2>.+)$",
            low,
        )
        if m and re.search(r"\bor\b|/", m.group("l2")):
            n = WORDNUM[m.group(1)]
            req_s = map_subject(m.group("req"))
            l2 = parse_subject_list(m.group("l2"))
            if req_s and l2:
                slots = [{"choose": 1, "from": [req_s]}, {"choose": n - 1, "from": l2}]

    # Shape A: "N principal passes in [any of] [the following subjects:] LIST"
    if slots is None:
        m = re.match(
            r"^(two|three) principal(?: level)? passes?(?: at [\"']?([a-e])[\"']? grade(?: or above)?)?"
            r" (?:in|of|from)\s+"
            r"(?:any (?:two |three )?of\s+)?(?:the following subjects?:?\s*)?(?P<list>.+)$",
            low,
        )
        if m:
            n = WORDNUM[m.group(1)]
            floor = m.group(2).upper() if m.group(2) else None
            raw_list = m.group("list")
            items = parse_subject_list(raw_list)
            if items:
                has_or = re.search(r"\bor\b|/", raw_list.lower()) is not None
                is_comma_list = "," in raw_list
                if not has_or and not is_comma_list and len(items) == n:
                    # "in Advanced Mathematics and Physics" = each required
                    slots = [{"choose": 1, "from": [s]} for s in items]
                elif (has_or or is_comma_list) and len(items) >= n:
                    # guidebook uses "A, B, C and D" as a choice list too
                    slots = [{"choose": n, "from": items}]
                else:
                    return None, pts, rest, f"ambiguous list arity: {raw_list!r}"
                if floor:
                    for s in slots:
                        s["min_grade"] = floor

    if slots is None:
        return None, pts, rest, f"no pattern matched: {first!r}"
    if paren_floor:
        for s in slots:
            s.setdefault("min_grade", paren_floor)

    # Grade-floor sentences among the rest (e.g. MD's 'minimum of "D" grade in ...')
    additional: list[str] = []
    for s in rest:
        fm = GRADE_FLOOR_RE.search(s)
        applied = False
        if fm:
            floor, floor_subjects = fm.group(1).upper(), parse_subject_list(fm.group(2))
            if floor_subjects:
                for slot in slots:
                    if slot["from"] != "any" and set(slot["from"]) <= set(floor_subjects):
                        slot["min_grade"] = floor
                        applied = True
                if not applied:
                    return None, pts, rest, f"grade floor did not match slots: {s!r}"
        if not applied:
            additional.append(s)
    return slots, pts, additional, ""


def infer_tags(name: str) -> list[str]:
    low = name.lower()
    tags = [tag for pat, tag in TAG_KEYWORDS if re.search(pat, low)]
    seen: list[str] = []
    for t in tags:
        if t not in seen:
            seen.append(t)
    return seen[:3]


def parse_points_cell(text: str) -> tuple[float | None, str]:
    text = norm(text).lower().replace(" .", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*from\s*3", text)
    if m:
        return float(m.group(1)), "best_three"
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if m:
        return float(m.group(1)), "slots"
    return None, "slots"


# ---- PDF table extraction ----------------------------------------------------

def extract_rows(doc: fitz.Document) -> list[dict]:
    rows: list[dict] = []
    HEADER_VOCAB = {"S/N", "SN", "Programme", "Programm", "Code", "Admission",
                    "Requirements", "Minimum", "Institutional", "Points",
                    "Capacity", "Duration", "(Yrs)", "Yrs", "e"}
    for pno in range(15, doc.page_count):
        page = doc[pno]
        words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,wno
        code_hdr = next((w for w in words if w[4] == "Code"), None)
        if code_hdr is None:
            continue
        code_y = code_hdr[1]
        # header words live in a band around the "Code" line (headers stack
        # multiple lines, e.g. "Minimum / Institutional / Admission / Points")
        band = [w for w in words if abs(w[1] - code_y) < 55 and w[4] in HEADER_VOCAB]
        header_bottom = max((w[3] for w in band), default=code_y + 12)
        header_top = min((w[1] for w in band), default=code_y)

        def hx(word: str, pick=min) -> float | None:
            xs = [w[0] for w in band if w[4] == word]
            return pick(xs) if xs else None

        pts_x = hx("Points")
        cap_x = hx("Capacity")
        dur_x = hx("Duration")
        if pts_x is None or cap_x is None:
            continue
        if dur_x is None:
            dur_x = cap_x + 60

        # institution header = the non-numeric text just above the table header
        inst_words = [w[4] for w in words if w[1] < header_top - 2 and not re.match(r"^\d+$", w[4])]
        inst_text = norm(" ".join(inst_words))
        # drop the running page header if present
        inst_text = re.sub(r"^Bachelor's Degree Admission Guidebook.*?Qualifications\)\s*", "", inst_text)
        im = re.search(r"([A-Z][^()]*?\([A-Za-z .&'-]+\))\s*,?\s*([A-Za-z' -]+?)(?:\s*Campus)?(?:\s*S/?N)?$", inst_text)
        institution = im.group(1).strip() if im else None
        location = im.group(2).strip() if im else None

        body = [w for w in words if w[1] > header_bottom + 2]

        # The code column is the one reliably-positioned reference: detect the
        # actual code words under the (center-aligned) "Code" header and derive
        # the prog|code|req boundaries from THEIR real x-extent. The numeric
        # right-hand columns use their header left edges with margin (headers
        # there are near-left-aligned and cells are short numbers).
        code_words = [
            w for w in body
            if CODE_RE.match(w[4]) and code_hdr[0] - 45 <= w[0] <= code_hdr[0] + 60
        ]
        if not code_words:
            continue
        code_left = min(w[0] for w in code_words) - 4
        code_right = max(w[2] for w in code_words) + 1

        def col_of(x0: float) -> str:
            if x0 >= dur_x - 10:
                return "dur"
            if x0 >= cap_x - 10:
                return "cap"
            if x0 >= pts_x - 10:
                return "pts"
            if x0 >= code_right:
                return "req"
            if x0 >= code_left:
                return "code"
            return "prog"
        codes = sorted(code_words, key=lambda w: w[1])
        for i, cw in enumerate(codes):
            # each row's content starts on the code's own line (top-aligned)
            top = cw[1] - 3
            bot = codes[i + 1][1] - 3 if i + 1 < len(codes) else page.rect.height
            cells: dict[str, list] = {k: [] for k in ("prog", "req", "pts", "cap", "dur")}
            for w in body:
                if top <= w[1] < bot:
                    c = col_of(w[0])
                    if c in cells:
                        cells[c].append(w)
            def cell_text(c):
                # sort into visual lines (3pt y-buckets) then left-to-right;
                # strip stray page numbers that fall into the last row's cell
                t = norm(" ".join(w[4] for w in sorted(cells[c], key=lambda w: (round(w[1] / 3), w[0]))))
                return re.sub(r"\s+\d{1,3}$", "", t)
            rows.append({
                "page": pno + 1,
                "institution": institution,
                "location": location,
                "code": cw[4],
                "name": norm(re.sub(r"\b\d{1,3}\.?\s*", "", cell_text("prog"))),
                "requirement_text": cell_text("req"),
                "points_cell": cell_text("pts"),
                "capacity_cell": cell_text("cap"),
                "duration_cell": cell_text("dur"),
            })

    # Backfill missing institution/location from the code prefix, but ONLY
    # when the prefix maps to exactly one (institution, location) pair across
    # the whole book — never guess between campuses.
    by_prefix: dict[str, set[tuple[str, str]]] = {}
    for r in rows:
        if r["institution"]:
            prefix = re.match(r"^[A-Z]+", r["code"]).group()
            by_prefix.setdefault(prefix, set()).add((r["institution"], r["location"] or ""))
    for r in rows:
        if not r["institution"]:
            prefix = re.match(r"^[A-Z]+", r["code"]).group()
            pairs = by_prefix.get(prefix, set())
            if len(pairs) == 1:
                r["institution"], r["location"] = next(iter(pairs))
    return rows


def build(rows: list[dict], curated_codes: set[str], known_subjects: set[str]) -> tuple[list[dict], list[dict]]:
    accepted, review = [], []
    seen_codes: set[str] = set()

    def reject(row, why):
        review.append({"why": why, **{k: row[k] for k in ("page", "institution", "code", "name", "requirement_text", "points_cell")}})

    for row in rows:
        code = row["code"]
        if code in curated_codes:
            continue  # curated (human-verified) always wins
        if code in seen_codes:
            reject(row, "duplicate code (continuation row?)")
            continue
        if not row["institution"] or not row["name"] or len(row["name"]) < 4:
            reject(row, "missing institution or name")
            continue
        slots, pts_text, additional, fail = parse_requirement(row["requirement_text"])
        if slots is None:
            reject(row, f"requirement not cleanly parsed: {fail}")
            continue
        for s in slots:
            if s["from"] != "any" and not set(s["from"]) <= known_subjects:
                slots = None
                break
        if slots is None:
            reject(row, "unknown subject id in parsed slots")
            continue
        cell_pts, basis = parse_points_cell(row["points_cell"])
        min_points = cell_pts if cell_pts is not None else pts_text
        if min_points is None:
            reject(row, f"no minimum points found: {row['points_cell']!r}")
            continue
        tags = infer_tags(row["name"])
        if not tags:
            reject(row, "no tags inferrable from name (interest mapping would fail)")
            continue
        cap_m = re.search(r"\d+", row["capacity_cell"])
        dur_m = re.search(r"\d+(?:\.\d+)?", row["duration_cell"])
        slug = re.sub(r"[^a-z0-9]+", "-", row["name"].lower()).strip("-")[:60]
        seen_codes.add(code)
        accepted.append({
            "id": f"{code.lower()}-{slug}",
            "code": code,
            "name": row["name"],
            "institution": row["institution"],
            "location": row["location"] or "",
            "tags": tags,
            "requirement_text": row["requirement_text"],
            "slots": slots,
            "min_points": min_points,
            "points_basis": basis,
            "additional_requirements": additional,
            "capacity": int(cap_m.group()) if cap_m else None,
            "duration_years": float(dur_m.group()) if dur_m else None,
            "checklist": {"what_is_it": None, "cost": None, "time_to_employment": None, "salary": None, "insider_notes": None},
            "source": f"TCU 2026/27 guidebook, PDF p.{row['page']} ({row['institution']})",
            "machine_parsed": True,
        })
    return accepted, review


def main() -> int:
    curated = json.loads((DATA / "programmes.json").read_text())
    curated_codes = {p["code"] for p in curated["programmes"]}
    subjects = {s["id"] for s in json.loads((DATA / "subjects.json").read_text())["subjects"]}

    doc = fitz.open(PDF)
    rows = extract_rows(doc)
    accepted, review = build(rows, curated_codes, subjects)

    (DATA / "programmes_extracted.json").write_text(json.dumps({
        "description": "Machine-extracted from the TCU 2026/27 guidebook by scripts/extract_guidebook.py. "
                       "Only cleanly parsed entries are included (see extraction_review.json for the rest). "
                       "Curated programmes.json wins on any code conflict.",
        "stats": {"rows_found": len(rows), "accepted": len(accepted),
                  "needs_review": len(review), "curated_skipped": len(curated_codes)},
        "programmes": accepted,
    }, indent=1, ensure_ascii=False) + "\n")
    (DATA / "extraction_review.json").write_text(json.dumps({
        "description": "Rows NOT served to students: requirement text did not parse cleanly. "
                       "Each keeps its raw text + page for human review/promotion into programmes.json.",
        "rows": review,
    }, indent=1, ensure_ascii=False) + "\n")

    print(f"rows found:    {len(rows)}")
    print(f"accepted:      {len(accepted)}")
    print(f"needs review:  {len(review)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
