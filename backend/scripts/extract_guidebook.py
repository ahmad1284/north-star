#!/usr/bin/env python3
"""Turn the guidebook's requirement prose into engine rules.

This script **interprets**. It no longer reads the PDF: `transcribe_guidebook.py`
does that, and this consumes its output (`guidebook_programmes.json`, 870 rows).

Why the split. This script used to do both jobs, and finding rows meant matching
programme codes against ``^[A-Z]{2,4}\\d{3}$``. Codes shaped CBD01 / SUM01 / CBMZ1
never matched, so whole pages were abandoned by ``if not code_words: continue``
without recording anything — 190 programmes neither served, nor quarantined, nor
logged. That row-finding code is gone rather than patched: transcription is proved
complete against an independent oracle, so re-deriving rows here would only add a
second way to be wrong.

HONESTY CONTRACT
----------------
Only requirement texts that parse CLEANLY against known patterns are accepted
(marked machine_parsed=true). Anything ambiguous — truncated lists, unknown
subjects, unmatched grade-floor sentences, unparseable points — goes to the
review file with its raw text and is NOT served to students. Curated entries
in programmes.json always win over extracted ones on programme-code conflict.

The asymmetry is deliberate and worth stating: quarantining a programme costs a
student an option they might have had. Serving a mis-parsed rule tells them they
qualify when they do not, and they find that out after applying. Those are not
equally bad, so when a rule is unclear this script refuses it.

Usage:  python3 scripts/extract_guidebook.py  (from backend/)
Reads:  northstar/data/guidebook_programmes.json  (the transcription)
Writes: northstar/data/programmes_extracted.json  (accepted entries)
        northstar/data/extraction_review.json    (rejected, with reasons)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "northstar" / "data"

# ---- subject vocabulary (longest-match-first) -------------------------------
SUBJECT_VARIANTS: dict[str, str] = {
    "basic applied mathematics": "basic_applied_mathematics",
    "basic applied mathematic": "basic_applied_mathematics",  # PDF truncation
    "basic applied maths": "basic_applied_mathematics",
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
    "science and practice of agriculture": "agriculture",
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
# "Basic Mathematics" is an O-level subject and "o-level" clauses are outside
# our input scope; Basic Applied Mathematics is a real A-level subject we now
# model, so it is no longer poison.
POISON = ("basic mathematics", "o-level", "o level")

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
    # Vocabulary gap found in cycle 10: 51 programmes parsed their requirements
    # cleanly and were quarantined ONLY because no tag could be inferred from the
    # name, which would have broken interest mapping. These are whole fields the
    # keyword list simply never named — planning, diplomacy, records management,
    # theology. Each maps onto an EXISTING tag, so `interests.json` and the bridge
    # logic are untouched; this widens what we can describe, not what we assert.
    (r"international relation|diplomacy|governance|leadership|"
     r"development planning|regional planning|population|policy analysis|"
     r"project planning|public relation", "social"),
    (r"records|archiv|achieves|library|information studies|"
     r"information management|auditing|assurance|supply chain|transport", "business"),
    (r"information system", "ict"),
    (r"theolog|religio|islamic studies|divinity|philosoph", "arts"),
    (r"natural resource|disaster|urban and regional|land management|"
     r"land survey|geomatic|geospatial", "environment"),
    (r"science", "science"),
]


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"').replace("''", '"')
    text = re.sub(r"\s+", " ", text).strip()
    # The PDF renders level references inconsistently: "O-Level", "O - Level",
    # "O'level", "A- level". Canonicalise so poison checks and patterns match.
    # The letter stays case-SENSITIVE on purpose: matching a lowercase "a"
    # would rewrite the ordinary article ("achieve a level of skill"). The word
    # itself is case-insensitive so "O-LEVEL" canonicalises too.
    text = re.sub(r"\b([OA])\s*['’-]?\s*(?i:levels?)\b", r"\1-Level", text)
    return text


# Some subject NAMES contain the word "and" ("Science and Practice of
# Agriculture", "Food and Human Nutrition"). Splitting a list on "and" would
# tear them apart and make a choice-list look conjunctive, so protect them
# first by collapsing them to an underscore form (also a valid lookup key).
_AND_NAMES = sorted(
    (v for v in SUBJECT_VARIANTS if " and " in v), key=len, reverse=True
)
SUBJECT_VARIANTS.update({v.replace(" ", "_"): SUBJECT_VARIANTS[v] for v in _AND_NAMES})


def protect_names(text: str) -> str:
    low = text.lower()
    for name in _AND_NAMES:
        low = low.replace(name, name.replace(" ", "_"))
    return low


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
    low = protect_names(norm(text))
    low = re.sub(r"^(?:any\s+)?one of the following subjects?:?\s*", "", low)
    low = re.sub(r"^the following subjects?:?\s*", "", low)
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


# Cross-slot conditions that used to be dropped into additional_requirements
# and therefore never enforced. Only encoded when EVERY subject named is one we
# model — enforcing a partial alternatives list would reject students who
# actually satisfy the guidebook rule.
# A sentence offering an O-level alternative ("... or a D in ordinary level
# Mathematics") is only half-checkable: we never see O-level results, so
# enforcing the A-level half alone would reject students who satisfy the rule.
OLEVEL_ESCAPE_RE = re.compile(r"\bo-level|\bordinary\s+level|\bo\s*'?\s*level", re.IGNORECASE)

MUST_INCLUDE_RE = re.compile(
    r"\bone of the (?:two|three)\s+(?:principal|passes|principal level passes|principal passes)"
    r"[^.]*?\bmust be (?:in|a pass in)\s+(?P<list>[^.]+)",
    re.IGNORECASE,
)
SUBSIDIARY_RE = re.compile(
    r"\bat least a subsidiary(?: level)? pass in\s+(?P<list>[^.]+)",
    re.IGNORECASE,
)
# "must have a principal pass in one of the following subjects: X, Y or Z"
PRINCIPAL_ONE_OF_RE = re.compile(
    r"\bmust have\s+(?:a\s+)?principal pass(?:es)? in one of the following subjects?:?\s*"
    r"(?P<list>[^.]+)",
    re.IGNORECASE,
)
# "a minimum of 'E' grade in either Chemistry or Geography at A-Level"
FLOOR_ONE_OF_RE = re.compile(
    r"minimum of\s*[\"']?([A-E])[\"']?\s*grade\s+in\s+(?:either\s+)?(?P<list>[^.]+?)"
    r"\s*at\s*A-?\s?level",
    re.IGNORECASE,
)
# "If one of the principal passes is not in Advanced Mathematics, an applicant
#  must have a subsidiary pass in Basic Applied Mathematics"
IF_NOT_MATCHED_RE = re.compile(
    r"\bif one of the principal passes?\s*(?:do(?:es)? not include|is not(?: in)?|are not)\s*"
    r"(?P<trigger>[^,]+?)[,.]?\s*(?:an?\s+)?applicant\s+(?:must have|MUST HAVE)\s*"
    r"(?:at least\s+)?a?\s*subsidiary pass in\s*(?P<list>[^.]+)",
    re.IGNORECASE,
)
# "at least C grade in Chemistry and at least D grade in Biology and E grade in
#  Physics, Mathematics, Nutrition, Geography, or Agriculture"
# Each clause is a separate holding requirement with its own floor.
FLOOR_CLAUSE_RE = re.compile(
    r"(?:minimum of\s*|at least\s*)?[\"']?([A-E])[\"']?\s*grades?\s+in\s+"
    r"(?P<list>[^.]+?)(?=\s+and\s+(?:at least\s+|a\s+)?(?:minimum of\s*)?[\"']?[A-E][\"']?\s*grades?\s+in\b|\s*[.$]|$)",
    re.IGNORECASE,
)


# An explicit choice marker overrides the separator: "one of the following:
# Geography, Physics and Advanced Mathematics" is a CHOICE despite the "and".
CHOICE_MARKER_RE = re.compile(r"one of the following|any one of|either|\bone of\b", re.IGNORECASE)


def list_semantics(raw_list: str) -> str:
    """Is this subject list conjunctive ("all of") or a choice ("one of")?

    Decided in ONE place because getting it wrong is a student-facing bug in
    both directions: reading a choice as conjunctive hides real options, and
    reading a conjunction as a choice tells a student they qualify when they
    do not. Detection runs on the name-protected text so that subjects whose
    own names contain "and" are not mistaken for conjunctions.
    """
    protected = protect_names(raw_list)
    if CHOICE_MARKER_RE.search(protected):
        return "choice"
    has_or = bool(re.search(r"\bor\b|/", protected, re.IGNORECASE))
    has_and = bool(re.search(r"\band\b", protected, re.IGNORECASE))
    if has_and and not has_or:
        return "all"
    return "choice"


def extract_constraints(additional: list[str]) -> tuple[list[dict], list[str]]:
    """Pull encodable cross-slot constraints out of prose sentences.

    Returns (constraints, sentences_that_remain_prose). A sentence is only
    consumed when it parses completely; anything else stays visible as an
    unverified condition.
    """
    constraints: list[dict] = []
    remaining: list[str] = []
    for s in additional:
        low = norm(s)
        # never encode advisory language as a hard rule
        if re.search(r"preference|priority|may be considered", low, re.I):
            remaining.append(s)
            continue
        # A sentence offering an O-level alternative is only half-checkable,
        # whichever pattern would match it — guard once, for every branch.
        if OLEVEL_ESCAPE_RE.search(low):
            remaining.append(s)
            continue
        consumed = False
        for rx in (MUST_INCLUDE_RE, PRINCIPAL_ONE_OF_RE):
            m = rx.search(low)
            if m:
                subs = parse_subject_list(m.group("list"))
                if subs:
                    constraints.append(
                        {"kind": "must_include", "subjects": subs, "source_text": s}
                    )
                    consumed = True
                    break
        if not consumed:
            m = FLOOR_ONE_OF_RE.search(low)
            if m:
                subs = parse_subject_list(m.group("list"))
                if subs:
                    # "must have a minimum of 'E' in either Chemistry or
                    # Geography" is a HOLDING requirement — the subject need
                    # not be one of the passes counted toward the slots — so it
                    # is subsidiary_from with a floor, not must_include.
                    constraints.append({
                        "kind": "subsidiary_from", "subjects": subs,
                        "min_grade": m.group(1).upper(), "source_text": s,
                    })
                    consumed = True
        # Conditional: "if one of the principal passes is not X, need subsidiary in Y".
        # Skip when there is an O-level escape clause — we can't check that half.
        if not consumed:
            m = IF_NOT_MATCHED_RE.search(low)
            if m:
                trig = parse_subject_list(m.group("trigger"))
                subs = parse_subject_list(m.group("list"))
                if trig and subs:
                    constraints.append({
                        "kind": "if_not_matched_subsidiary", "subjects": subs,
                        "trigger_subjects": trig, "source_text": s,
                    })
                    consumed = True

        # Multi-clause floors: "C grade in Chemistry and D grade in Biology and
        # E grade in Physics, Maths, ..." -> one holding requirement per clause.
        if not consumed:
            clauses = FLOOR_CLAUSE_RE.findall(low)
            if len(clauses) >= 2:
                parsed = [(g, raw, parse_subject_list(raw)) for g, raw in clauses]
                if all(subs for _, _, subs in parsed):
                    for grade, raw, subs in parsed:
                        # "D grades in Chemistry and Biology" needs BOTH;
                        # "E grade in Physics, Maths or Geography" needs one.
                        kind = (
                            "subsidiary_all"
                            if list_semantics(raw) == "all" and len(subs) > 1
                            else "subsidiary_from"
                        )
                        constraints.append({
                            "kind": kind, "subjects": subs,
                            "min_grade": grade.upper(), "source_text": s,
                        })
                    consumed = True

        if not consumed:
            m = SUBSIDIARY_RE.search(low)
            # Only when the sentence has no O-level fallback clause ("subsidiary
            # OR an O-level grade" is not fully checkable), and only when the
            # alternatives are joined by "or" — "Physics and Mathematics" means
            # BOTH, and encoding it as a choice would be too permissive.
            if m:
                raw_list = m.group("list")
                subs = parse_subject_list(raw_list)
                if subs:
                    kind = (
                        "subsidiary_all"
                        if list_semantics(raw_list) == "all" and len(subs) > 1
                        else "subsidiary_from"
                    )
                    constraints.append(
                        {"kind": kind, "subjects": subs, "source_text": s}
                    )
                    consumed = True
        if not consumed:
            remaining.append(s)
    return constraints, remaining


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

INSTITUTION_RE = re.compile(
    r"^(.*?\([A-Za-z .&'-]+\)|.*?University|.*?College|.*?Institute|.*?Academy|.*?Centre)"
    r"\s*[,-]?\s*(.*)$")


def split_institution(full: str) -> tuple[str, str]:
    """Split "Ardhi University (ARU), Dar es Salaam" into institution + location.

    The transcription keeps the guidebook's own string intact, which is the right
    thing for a verbatim record but not what the engine wants. Splitting here, at
    the point of interpretation, keeps the transcription faithful.
    """
    full = (full or "").strip()
    m = INSTITUTION_RE.match(full)
    if not m:
        return full, ""
    inst, loc = m.group(1).strip().rstrip(","), m.group(2).strip()
    loc = re.sub(r"\s*Campus\s*$", "", loc).strip(" ,-")
    return inst, loc


def rows_from_transcription() -> list[dict]:
    """Adapt transcription rows to the shape `build()` expects.

    Rows carrying a recorded transcription problem are passed through anyway —
    `build()` decides what is servable, and a row that failed transcription will
    fail parsing too and land in the review file with a reason. Dropping it here
    would remove it from BOTH outputs, which is exactly the silent loss this
    pipeline was rebuilt to prevent.
    """
    src = DATA / "guidebook_programmes.json"
    if not src.exists():
        raise SystemExit(
            f"error: {src} missing — run scripts/transcribe_guidebook.py first")
    rows = []
    for r in json.loads(src.read_text(encoding="utf-8")):
        institution, location = split_institution(r["institution"])
        rows.append({
            "page": r["page"],
            "institution": institution,
            "location": location,
            "code": r["code"],
            "name": r["programme"],
            "requirement_text": r["requirements"],
            "points_cell": r["points"],
            "capacity_cell": r["capacity"],
            "duration_cell": r["duration"],
        })
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
        constraints, additional = extract_constraints(additional)
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
            "constraints": constraints,
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

    rows = rows_from_transcription()
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
