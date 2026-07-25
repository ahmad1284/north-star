"""Realistic student personas as living sanity checks.

Each persona is a plausible Form 6 graduate; the assertions encode what a
sensible answer looks like, so any rule/data/ranking change that breaks
common sense breaks the build.
"""

import pytest

from northstar.engine import evaluate_all
from northstar.loader import load_knowledge_base
from northstar.models import StudentProfile
from northstar.ranking import rank_and_group


@pytest.fixture(scope="module")
def kb():
    return load_knowledge_base()


def run(kb, grades):
    profile = StudentProfile(grades=grades)
    return rank_and_group(kb, profile, evaluate_all(kb, profile))


def all_ids(out):
    return {
        r["programme"]["id"]
        for group in out["groups"].values()
        for r in group
    }


def ids(out, group):
    return [r["programme"]["id"] for r in out["groups"][group]]


def test_amina_strong_pcb(kb):
    """Straight-A PCB: full health suite plus non-obvious discoveries."""
    out = run(kb, {"chemistry": "A", "biology": "A", "physics": "B"})
    fy = ids(out, "for_you")
    assert "suza-doctor-of-medicine" in fy
    assert "muhas-bachelor-of-pharmacy" in fy
    disc = ids(out, "discoveries")
    assert "aru-bachelor-of-architecture" in disc
    assert "suza-accounting-finance" in disc


def test_juma_weak_pcb_no_md_but_still_has_paths(kb):
    """D,D,E in PCB: MD out (5 pts < 6) — but teaching & agriculture remain."""
    out = run(kb, {"chemistry": "D", "biology": "D", "physics": "E"})
    everything = all_ids(out)
    assert "suza-doctor-of-medicine" not in everything
    assert "suza-bsc-with-education" in everything
    assert "sua-bsc-agriculture" in everything
    assert out["counts"]["eligible"] > 0, "a weak student must never face an empty page"


def test_zainab_egm_business_and_engineering_discovery(kb):
    """EGM: business/CS in for_you; AdvMath+Geo opens Agricultural Engineering."""
    out = run(kb, {"economics": "B", "geography": "C", "advanced_mathematics": "C"})
    fy = ids(out, "for_you")
    assert "udsm-ba-economics" in fy
    assert "suza-bsc-computer-science" in fy
    assert "sua-bsc-agricultural-engineering" in ids(out, "discoveries")


def test_hamisi_hkl_arts_plus_it_discovery(kb):
    """HKL: UDSM arts suite in for_you; SUZA IT accepts Hist+Kis — a discovery."""
    out = run(kb, {"history": "B", "kiswahili": "A", "literature_in_english": "C"})
    fy = ids(out, "for_you")
    assert "udsm-ba-literature" in fy
    assert "suza-ba-with-education" in fy
    assert "suza-bit-application-management" in ids(out, "discoveries")
    # And no science/health programme leaks in
    assert "suza-doctor-of-medicine" not in all_ids(out)


def test_neema_pcm_engineering_focus(kb):
    """PCM: engineering/CS in for_you, arts-side economics as a discovery."""
    out = run(kb, {"physics": "C", "chemistry": "D", "advanced_mathematics": "B"})
    fy = ids(out, "for_you")
    assert "udsm-bsc-mining-engineering" in fy
    assert "suza-bsc-computer-science" in fy
    assert "udsm-ba-economics" in all_ids(out)


def test_salma_eca_narrow_but_real(kb):
    """ECA against the current seed: few options, but the right ones."""
    out = run(kb, {"economics": "C", "commerce": "D", "accountancy": "C"})
    everything = all_ids(out)
    assert "suza-accounting-finance" in everything
    assert "udsm-ba-economics" in everything
    # No science/health leakage
    assert "muhas-bachelor-of-pharmacy" not in everything
