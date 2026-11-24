"""Data model. Everything the framework outputs is traceable to an Evidence item."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Any


class EvidenceLevel(IntEnum):
    """How much the framework trusts a piece of evidence.

    L1 vendor self-description (e.g. a Crunchbase/LinkedIn blurb written by the vendor)
    L2 vendor technical documentation / datasheet / product docs
    L3 independent third party (analyst report, customer reference, independent press)
    L4 independently tested or audited (hands-on evaluation, certification audit)
    """
    NONE = 0
    SELF_DESCRIPTION = 1
    VENDOR_DOCUMENTATION = 2
    THIRD_PARTY = 3
    INDEPENDENT_TEST = 4


@dataclass
class Evidence:
    text: str
    source: str  # e.g. "crunchbase:short_description" or a URL
    level: EvidenceLevel = EvidenceLevel.SELF_DESCRIPTION
    domain_hint: str | None = None  # optional: evidence explicitly attached to one capability domain
    retrieved_on: str | None = None


@dataclass
class Company:
    name: str
    description: str = ""
    website: str | None = None
    source_url: str | None = None
    founded_year: int | None = None
    total_funding_usd: float | None = None
    employee_range: str | None = None  # normalised "11-50", "10001+" ...
    last_funding_type: str | None = None
    ipo_status: str | None = None  # "public" / "private" / None
    source: str = "unknown"
    extra_evidence: list[Evidence] = field(default_factory=list)

    @property
    def key(self) -> str:
        """De-duplication key: website domain if known, else normalised name."""
        if self.website:
            w = self.website.lower().split("://")[-1].split("/")[0]
            return w.removeprefix("www.")
        return "".join(ch for ch in self.name.lower() if ch.isalnum())

    def all_evidence(self) -> list[Evidence]:
        ev = []
        if self.description:
            ev.append(Evidence(self.description, f"{self.source}:short_description", EvidenceLevel.SELF_DESCRIPTION))
        ev.extend(self.extra_evidence)
        return ev


@dataclass
class CapabilityFinding:
    domain_id: str
    domain_name: str
    evidence_level: int  # max EvidenceLevel among supporting evidence
    matched_phrases: list[str]
    sources: list[str]


@dataclass
class Scorecard:
    name: str
    key: str
    segment: str
    segment_rationale: list[str]
    in_scope: bool
    capabilities: list[CapabilityFinding]
    breadth_pct: float | None
    assurance_pct: float | None
    framework_coverage: dict[str, Any]
    framework_coverage_pct: float | None
    capability_index: float | None
    maturity_tier: str
    maturity_rationale: list[str]
    age_years: int | None
    confidence: str
    data_quality_flags: list[str]
    limitations: list[str]
    facts: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
