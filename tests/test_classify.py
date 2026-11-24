import pytest

from aisec_eval import classify_segment
from aisec_eval import taxonomy as T


@pytest.mark.parametrize("text,expected", [
    ("Acme provides an AI firewall that blocks prompt injection attacks against LLM apps.", T.SECURITY_FOR_AI),
    ("Acme secures AI agents and MCP servers in the enterprise.", T.SECURITY_FOR_AI),
    ("Acme detects shadow AI and protects sensitive data sent to generative AI tools.", T.SECURITY_FOR_AI),
    ("Acme offers automated red teaming of LLM applications.", T.SECURITY_FOR_AI),
    ("Acme is a cybersecurity company that uses agentic AI to triage and investigate alerts.", T.AI_FOR_SECURITY),
    ("Acme delivers autonomous AI security agents for security operations teams.", T.AI_FOR_SECURITY),
    ("Acme is an AI-powered email security platform that stops phishing.", T.AI_FOR_SECURITY),
    ("Acme is an AI governance platform for EU AI Act compliance.", T.AI_GOVERNANCE),
    ("Acme sells next-generation network firewalls.", T.ADJACENT),
    ("Acme bakes bread.", T.OUT_OF_SCOPE),
    ("Acme makes AI-powered gun detection cameras for schools.", T.ADJACENT),
])
def test_segments(text, expected):
    assert classify_segment(text).segment == expected


def test_ai_token_is_case_sensitive_word():
    # "said", "air", "chair" must not count as AI.
    d = classify_segment("Acme said its air filter chair improves security.")
    assert d.segment == T.ADJACENT
    assert "ai_terms=no" in d.rationale


def test_company_name_containing_security_does_not_make_ai_the_protected_object():
    # Regression: "RAD Security offers an AI-driven..." once matched "security ... AI".
    text = "RAD Security offers an AI-driven security platform that auto-triages threats."
    assert classify_segment(text).segment == T.AI_FOR_SECURITY


def test_rationale_is_populated():
    d = classify_segment("Acme secures AI agents.")
    assert any(r.startswith("security_for_ai_signals=") for r in d.rationale)
