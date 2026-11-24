import csv
import json

from aisec_eval.cli import main
from conftest import FIXTURES


def test_cli_end_to_end_on_synthetic_fixture(tmp_path):
    assert main(["evaluate", "--input", str(FIXTURES / "synthetic_companies.csv"),
                 "--out", str(tmp_path), "--as-of", "2026-11-24"]) == 0
    for f in ("scorecards.json", "scorecards.csv", "summary.json", "report.md"):
        assert (tmp_path / f).exists()
    cards = {c["name"]: c for c in json.loads((tmp_path / "scorecards.json").read_text())}
    assert len(cards) == 7  # duplicate removed
    assert cards["Example Guardrail Co"]["segment"] == "security_for_ai"
    assert cards["Example Agent Shield"]["segment"] == "security_for_ai"
    assert cards["Example SOC Agents"]["segment"] == "ai_for_security"
    assert cards["Example Governance"]["segment"] == "ai_governance"
    assert cards["Example Firewall Corp"]["segment"] == "adjacent"
    assert cards["Example Bakery"]["segment"] == "out_of_scope"
    assert cards["Example Unknown"]["maturity_tier"] == "unknown"
    assert "LLM01" in cards["Example Guardrail Co"]["framework_coverage"]["owasp_llm_2025"]
    rows = list(csv.DictReader((tmp_path / "scorecards.csv").open()))
    assert len(rows) == 7
    assert "Duplicates removed: 1" in (tmp_path / "report.md").read_text()
