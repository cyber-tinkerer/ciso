"""Core evaluation: segment classification, capability findings, maturity, scoring.

Design rules (enforced by tests):
1. Every capability finding is backed by a phrase that literally occurs in a cited source.
2. Missing data is reported as unknown (None), never silently scored as zero.
3. Capability (what the product claims to do, and how well-evidenced that is) and
   maturity (how established the company is) are scored separately and never mixed.
4. Adding evidence can never lower a company's assurance score.
5. Same input -> same output (no randomness, no network).
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import taxonomy as T
from .ingest import employee_lower_bound
from .models import CapabilityFinding, Company, Evidence, EvidenceLevel, Scorecard

DEFAULT_CONFIG = {
    # Weights of the three components of the capability index. Must sum to 1.
    "index_weights": {"breadth": 0.4, "assurance": 0.4, "framework_coverage": 0.2},
    # How much each evidence level is trusted (0..1).
    "evidence_weights": {"0": 0.0, "1": 0.25, "2": 0.5, "3": 0.75, "4": 1.0},
    # Maturity tier thresholds.
    "maturity": {
        "established_min_employees": 5001,
        "scale_up_min_employees": 1001,
        "scale_up_min_funding_usd": 250_000_000,
        "growth_min_employees": 101,
        "growth_min_funding_usd": 50_000_000,
        "early_min_employees": 11,
        "early_min_funding_usd": 5_000_000,
    },
    "min_description_chars": 40,
}


def load_config(path: str | Path | None = None) -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if path:
        user = json.loads(Path(path).read_text())
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    validate_config(cfg)
    return cfg


def validate_config(cfg: dict) -> None:
    w = cfg["index_weights"]
    if set(w) != {"breadth", "assurance", "framework_coverage"}:
        raise ValueError(f"index_weights must have keys breadth/assurance/framework_coverage, got {sorted(w)}")
    if any(v < 0 for v in w.values()) or abs(sum(w.values()) - 1.0) > 1e-9:
        raise ValueError(f"index_weights must be non-negative and sum to 1, got {w}")
    ew = {int(k): v for k, v in cfg["evidence_weights"].items()}
    levels = sorted(ew)
    if levels != [0, 1, 2, 3, 4]:
        raise ValueError("evidence_weights must define levels 0..4")
    if any(ew[a] > ew[b] for a, b in zip(levels, levels[1:])):
        raise ValueError("evidence_weights must be non-decreasing with evidence level")
    if not all(0 <= v <= 1 for v in ew.values()):
        raise ValueError("evidence_weights must be within [0, 1]")


# --------------------------------------------------------------------------- classification

@dataclass
class SegmentDecision:
    segment: str
    rationale: list[str] = field(default_factory=list)


def _hits(patterns, text: str) -> list[str]:
    out = []
    for p in patterns:
        m = p.search(text)
        if m:
            out.append(m.group(0))
    return out


def classify_segment(text: str) -> SegmentDecision:
    """Decide which market segment the evidence text places a company in."""
    has_ai = bool(T.AI_TERMS.search(text) or T.AI_TERMS_CI.search(text))
    sec = T.SECURITY_TERMS.search(text)
    gov = T.GOVERNANCE_TERMS.search(text)
    sfai = _hits(T.SECURITY_FOR_AI_SIGNALS, text)
    sfai_weak = _hits(T.WEAK_SECURITY_FOR_AI_SIGNALS, text)
    aifs = _hits(T.AI_FOR_SECURITY_SIGNALS, text)
    physical = T.PHYSICAL_SECURITY.search(text)

    r = [f"ai_terms={'yes' if has_ai else 'no'}",
         f"security_terms={sec.group(0)!r}" if sec else "security_terms=none",
         f"governance_terms={gov.group(0)!r}" if gov else "governance_terms=none"]
    if sfai:
        r.append(f"security_for_ai_signals={sfai}")
    if sfai_weak:
        r.append(f"weak_security_for_ai_signals={sfai_weak}")
    if aifs:
        r.append(f"ai_for_security_signals={aifs}")

    if physical and not re.search(r"cyber|network|data|software|cloud|API", text, re.IGNORECASE):
        r.append(f"physical_security={physical.group(0)!r}")
        return SegmentDecision(T.ADJACENT, r)
    if not has_ai:
        return SegmentDecision(T.ADJACENT if (sec or gov) else T.OUT_OF_SCOPE, r)
    sfai_score = len(sfai) + T.WEAK_WEIGHT * len(sfai_weak)
    if sec and (sfai_score or aifs):
        # AI-as-mechanism wins only when it has strictly more evidence than AI-as-object.
        seg = T.AI_FOR_SECURITY if len(aifs) > sfai_score else T.SECURITY_FOR_AI
        return SegmentDecision(seg, r)
    if gov:
        return SegmentDecision(T.AI_GOVERNANCE, r)
    if sec:
        return SegmentDecision(T.ADJACENT, r + ["security mentioned but AI not tied to the security claim"])
    return SegmentDecision(T.OUT_OF_SCOPE, r)


# --------------------------------------------------------------------------- capabilities

def find_capabilities(evidence: list[Evidence]) -> list[CapabilityFinding]:
    findings: dict[str, CapabilityFinding] = {}
    for ev in evidence:
        for d in T.DOMAINS:
            phrases = []
            if ev.domain_hint == d.id:
                phrases.append(ev.text[:120])
            else:
                for p in d.patterns:
                    m = p.search(ev.text)
                    if m and not any(x.search(ev.text) for x in d.exclude):
                        phrases.append(m.group(0))
            if not phrases:
                continue
            f = findings.get(d.id)
            if f is None:
                f = findings[d.id] = CapabilityFinding(d.id, d.name, int(ev.level), [], [])
            f.evidence_level = max(f.evidence_level, int(ev.level))
            for ph in phrases:
                if ph not in f.matched_phrases:
                    f.matched_phrases.append(ph)
            if ev.source not in f.sources:
                f.sources.append(ev.source)
    order = {d.id: i for i, d in enumerate(T.DOMAINS)}
    return sorted(findings.values(), key=lambda f: order[f.domain_id])


def framework_coverage(segment: str, findings: list[CapabilityFinding]) -> tuple[dict, float | None]:
    ids = {f.domain_id for f in findings}
    owasp = sorted({r for i in ids for r in T.DOMAIN_BY_ID[i].owasp_llm})
    rmf = [f for f in T.NIST_AI_RMF if any(f in T.DOMAIN_BY_ID[i].nist_ai_rmf for i in ids)]
    csf = [f for f in T.NIST_CSF_2 if any(f in T.DOMAIN_BY_ID[i].nist_csf for i in ids)]
    cov = {"owasp_llm_2025": owasp, "nist_ai_rmf": rmf, "nist_csf_2": csf}
    if segment == T.SECURITY_FOR_AI:
        pct = 100 * len(owasp) / len(T.OWASP_LLM_2025)
    elif segment == T.AI_FOR_SECURITY:
        pct = 100 * len(csf) / len(T.NIST_CSF_2)
    elif segment == T.AI_GOVERNANCE:
        pct = 100 * len(rmf) / len(T.NIST_AI_RMF)
    else:
        pct = None
    return cov, pct


# --------------------------------------------------------------------------- maturity

def maturity_tier(c: Company, cfg: dict, today: _dt.date) -> tuple[str, list[str]]:
    m = cfg["maturity"]
    emp = employee_lower_bound(c.employee_range)
    fund = c.total_funding_usd
    why = [f"employees={c.employee_range or 'unknown'}", f"funding_usd={fund if fund is not None else 'unknown'}",
           f"ipo_status={c.ipo_status or 'unknown'}", f"founded={c.founded_year or 'unknown'}"]
    if c.ipo_status == "public" or (emp is not None and emp >= m["established_min_employees"]):
        return "established", why
    if (emp is not None and emp >= m["scale_up_min_employees"]) or (fund is not None and fund >= m["scale_up_min_funding_usd"]):
        return "scale_up", why
    if (emp is not None and emp >= m["growth_min_employees"]) or (fund is not None and fund >= m["growth_min_funding_usd"]):
        return "growth", why
    if (emp is not None and emp >= m["early_min_employees"]) or (fund is not None and fund >= m["early_min_funding_usd"]):
        return "early", why
    if emp is None and fund is None:
        return "unknown", why + ["no employee or funding data: tier not inferred"]
    return "nascent", why


# --------------------------------------------------------------------------- data quality

_LEADING_NAME = re.compile(r"^([A-Z][\w.&'-]*(?:\s+[A-Z][\w.&'-]*)?)\s+(?:is|provides|develops|offers|builds|helps|delivers|operates|employs|enables|protects|manufactures|focuses|gives|unifies|links|closes|deploys|proves|secures)\b")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _names_agree(subject: str, name: str) -> bool:
    """True if the subject of the description's first sentence plausibly is `name`."""
    first, n, subj = _norm(subject.split()[0]), _norm(name), _norm(subject)
    return bool(first) and (first in n or n in subj)


def data_quality_flags(c: Company, cfg: dict, today: _dt.date) -> list[str]:
    flags = []
    if not c.description:
        flags.append("missing_description")
    elif len(c.description) < cfg["min_description_chars"]:
        flags.append("description_too_short")
    if c.founded_year is None:
        flags.append("missing_founded_year")
    elif c.founded_year > today.year:
        flags.append("founded_year_in_future")
    if c.total_funding_usd is None:
        flags.append("missing_funding")
    if c.employee_range is None:
        flags.append("missing_employee_count")
    if c.description:
        m = _LEADING_NAME.match(c.description)
        if m and not _names_agree(m.group(1), c.name):
            flags.append(f"name_description_mismatch(description subject {m.group(1)!r})")
    if c.source_url and "/organization/" in c.source_url:
        slug = c.source_url.rstrip("/").rsplit("/", 1)[-1]
        tokens = [t for t in slug.split("-") if len(t) >= 3 and not re.fullmatch(r"[0-9a-f]{4}", t)]
        if tokens and not re.fullmatch(r"[0-9a-f-]{36}", slug):
            name = _norm(c.name)
            if not any(t in name or name in t for t in tokens):
                flags.append(f"source_record_name_mismatch(slug {slug!r}: possible rename or merged record)")
    return flags


# --------------------------------------------------------------------------- scoring

def evaluate_company(c: Company, cfg: dict | None = None, today: _dt.date | None = None) -> Scorecard:
    cfg = cfg or load_config()
    today = today or _dt.date.today()
    ew = {int(k): float(v) for k, v in cfg["evidence_weights"].items()}
    evidence = c.all_evidence()
    text = " \n".join(e.text for e in evidence)

    seg = classify_segment(text)
    in_scope = seg.segment in T.IN_SCOPE_SEGMENTS
    findings = find_capabilities(evidence)
    relevant = T.domains_for_segment(seg.segment)
    rel_ids = {d.id for d in relevant}
    rel_findings = [f for f in findings if f.domain_id in rel_ids]

    breadth = assurance = index = None
    cov, cov_pct = framework_coverage(seg.segment, findings)
    if in_scope:
        total_w = sum(d.weight for d in relevant)
        breadth = 100 * sum(T.DOMAIN_BY_ID[f.domain_id].weight for f in rel_findings) / total_w
        assurance = (100 * sum(ew[f.evidence_level] for f in rel_findings) / len(rel_findings)) if rel_findings else 0.0
        w = cfg["index_weights"]
        index = round(w["breadth"] * breadth + w["assurance"] * assurance + w["framework_coverage"] * (cov_pct or 0), 1)
        breadth, assurance = round(breadth, 1), round(assurance, 1)
        cov_pct = round(cov_pct, 1) if cov_pct is not None else None

    tier, tier_why = maturity_tier(c, cfg, today)
    flags = data_quality_flags(c, cfg, today)
    if in_scope and not rel_findings:
        flags.append("in_scope_but_no_specific_capability_claimed")

    max_level = max((f.evidence_level for f in findings), default=0)
    if not in_scope:
        confidence = "n/a"
    elif max_level >= EvidenceLevel.THIRD_PARTY and not flags:
        confidence = "high"
    elif max_level >= EvidenceLevel.VENDOR_DOCUMENTATION or (rel_findings and len(flags) <= 1):
        confidence = "medium"
    else:
        confidence = "low"

    limitations = []
    if max_level <= EvidenceLevel.SELF_DESCRIPTION:
        limitations.append("Evidence is vendor self-description only (L1). Capabilities are claimed, not verified.")
    if c.description and len(evidence) == 1:
        limitations.append("Single short text source: absence of a capability here does not mean the vendor lacks it.")

    return Scorecard(
        name=c.name, key=c.key, segment=seg.segment, segment_rationale=seg.rationale, in_scope=in_scope,
        capabilities=findings, breadth_pct=breadth, assurance_pct=assurance,
        framework_coverage=cov, framework_coverage_pct=cov_pct, capability_index=index,
        maturity_tier=tier, maturity_rationale=tier_why,
        age_years=(today.year - c.founded_year) if c.founded_year else None,
        confidence=confidence, data_quality_flags=flags, limitations=limitations,
        facts={"website": c.website, "source_url": c.source_url, "founded_year": c.founded_year,
               "total_funding_usd": c.total_funding_usd, "employee_range": c.employee_range,
               "last_funding_type": c.last_funding_type, "ipo_status": c.ipo_status, "source": c.source},
    )


def evaluate_all(companies: list[Company], cfg: dict | None = None, today: _dt.date | None = None) -> list[Scorecard]:
    cfg = cfg or load_config()
    return [evaluate_company(c, cfg, today) for c in companies]
