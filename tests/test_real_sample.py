"""End-to-end test on the real Crunchbase sample pulled on 2026-11-24.

The raw data is licensed and not committed (see .gitignore); these tests skip
when it is absent. Thresholds are set slightly below the measured held-out
performance so that regressions fail the build.
"""
import pytest

from aisec_eval import evaluate_all, load_config
from aisec_eval import taxonomy as T
from aisec_eval.ingest import attach_evidence, dedupe, load_any, load_evidence
from aisec_eval.validate import compare, load_labels
from conftest import RAW, ROOT, TODAY

FILES = [RAW / "crunchbase_ai_security_2026-11-24.json", RAW / "crunchbase_public_cyber_2026-11-24.json"]
pytestmark = pytest.mark.skipif(not all(f.exists() for f in FILES), reason="raw Crunchbase sample not present")


@pytest.fixture(scope="module")
def companies():
    cos = []
    for f in FILES:
        cos += load_any(f)
    return dedupe(cos)[0]


@pytest.fixture(scope="module")
def cards(companies):
    return {c.name: c for c in evaluate_all(companies, load_config(), TODAY)}


@pytest.fixture(scope="module")
def validation(cards):
    return compare(list(cards.values()), load_labels(ROOT / "validation" / "ground_truth_labels.csv"))


def test_whole_sample_evaluated(companies, cards):
    assert len(companies) == 215
    assert len(cards) == 215


def test_scorecard_invariants(companies, cards):
    by_name = {c.name: c for c in companies}
    for name, card in cards.items():
        assert card.segment in T.ALL_SEGMENTS
        if card.in_scope:
            assert 0 <= card.capability_index <= 100
        else:
            assert card.capability_index is None
        texts = {e.source: e.text for e in by_name[name].all_evidence()}
        for f in card.capabilities:
            for ph in f.matched_phrases:
                assert any(ph in texts[s] for s in f.sources), (name, f.domain_id, ph)


def test_all_labels_matched(validation):
    assert validation["unmatched_labels"] == []
    assert validation["matched"] == 215


def test_heldout_performance(validation):
    m = validation["heldout"]
    assert m["in_scope_precision"] >= 0.88
    assert m["in_scope_recall"] >= 0.92
    assert m["segment_accuracy"] >= 0.72


@pytest.mark.parametrize("name", ["Sai Security Printers", "GotYu", "Optical Standard Technology",
                                  "Nexchain", "CARPL.ai", "Anvaya Insights", "Experian", "Nokia"])
def test_obvious_non_ai_security_companies_excluded(cards, name):
    assert not cards[name].in_scope, (name, cards[name].segment, cards[name].segment_rationale)


@pytest.mark.parametrize("name,segment", [
    ("HiddenLayer", T.SECURITY_FOR_AI), ("Noma Security", T.SECURITY_FOR_AI), ("Lasso Security", T.SECURITY_FOR_AI),
    ("Zenity", T.SECURITY_FOR_AI), ("Mindgard", T.SECURITY_FOR_AI), ("Silmaril", T.SECURITY_FOR_AI),
    ("Dropzone AI", T.AI_FOR_SECURITY), ("Exaforce", T.AI_FOR_SECURITY), ("Abnormal AI", T.AI_FOR_SECURITY),
    ("Credo AI", T.AI_GOVERNANCE), ("Monitaur", T.AI_GOVERNANCE), ("Saidot", T.AI_GOVERNANCE),
])
def test_unambiguous_companies(cards, name, segment):
    assert cards[name].segment == segment


def test_corrupted_records_flagged(cards):
    for name in ("SEALRIGOBERTO GONZALEZ DE JESUS", "Quantum Cyber"):
        assert any("mismatch" in f for f in cards[name].data_quality_flags), name


def test_both_established_and_new_companies_present(cards):
    tiers = {c.maturity_tier for c in cards.values()}
    assert {"established", "scale_up", "growth", "early", "nascent"} <= tiers
    years = [c.facts["founded_year"] for c in cards.values() if c.facts["founded_year"]]
    assert min(years) < 1950 and max(years) == 2026


def test_higher_level_evidence_reclassifies_incumbents(companies):
    cos = [c for c in companies if c.name in ("Zscaler", "Microsoft")]
    before = {c.name: c for c in evaluate_all(cos, load_config(), TODAY)}
    import copy
    cos2 = copy.deepcopy(cos)
    attach_evidence(cos2, load_evidence(ROOT / "examples" / "evidence_incumbents.json"))
    after = {c.name: c for c in evaluate_all(cos2, load_config(), TODAY)}
    for n in ("Zscaler", "Microsoft"):
        assert not before[n].in_scope
        assert after[n].segment == T.SECURITY_FOR_AI
        assert max(f.evidence_level for f in after[n].capabilities) == 2
        assert after[n].assurance_pct == 50.0
