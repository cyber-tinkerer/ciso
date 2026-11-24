import json

from aisec_eval.ingest import (attach_evidence, dedupe, load_any, load_crunchbase_query_answer,
                               load_evidence, normalise_employees)
from conftest import FIXTURES


def test_normalise_employees():
    assert normalise_employees("c_00011_00050") == "11-50"
    assert normalise_employees("c_10001_max") == "10001+"
    assert normalise_employees("1001-5000") == "1001-5000"
    assert normalise_employees(None) is None and normalise_employees("") is None


def test_query_answer_format(tmp_path):
    p = tmp_path / "qa.json"
    p.write_text(json.dumps({
        "columns": ["COMPANY", "WEBSITE", "FOUNDED_YEAR", "TOTAL_FUNDING_USD", "EMPLOYEE_COUNT_RANGE",
                    "LAST_FUNDING_TYPE", "IPO_STATUS", "SHORT_DESCRIPTION"],
        "rows": [[{"value": "Acme", "url": "https://cb.example/acme"}, '{\n  "value": "https://acme.example"\n}',
                  2022, 1000000, "11-50", "Seed", "private", "Acme secures AI agents."],
                 [{"value": "NoData"}, None, None, None, None, None, None, None]]}))
    a, b = load_crunchbase_query_answer(p)
    assert (a.name, a.website, a.founded_year, a.total_funding_usd, a.employee_range) == \
        ("Acme", "https://acme.example", 2022, 1e6, "11-50")
    assert a.source_url == "https://cb.example/acme"
    assert (b.website, b.founded_year, b.total_funding_usd, b.description) == (None, None, None, "")


def test_generic_csv_and_dedupe():
    cos = load_any(FIXTURES / "synthetic_companies.csv")
    assert len(cos) == 8
    kept, dropped = dedupe(cos)
    assert len(kept) == 7
    assert dropped == [("Example Guardrail Co Duplicate", "Example Guardrail Co")]


def test_evidence_attach(tmp_path):
    cos = load_any(FIXTURES / "synthetic_companies.csv")
    p = tmp_path / "ev.json"
    p.write_text(json.dumps([
        {"company": "example firewall corp", "text": "Protects LLM apps from prompt injection.",
         "source": "https://fw.example/docs", "level": 2},
        {"company": "Not In Sample", "text": "x", "source": "y", "level": 3}]))
    unmatched = attach_evidence(cos, load_evidence(p))
    assert unmatched == ["not in sample"]
    fw = next(c for c in cos if c.name == "Example Firewall Corp")
    assert len(fw.extra_evidence) == 1 and int(fw.extra_evidence[0].level) == 2
