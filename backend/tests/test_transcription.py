"""Tests for the full-guidebook transcription pass.

Why this file exists: the bug this cycle fixes was **silence**, not inaccuracy.
`extract_guidebook.py` matched programme codes against `^[A-Z]{2,4}\\d{3}$`, so
pages whose codes were shaped `CBD01` produced no rows and were skipped by
`if not code_words: continue` without a word. 190 programmes ended up neither
served, nor quarantined, nor logged — invisible to the very mechanism built to
keep gaps visible.

So these tests are aimed at the *completeness claim*, not the happy path. A
transcriber that is confidently wrong about its own coverage would be worse than
the one it replaces, so the assertions below try to catch that specifically:

* the header mapper must survive the real malformations in the guidebook, including
  the one that hid an entire institution (page 280 omits the word "Programme");
* the S/N audit must distinguish rows *we* lost from numbers the guidebook itself
  never printed — collapsing those two would either hide our bugs or invent ones;
* the committed output must still account for an **independent** extraction of the
  same document (the prior-art catalog), which is what surfaced the original bug.

The unit tests import the module directly; the coverage tests read the committed
artifacts, so neither needs the 376-page PDF.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from transcribe_guidebook import (  # noqa: E402
    inst_key,
    institution_of,
    map_columns,
    merge_header_block,
    norm,
)

DATA = Path(__file__).resolve().parents[1] / "northstar" / "data"
PRIOR_ART = (Path(__file__).resolve().parents[2] / "prior-art" / "kazikijana"
             / "src" / "data" / "tcu_catalog.json")

STANDARD_HEADER = ["S/N", "Programme", "Code", "Admission Requirements",
                   "Minimum Institutional Admission Points", "Admission Capacity",
                   "Programme Duration (Yrs)"]


@pytest.fixture(scope="module")
def rows():
    return json.loads((DATA / "guidebook_programmes.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def coverage():
    return json.loads((DATA / "guidebook_coverage.json").read_text(encoding="utf-8"))


# --- header mapping ---------------------------------------------------------

def test_standard_header_maps_all_seven_columns():
    m = map_columns(STANDARD_HEADER)
    assert m == {"sn": 0, "programme": 1, "code": 2, "requirements": 3,
                 "points": 4, "capacity": 5, "duration": 6}


def test_programme_duration_does_not_steal_the_programme_column():
    """"Programme Duration (Yrs)" contains "programme"; the specific label must win."""
    m = map_columns(STANDARD_HEADER)
    assert m["programme"] == 1 and m["duration"] == 6


@pytest.mark.parametrize("sn_label", ["S/N", "SN", "S/ N", "s/n"])
def test_sn_header_spelling_variants(sn_label):
    """All three spellings occur in the guidebook; "S/ N" (page 125) is split by
    the PDF's text layer and previously defeated exact matching."""
    header = [sn_label] + STANDARD_HEADER[1:]
    assert map_columns(header) is not None


def test_extra_ruled_columns_do_not_shift_the_mapping():
    """Pages 50-51 return 9-column grids with empty sub-divisions. Reading by
    position lost CBD13-CBD20; reading by label must not."""
    header = ["SN", "Programme", "", "", "Code", "Admission Requirements",
              "Minimum Institutional Admission Points", "Admission Capacity",
              "Programme Duration (Yrs)"]
    m = map_columns(header)
    assert m["sn"] == 0 and m["programme"] == 1 and m["code"] == 4
    assert m["requirements"] == 5 and m["duration"] == 8


def test_header_without_the_word_programme_is_still_a_programme_table():
    """Page 280 (Tengeru Institute) omits "Programme" from its header entirely —
    the word appears only inside "Programme Duration (Yrs)". Requiring the label
    silently dropped the whole institution."""
    header = ["S/N", "Code", "Admission Requirements",
              "Minimum Institutional Admission Points", "Admission Capacity",
              "Programme Duration (Yrs)"]
    m = map_columns(header)
    assert m is not None
    assert m["sn"] == 0 and m["code"] == 1


def test_non_programme_tables_are_rejected():
    for header in ([], ["Item", "Description"], ["S/N", "Name", "Address"],
                   ["Fee", "Amount"]):
        assert map_columns(header) is None


def test_code_column_alone_is_not_enough():
    """S/N + Code with no descriptive column is not a programme table."""
    assert map_columns(["S/N", "Code"]) is None


# --- stacked headers --------------------------------------------------------

def test_merge_header_block_recovers_stacked_labels():
    """Page 46 stacks "Minimum / Institutional / Admission / Points" down four
    rows, so the word "Points" never appears on the header row itself."""
    grid = [
        ["S/N", "Programme", "Code", "Admission Requirements", "Minimum",
         "Admission Capacity", "Programme Duration (Yrs)"],
        ["", "", "", "", "Institutional", "", ""],
        ["", "", "", "", "Admission Points", "", ""],
        ["1.", "Bachelor of X", "WM001", "Two principal passes", "4.0", "50", "3"],
    ]
    merged = merge_header_block(grid, 0)
    assert "points" in merged[4].lower()
    assert map_columns(merged)["points"] == 4


def test_merge_header_block_stops_at_the_first_data_row():
    """It must not swallow data. Page 123 has a wrapped programme name directly
    under the header; merging it in displaced a mapping that was already correct."""
    grid = [
        ["S/N", "Programme", "Code", "Admission Requirements",
         "Minimum Institutional Admission Points", "Admission Capacity",
         "Programme Duration (Yrs)"],
        ["1.", "Bachelor of Science", "KC001", "Three principal passes", "6.0",
         "96", "3"],
    ]
    merged = merge_header_block(grid, 0)
    assert "Bachelor of Science" not in " ".join(merged)
    assert map_columns(merged)["requirements"] == 3


# --- institution attribution -----------------------------------------------

def test_institution_joins_cells_split_across_the_row():
    """Page 327 split "University of Dodoma (UDOM), Dodoma" across cells. Taking
    only the first yielded an institution called "University", which then read as
    UDOM missing its first four programmes."""
    grid = [["University", "of Dodoma (UDOM),", "Dodoma", "", "", "", ""],
            STANDARD_HEADER]
    assert institution_of(grid, 1) == "University of Dodoma (UDOM), Dodoma"


def test_institution_is_none_when_nothing_precedes_the_header():
    assert institution_of([STANDARD_HEADER], 0) is None


def test_inst_key_normalises_spacing_inside_parentheses():
    """"( UDOM)" and "(UDOM)" are the same institution; left split they each
    report a phantom run of missing S/N values."""
    assert inst_key("University of Dodoma ( UDOM), Dodoma") == \
           inst_key("University of Dodoma (UDOM), Dodoma")


def test_norm_collapses_whitespace_and_newlines_only():
    assert norm("  Bachelor  of\nScience ") == "Bachelor of Science"
    assert norm(None) == ""
    # transcription must not alter content beyond whitespace
    assert norm("C grade; D grade.") == "C grade; D grade."


# --- the completeness claim -------------------------------------------------

def test_no_rows_were_lost_in_transcription(coverage):
    """The headline guarantee. The S/N oracle is independent of how rows are
    found, so a systematic row-detection failure shows up here rather than
    agreeing with itself."""
    lost = [f for f in coverage["sn_audit_findings"] if "LOST" in f["issue"]]
    assert lost == [], f"rows lost: {lost}"


def test_audit_separates_source_gaps_from_our_losses(coverage):
    """Remaining findings must be the guidebook's own numbering skips — verified
    against the PDF text — not unexplained absences."""
    issues = {f["issue"] for f in coverage["sn_audit_findings"]}
    assert issues <= {"S/N absent from the guidebook itself"}, issues


def test_every_row_is_accounted_for(rows, coverage):
    assert coverage["rows_transcribed"] == len(rows)
    assert len(rows) > 850


def test_no_row_carries_an_unresolved_problem(rows):
    """A row that cannot be read cleanly is still emitted, with the problem on it.
    Zero is the current state; a regression here means output quality slipped."""
    flagged = [(r["page"], r["code"], r["problems"]) for r in rows if r["problems"]]
    assert flagged == [], f"rows with problems: {flagged[:5]}"


def test_every_page_is_classified(coverage):
    """No page may be skipped in silence — that was the original defect."""
    assert len(coverage["pages"]) == 376
    assert all(p["status"] in {"programme_table", "no_table", "not_programme_table"}
               for p in coverage["pages"])
    counted = (coverage["pages_with_programme_table"]
               + coverage["pages_without_table"]
               + coverage["pages_with_other_table"])
    assert counted == len(coverage["pages"])


def test_programme_codes_are_unique(rows):
    codes = [r["code"] for r in rows if r["code"]]
    dupes = {c for c in codes if codes.count(c) > 1}
    assert not dupes, f"duplicate codes: {sorted(dupes)[:10]}"


def test_core_fields_are_populated(rows):
    """Transcription is only useful if the cells actually carry content."""
    for field in ("code", "programme", "requirements"):
        empty = [r["page"] for r in rows if not r[field]]
        assert not empty, f"{len(empty)} rows with empty {field} (pages {empty[:5]})"


@pytest.mark.parametrize("code", [
    "CBD01",   # College of Business Education, Dar es Salaam
    "CBM01",   # College of Business Education, Dodoma
    "CBMZ1",   # College of Business Education, Mwanza — 4 letters, 1 digit
    "SUM01",   # Abdulrahman Al-Sumait University, Zanzibar
    "AKU01",   # Aga Khan University
    "DMI01",   # Dar es Salaam Maritime Institute
    "CFR01",   # Centre for Foreign Relations
    "CD001",   # Tengeru Institute — the header with no "Programme" label
])
def test_codes_the_old_regex_could_never_match_are_present(rows, code):
    """Each of these is shaped so `^[A-Z]{2,4}\\d{3}$` rejects it, which is why
    its whole institution was invisible."""
    assert any(r["code"] == code for r in rows), f"{code} missing"


def test_accounts_for_an_independent_extraction(rows):
    """Coverage fixture: the prior-art catalog is 146 rows pulled from the TCU
    guidebook by an unrelated tool. Cross-checking two independent extractions is
    what exposed the original 190-programme gap, so it belongs in the suite rather
    than in a zip file someone happens to send.

    ZU009 is the one documented exception: it is genuinely absent from *this*
    edition of the PDF. That catalog cites pages up to 392 in a 376-page document,
    so it was extracted from a different edition.
    """
    if not PRIOR_ART.exists():          # reference material, may not be checked out
        pytest.skip("prior-art catalog not present")
    prior = {r["Code"].strip().upper()
             for r in json.loads(PRIOR_ART.read_text(encoding="utf-8"))}
    ours = {r["code"].strip().upper() for r in rows if r["code"]}
    missing = prior - ours
    assert missing <= {"ZU009"}, f"unexplained absences: {sorted(missing)}"


def test_pipeline_output_reconciles_to_the_transcription(rows):
    """Every transcribed row must end up somewhere accountable.

    This replaced an earlier test asserting the transcription was a superset of the
    old pipeline. That became true by construction once `extract_guidebook.py`
    started consuming this file, so it stopped testing anything. The invariant that
    still has teeth is the reconciliation: served + quarantined + curated must equal
    what was transcribed. A row that is in none of them has been lost in silence,
    which is the whole failure this pipeline was rebuilt to prevent.
    """
    buckets = {}
    for name in ("programmes.json", "programmes_extracted.json",
                 "extraction_review.json"):
        blob = json.loads((DATA / name).read_text(encoding="utf-8"))
        records = blob if isinstance(blob, list) else next(
            v for v in blob.values() if isinstance(v, list))
        buckets[name] = {r.get("code", "").strip().upper()
                         for r in records if r.get("code")}

    accounted = set().union(*buckets.values())
    transcribed = {r["code"].strip().upper() for r in rows if r["code"]}
    lost = transcribed - accounted
    assert not lost, f"{len(lost)} transcribed rows in no output bucket: {sorted(lost)[:10]}"


def test_serving_more_than_the_old_pipeline_did(rows):
    """Cycle 10's point: the guidebook we transcribed actually reaches students.
    The old pipeline served 362 (30 curated + 332 machine-parsed)."""
    curated = json.loads((DATA / "programmes.json").read_text(encoding="utf-8"))["programmes"]
    blob = json.loads((DATA / "programmes_extracted.json").read_text(encoding="utf-8"))
    machine = blob if isinstance(blob, list) else next(
        v for v in blob.values() if isinstance(v, list))
    assert len(curated) + len(machine) > 362


def test_csv_and_json_agree():
    import csv
    with (DATA / "guidebook_programmes.csv").open(encoding="utf-8") as fh:
        csv_rows = list(csv.DictReader(fh))
    json_rows = json.loads((DATA / "guidebook_programmes.json").read_text(encoding="utf-8"))
    assert len(csv_rows) == len(json_rows)
    assert [r["code"] for r in csv_rows] == [r["code"] for r in json_rows]
