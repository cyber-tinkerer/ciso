import dataclasses

import pytest

from aisec_eval import Company, Evidence, EvidenceLevel, evaluate_company, load_config
from aisec_eval.evaluate import maturity_tier, validate_config


def co(**kw):
    base = dict(name="Acme", description="Acme secures AI agents with real-time guardrails against prompt injection.",
                website="https://acme.example", founded_year=2024, total_funding_usd=10e6,
                employee_range="11-50", ipo_status="private", source="test")
    base.update(kw)
    return Company(**base)


def test_every_finding_is_traceable_to_source_text(today):
    c = co()
    card = evaluate_company(c, today=today)
    texts = {e.source: e.text for e in c.all_evidence()}
    assert card.capabilities
    for f in card.capabilities:
        for phrase in f.matched_phrases:
            assert any(phrase in texts[s] for s in f.sources), (f.domain_id, phrase)


def test_out_of_scope_gets_no_scores_not_zero(today):
    card = evaluate_company(co(description="Acme bakes sourdough bread for cafes."), today=today)
    assert card.in_scope is False
    assert card.capability_index is None and card.breadth_pct is None and card.assurance_pct is None
    assert card.confidence == "n/a"


def test_missing_maturity_data_is_unknown_not_nascent(today):
    card = evaluate_company(co(total_funding_usd=None, employee_range=None, ipo_status=None), today=today)
    assert card.maturity_tier == "unknown"
    assert "missing_funding" in card.data_quality_flags
    assert "missing_employee_count" in card.data_quality_flags


@pytest.mark.parametrize("kw,tier", [
    (dict(ipo_status="public", employee_range="11-50"), "established"),
    (dict(employee_range="5001-10000"), "established"),
    (dict(employee_range="1001-5000"), "scale_up"),
    (dict(total_funding_usd=250e6, employee_range="51-100"), "scale_up"),
    (dict(total_funding_usd=50e6, employee_range="11-50"), "growth"),
    (dict(total_funding_usd=1e6, employee_range="101-250"), "growth"),
    (dict(total_funding_usd=5e6, employee_range="1-10"), "early"),
    (dict(total_funding_usd=1e6, employee_range="1-10"), "nascent"),
])
def test_maturity_tiers(kw, tier, today):
    assert maturity_tier(co(**kw), load_config(), today)[0] == tier


def test_capability_and_maturity_are_independent(today):
    small = evaluate_company(co(total_funding_usd=1e5, employee_range="1-10"), today=today)
    big = evaluate_company(co(total_funding_usd=1e9, employee_range="1001-5000"), today=today)
    assert small.capability_index == big.capability_index
    assert small.maturity_tier != big.maturity_tier


@pytest.mark.parametrize("level", [EvidenceLevel.VENDOR_DOCUMENTATION, EvidenceLevel.THIRD_PARTY,
                                   EvidenceLevel.INDEPENDENT_TEST])
def test_stronger_evidence_never_lowers_assurance(level, today):
    base = co()
    before = evaluate_company(base, today=today)
    domain = before.capabilities[0].domain_id
    stronger = dataclasses.replace(base, extra_evidence=[
        Evidence("Independent evaluation confirmed the guardrails.", "https://lab.example/report", level, domain_hint=domain)])
    after = evaluate_company(stronger, today=today)
    assert after.segment == before.segment
    assert after.assurance_pct > before.assurance_pct
    assert after.capability_index >= before.capability_index
    f = next(x for x in after.capabilities if x.domain_id == domain)
    assert f.evidence_level == int(level)
    assert "https://lab.example/report" in f.sources


def test_l1_only_carries_limitation_and_is_not_high_confidence(today):
    card = evaluate_company(co(), today=today)
    assert card.confidence != "high"
    assert any("not verified" in x for x in card.limitations)


def test_deterministic(today):
    a = evaluate_company(co(), today=today).to_dict()
    b = evaluate_company(co(), today=today).to_dict()
    assert a == b


def test_data_quality_flags(today):
    card = evaluate_company(co(name="Wrongname Holdings", founded_year=2030,
                               description="Rightname is a company that secures AI agents."), today=today)
    assert "founded_year_in_future" in card.data_quality_flags
    assert any(f.startswith("name_description_mismatch") for f in card.data_quality_flags)
    card = evaluate_company(co(source_url="https://www.crunchbase.com/organization/mainz-biomed"), today=today)
    assert any(f.startswith("source_record_name_mismatch") for f in card.data_quality_flags)
    card = evaluate_company(co(description="AI security"), today=today)
    assert "description_too_short" in card.data_quality_flags


def test_name_check_tolerates_case_and_suffix_differences(today):
    for name, desc in [("Aim Intelligence", "AIM Intelligence is an AI security platform."),
                       ("OnboardAI", "Onboard AI is a company that secures AI agents."),
                       ("Gray Swan", "Gray Swan AI is a company specializing in security of AI systems.")]:
        card = evaluate_company(co(name=name, description=desc), today=today)
        assert not any("mismatch" in f for f in card.data_quality_flags), name


@pytest.mark.parametrize("bad", [
    {"index_weights": {"breadth": 0.5, "assurance": 0.5, "framework_coverage": 0.5}},
    {"index_weights": {"breadth": 1.0}},
    {"evidence_weights": {"0": 0, "1": 0.9, "2": 0.5, "3": 0.75, "4": 1}},
])
def test_invalid_config_rejected(bad):
    cfg = load_config()
    for k, v in bad.items():
        cfg[k] = v
    with pytest.raises(ValueError):
        validate_config(cfg)


def test_index_bounds(today):
    card = evaluate_company(co(), today=today)
    for v in (card.capability_index, card.breadth_pct, card.assurance_pct, card.framework_coverage_pct):
        assert 0 <= v <= 100
