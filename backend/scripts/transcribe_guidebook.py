#!/usr/bin/env python3
"""Transcribe the TCU guidebook's programme tables — completely and verifiably.

This is a TRANSCRIPTION pass, not an interpretation pass. It reproduces what the
guidebook says, verbatim, into CSV and JSON. It does not parse requirement prose
into rules — that is `extract_guidebook.py`'s job, and keeping the two separate is
the point of this script.

Why it exists
-------------
`extract_guidebook.py` detected rows by matching programme codes against
``^[A-Z]{2,4}\\d{3}$``. Codes shaped CBD01 / SUM01 / CBMZ1 never matched, so whole
pages were abandoned by ``if not code_words: continue`` — silently. 190 programmes
were neither served nor quarantined nor logged. The corpus looked healthy because
the thing measuring its health sat downstream of the thing that failed.

Two design rules follow from that, and both matter more than tidy output:

1. **Rows are found from the PDF's own ruled table cells** (``page.find_tables()``),
   not from guesses about column x-positions or code shape. The guidebook's tables
   are ruled, so the structure is already in the file; inferring it was the mistake.

2. **Nothing is ever dropped in silence.** Every page is classified, every table is
   classified, and a row that cannot be read cleanly is still emitted — with its
   problem recorded on it. Absence of output must always be accompanied by a stated
   reason, because the failure this replaces was silence, not inaccuracy.

Completeness is checked against an oracle that is *independent of anything above*:
each institution's table numbers its own rows in an S/N column. If a run of S/N
values is not contiguous, rows were lost — and we can say exactly how many and where.

Usage
-----
    python scripts/transcribe_guidebook.py [--pdf PATH] [--outdir DIR]

Writes ``guidebook_programmes.csv``, ``guidebook_programmes.json`` and
``guidebook_coverage.json``.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

import fitz  # PyMuPDF

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PDF = REPO / "inputs" / "tcu-undergraduate-admission-guidebook-2026-2027.pdf"
DEFAULT_OUT = REPO / "backend" / "northstar" / "data"

# The seven columns of a programme table, in order. Matching is fuzzy because the
# guidebook's own headers are inconsistent: "S/N", "SN" and "S/ N" all occur, and
# "Admission Capacity" is sometimes split as "Admissio n Capacity" by the PDF's
# text layer. Anchoring on exact strings is what brittleness looks like.
COLUMNS = ("sn", "programme", "code", "requirements", "points", "capacity", "duration")

_SN_HEADER = re.compile(r"^s\s*/?\s*n$")
_WS = re.compile(r"\s+")


def norm(text: str | None) -> str:
    """Collapse whitespace. Deliberately does nothing else — this is transcription."""
    return _WS.sub(" ", (text or "").replace("\n", " ")).strip()


def merge_header_block(grid: list[list[str | None]], start: int) -> list[str]:
    """Fold a multi-row header into one row of per-column text.

    The guidebook stacks headers: "Minimum" sits on the header row while
    "Institutional / Admission / Points" continue on the rows beneath it. Reading
    only the first row loses the word "Points" entirely, which is why pages 46 and
    190 reported a missing points column. Consume rows until one carries an S/N
    value (the first data row).
    """
    width = max(len(r) for r in grid[start:start + 4]) if grid[start:] else 0
    merged = [""] * width
    for row in grid[start:start + 4]:
        cells = [norm(c) for c in row]
        # The first cell holding a bare number starts the data; stop before it.
        if any(re.match(r"^\d{1,3}[.,)]?$", c) for c in cells[:2] if c):
            break
        for i, c in enumerate(cells):
            if c:
                merged[i] = f"{merged[i]} {c}".strip() if merged[i] else c
    return merged


def map_columns(row: list[str | None]) -> dict[str, int] | None:
    """Map each logical column to its index in *this* table's header row.

    Column POSITIONS are not stable across the guidebook: PyMuPDF returns 7-column
    grids on most pages but 8, 9 and 17-column ones where the PDF carries extra
    ruled sub-divisions. The header LABELS are stable, so match on those and read
    data cells through the resulting map. Assuming fixed positions is what made
    pages 50-51 (CBD13-CBD20) look like "not a programme table".

    Returns None if this row is not a programme-table header.
    """
    if not row:
        return None
    cells = [norm(c).lower() for c in row]
    found: dict[str, int] = {}
    for i, c in enumerate(cells):
        if not c:
            continue
        # Order matters: "Programme Duration (Yrs)" contains both words, so the
        # more specific label has to win before "programme" is considered.
        if "duration" in c:
            found.setdefault("duration", i)
        elif "capacity" in c:
            found.setdefault("capacity", i)
        elif "points" in c:
            found.setdefault("points", i)
        elif "requirement" in c:
            found.setdefault("requirements", i)
        elif c == "code":
            found.setdefault("code", i)
        elif "programme" in c or "programm" in c:
            found.setdefault("programme", i)
        elif _SN_HEADER.match(c) or c in {"s/n", "sn"}:
            found.setdefault("sn", i)
    # Identify a programme table by S/N + Code plus at least one of the descriptive
    # columns. The Programme column is deliberately NOT required: page 280 (Tengeru
    # Institute) omits the word entirely from its header — "Programme" appears only
    # inside "Programme Duration (Yrs)" — yet the column is plainly there in the
    # data. Requiring the label lost the whole institution.
    if not {"sn", "code"} <= found.keys():
        return None
    if not found.keys() & {"requirements", "points", "capacity", "duration"}:
        return None

    # Some headers are mangled past recognition by the PDF's text layer — page 156
    # renders "Admission Capacity" as "Admissio n" and glues "Programme Duration"
    # onto it. The COLUMN ORDER is fixed by the guidebook's layout, so recover an
    # unnamed column positionally: take unclaimed indices lying between its named
    # neighbours. Positional inference is a fallback, never the primary method.
    taken = set(found.values())
    for pos, name in enumerate(COLUMNS):
        if name in found:
            continue
        prev = max((found[c] for c in COLUMNS[:pos] if c in found), default=-1)
        nxt = min((found[c] for c in COLUMNS[pos + 1:] if c in found),
                  default=len(cells))
        gap = [i for i in range(prev + 1, nxt) if i not in taken]
        if gap:
            found[name] = gap[0]
            taken.add(gap[0])
    return found


@dataclass
class Row:
    """One transcribed programme. `problems` is never allowed to be a reason to drop it."""
    page: int                      # 1-based, as printed in citations
    institution: str | None
    sn: str
    programme: str
    code: str
    requirements: str
    points: str
    capacity: str
    duration: str
    problems: list[str] = field(default_factory=list)


@dataclass
class PageReport:
    page: int
    tables: int
    status: str          # "programme_table" | "no_table" | "not_programme_table"
    rows: int = 0
    detail: str = ""


def institution_of(rows: list[list[str | None]], header_idx: int) -> str | None:
    """The institution is the last non-empty cell above the header row.

    The guidebook repeats it at the top of every page a table spans, which is what
    lets a table continue across pages without losing its owner.

    Join every non-empty cell in that row: where the table grid splits the name
    across cells, taking only the first yields a fragment. Page 327 attributed four
    UDOM programmes to an institution called "University", which then read as UDOM
    missing its first four rows.
    """
    for r in range(header_idx - 1, -1, -1):
        parts = [norm(c) for c in rows[r] if norm(c)]
        if parts:
            return " ".join(parts)
    return None


def transcribe(pdf_path: Path) -> tuple[list[Row], list[PageReport]]:
    doc = fitz.open(pdf_path)
    out: list[Row] = []
    reports: list[PageReport] = []
    # Carries the previous row across a page break so wrapped requirement text that
    # continues onto the next page is appended to the row it belongs to.
    last_row: Row | None = None
    last_institution: str | None = None

    for pno in range(doc.page_count):
        page = doc[pno]
        tables = page.find_tables().tables
        printed = pno + 1

        if not tables:
            reports.append(PageReport(printed, 0, "no_table",
                                      detail="no ruled table detected"))
            continue

        page_rows = 0
        classified = False
        # Exactly one report per page. A page carrying both a programme table and
        # some other table must not produce two rows in the coverage report — the
        # report is the completeness record, so its own arithmetic has to hold.
        skipped: list[str] = []
        for tbl in tables:
            grid = tbl.extract()
            if not grid:
                continue
            header_idx = colmap = None
            for i, r in enumerate(grid):
                single = map_columns(r)
                if single:
                    # Merge stacked header rows ONLY when the single row is missing
                    # a column. Merging unconditionally lets a wrapped data row
                    # ("in Nursing" on page 123) leak into the header and displace a
                    # mapping that was already correct. Repair, never routine.
                    colmap = single
                    if len(single) < len(COLUMNS):
                        merged = map_columns(merge_header_block(grid, i))
                        if merged and len(merged) > len(single):
                            colmap = {**merged, **single}
                    header_idx = i
                    break
            if header_idx is None:
                skipped.append(f"{len(grid)}x{len(grid[0])} table with no programme header")
                continue

            classified = True
            institution = institution_of(grid, header_idx) or last_institution
            if institution:
                last_institution = institution

            for raw in grid[header_idx + 1:]:
                cells = [norm(c) for c in raw]
                # Read through the header map, so extra ruled sub-divisions in the
                # PDF shift nothing. A column the header didn't name reads as empty
                # rather than throwing the whole row away.
                def col(name: str) -> str:
                    i = colmap.get(name)
                    return cells[i] if i is not None and i < len(cells) else ""

                shape_problem = ""
                missing_cols = [c for c in COLUMNS if c not in colmap]
                if missing_cols:
                    shape_problem = f"header lacked column(s): {', '.join(missing_cols)}"

                sn, prog, code = col("sn"), col("programme"), col("code")
                req, pts = col("requirements"), col("points")
                cap, dur = col("capacity"), col("duration")
                if not any(cells):
                    continue  # a ruled but wholly empty row carries no information

                # A row with no S/N is wrapped text belonging to the row above.
                if not sn:
                    if last_row is not None:
                        for name, value in zip(COLUMNS[1:], (prog, code, req, pts, cap, dur)):
                            if value:
                                cur = getattr(last_row, _FIELD[name])
                                setattr(last_row, _FIELD[name],
                                        f"{cur} {value}".strip() if cur else value)
                        if shape_problem:
                            last_row.problems.append(shape_problem)
                    else:
                        out.append(Row(printed, institution, "", prog, code, req, pts,
                                       cap, dur,
                                       ["continuation row with no preceding row"]))
                        page_rows += 1
                    continue

                row = Row(printed, institution, sn, prog, code, req, pts, cap, dur)
                if shape_problem:
                    row.problems.append(shape_problem)
                for label, value in (("code", code), ("programme", prog),
                                     ("requirements", req)):
                    if not value:
                        row.problems.append(f"empty {label}")
                out.append(row)
                last_row = row
                page_rows += 1

        if classified:
            reports.append(PageReport(printed, len(tables), "programme_table",
                                      page_rows, "; ".join(skipped)))
        else:
            reports.append(PageReport(
                printed, len(tables), "not_programme_table", 0,
                "; ".join(skipped) or "tables present but none had a programme header"))
    return out, reports


_FIELD = {"programme": "programme", "code": "code", "requirements": "requirements",
          "points": "points", "capacity": "capacity", "duration": "duration"}


def inst_key(name: str | None) -> str:
    """Group institutions for the audit.

    "University of Dodoma ( UDOM)" and "University of Dodoma (UDOM)" are the same
    institution rendered differently by the PDF's text layer. Left unnormalised they
    split into two runs and each reports a phantom "missing 1,2,3,4".
    """
    return _WS.sub(" ", (name or "(unknown)").replace("( ", "(").replace(" )", ")")).strip().lower()


def sn_audit(rows: list[Row], doc: fitz.Document) -> list[dict]:
    """Independent completeness check: each institution numbers its rows 1..N.

    The S/N column is not used to find rows, so this can catch a systematic
    row-detection failure rather than agreeing with it.

    Crucially it separates two very different things. A number missing from our
    output because the guidebook never printed it is the guidebook's gap; a number
    the guidebook prints and we don't have is *our* lost row. Only the second is a
    defect in this script, and conflating them would either hide our bugs or invent
    ones we don't have.
    """
    findings: list[dict] = []
    seen: dict[str, list[tuple[int, int]]] = {}
    labels: dict[str, str] = {}
    for r in rows:
        if not r.sn:
            continue
        key = inst_key(r.institution)
        labels.setdefault(key, r.institution or "(unknown)")
        m = re.match(r"^(\d{1,3})", r.sn)
        if not m:
            findings.append({"institution": r.institution, "page": r.page,
                             "issue": f"unreadable S/N {r.sn!r}"})
            continue
        seen.setdefault(key, []).append((int(m.group(1)), r.page))

    for key, pairs in seen.items():
        nums = [n for n, _ in pairs]
        pages = sorted({p for _, p in pairs})
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if missing:
            # Does the guidebook actually print this number on any of the
            # institution's pages? If not, the sequence skips it at source.
            text = " ".join(doc[p - 1].get_text() for p in pages
                            if 1 <= p <= doc.page_count)
            absent_in_source, lost = [], []
            for n in missing:
                (lost if re.search(rf"(?m)^\s*{n}\s*[.,)]\s*$", text)
                 else absent_in_source).append(n)
            if lost:
                findings.append({"institution": labels[key],
                                 "issue": "rows LOST in transcription",
                                 "missing": lost, "max": max(nums), "pages": pages})
            if absent_in_source:
                findings.append({"institution": labels[key],
                                 "issue": "S/N absent from the guidebook itself",
                                 "missing": absent_in_source, "max": max(nums),
                                 "pages": pages})
        dupes = sorted({n for n in nums if nums.count(n) > 1})
        if dupes:
            findings.append({"institution": labels[key],
                             "issue": "duplicate S/N values",
                             "duplicates": dupes, "pages": pages})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"error: PDF not found: {args.pdf}", file=sys.stderr)
        return 1

    rows, reports = transcribe(args.pdf)
    doc = fitz.open(args.pdf)
    args.outdir.mkdir(parents=True, exist_ok=True)

    csv_path = args.outdir / "guidebook_programmes.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["page", "institution", "sn", "programme", "code",
                    "admission_requirements", "minimum_points", "capacity",
                    "duration_years", "problems"])
        for r in rows:
            w.writerow([r.page, r.institution or "", r.sn, r.programme, r.code,
                        r.requirements, r.points, r.capacity, r.duration,
                        "; ".join(r.problems)])

    json_path = args.outdir / "guidebook_programmes.json"
    json_path.write_text(json.dumps([asdict(r) for r in rows], indent=2,
                                    ensure_ascii=False), encoding="utf-8")

    audit = sn_audit(rows, doc)
    institutions = sorted({r.institution for r in rows if r.institution})
    coverage = {
        "source_pdf": args.pdf.name,
        "pages_total": len(reports),
        "pages_with_programme_table": sum(1 for r in reports if r.status == "programme_table"),
        "pages_without_table": sum(1 for r in reports if r.status == "no_table"),
        "pages_with_other_table": sum(1 for r in reports if r.status == "not_programme_table"),
        "rows_transcribed": len(rows),
        "rows_with_problems": sum(1 for r in rows if r.problems),
        "institutions": len(institutions),
        "sn_audit_findings": audit,
        "pages": [asdict(r) for r in reports],
        "institution_list": institutions,
    }
    (args.outdir / "guidebook_coverage.json").write_text(
        json.dumps(coverage, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"transcribed {len(rows)} rows from {coverage['pages_with_programme_table']} "
          f"pages across {len(institutions)} institutions")
    print(f"  rows carrying a recorded problem : {coverage['rows_with_problems']}")
    print(f"  S/N audit findings               : {len(audit)}")
    print(f"  pages with no table              : {coverage['pages_without_table']}")
    print(f"  pages with a non-programme table : {coverage['pages_with_other_table']}")
    print(f"wrote {csv_path.name}, {json_path.name}, guidebook_coverage.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
