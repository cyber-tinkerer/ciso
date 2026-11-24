import re

from aisec_eval import taxonomy as T


def test_domain_ids_unique_and_patterns_compiled():
    ids = [d.id for d in T.DOMAINS]
    assert len(ids) == len(set(ids))
    for d in T.DOMAINS:
        assert d.patterns, d.id
        assert all(isinstance(p, re.Pattern) for p in d.patterns)
        assert d.segment in T.IN_SCOPE_SEGMENTS


def test_every_owasp_llm_risk_is_reachable():
    """A risk no domain maps to could never be reported as covered (structural blind spot)."""
    mapped = {r for d in T.DOMAINS for r in d.owasp_llm}
    assert mapped == set(T.OWASP_LLM_2025)


def test_every_nist_function_is_reachable():
    assert {f for d in T.DOMAINS for f in d.nist_ai_rmf} == set(T.NIST_AI_RMF)
    csf = {f for d in T.DOMAINS for f in d.nist_csf}
    # Recover is deliberately not claimed by any AI-security capability domain.
    assert csf == set(T.NIST_CSF_2) - {"Recover"}


def test_framework_ids_are_valid():
    for d in T.DOMAINS:
        assert set(d.owasp_llm) <= set(T.OWASP_LLM_2025), d.id
        assert set(d.nist_ai_rmf) <= set(T.NIST_AI_RMF), d.id
        assert set(d.nist_csf) <= set(T.NIST_CSF_2), d.id


def test_each_in_scope_segment_has_relevant_domains():
    for s in T.IN_SCOPE_SEGMENTS:
        assert T.domains_for_segment(s)
    assert T.domains_for_segment(T.ADJACENT) == ()
    assert T.domains_for_segment(T.OUT_OF_SCOPE) == ()
