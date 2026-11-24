"""Loaders that turn heterogeneous sources into `Company` records.

Supported inputs
* Crunchbase MCP `cb_expert_query_answer` JSON (columns + rows)
* Compact Crunchbase search JSON ({"entities": [{name, short_description, ...}]})
* Generic CSV / JSON list with columns: name, description, website, founded_year,
  total_funding_usd, employee_range, last_funding_type, ipo_status
* Evidence file (JSON list) adding higher-assurance evidence to named companies
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable

from .models import Company, Evidence, EvidenceLevel

_EMP_ENUM = re.compile(r"c_0*(\d+)_(?:0*(\d+)|max)")


def normalise_employees(value: Any) -> str | None:
    """'c_00011_00050' -> '11-50', 'c_10001_max' -> '10001+', '1001-5000' -> '1001-5000'."""
    if value in (None, ""):
        return None
    s = str(value).strip()
    m = _EMP_ENUM.fullmatch(s)
    if m:
        lo, hi = m.group(1), m.group(2)
        return f"{lo}-{hi}" if hi else f"{lo}+"
    return s


def employee_lower_bound(rng: str | None) -> int | None:
    if not rng:
        return None
    m = re.match(r"(\d+)", rng)
    return int(m.group(1)) if m else None


def _year(value: Any) -> int | None:
    if value in (None, ""):
        return None
    m = re.match(r"(\d{4})", str(value))
    return int(m.group(1)) if m else None


def _num(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, dict):
        value = value.get("value_usd", value.get("value"))
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _unwrap(value: Any) -> Any:
    """Crunchbase sometimes returns '{"value": "..."}' strings or dicts with a 'value' key."""
    if isinstance(value, str) and value.lstrip().startswith("{"):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return value
    if isinstance(value, dict):
        return value.get("value")
    return value


def load_crunchbase_query_answer(path: str | Path) -> list[Company]:
    data = json.loads(Path(path).read_text())
    cols = [c.upper() for c in data["columns"]]
    idx = {c: i for i, c in enumerate(cols)}

    def get(row, *names):
        for n in names:
            if n in idx:
                return row[idx[n]]
        return None

    out = []
    for row in data["rows"]:
        ident = get(row, "COMPANY", "NAME", "ORGANIZATION")
        name = _unwrap(ident)
        source_url = ident.get("url") if isinstance(ident, dict) else None
        out.append(Company(
            name=str(name),
            description=_unwrap(get(row, "SHORT_DESCRIPTION", "DESCRIPTION")) or "",
            website=_unwrap(get(row, "WEBSITE", "WEBSITE_URL")),
            source_url=source_url,
            founded_year=_year(_unwrap(get(row, "FOUNDED_YEAR", "FOUNDED_ON"))),
            total_funding_usd=_num(get(row, "TOTAL_FUNDING_USD", "FUNDING_TOTAL")),
            employee_range=normalise_employees(_unwrap(get(row, "EMPLOYEE_COUNT_RANGE", "NUM_EMPLOYEES_ENUM"))),
            last_funding_type=_unwrap(get(row, "LAST_FUNDING_TYPE")),
            ipo_status=_unwrap(get(row, "IPO_STATUS")),
            source="crunchbase",
        ))
    return out


def load_crunchbase_entities(path: str | Path, ipo_status: str | None = None) -> list[Company]:
    data = json.loads(Path(path).read_text())
    out = []
    for e in data["entities"]:
        out.append(Company(
            name=e["name"],
            description=e.get("short_description", ""),
            website=e.get("website_url"),
            source_url=e.get("url"),
            founded_year=_year(e.get("founded_on")),
            total_funding_usd=_num(e.get("funding_total")),
            employee_range=normalise_employees(e.get("num_employees_enum")),
            last_funding_type=e.get("last_funding_type"),
            ipo_status=e.get("ipo_status", ipo_status),
            source="crunchbase",
        ))
    return out


def load_generic(path: str | Path) -> list[Company]:
    p = Path(path)
    if p.suffix.lower() == ".csv":
        with p.open(newline="") as f:
            records: Iterable[dict] = list(csv.DictReader(f))
    else:
        records = json.loads(p.read_text())
    out = []
    for r in records:
        out.append(Company(
            name=r["name"],
            description=r.get("description") or "",
            website=r.get("website") or None,
            founded_year=_year(r.get("founded_year")),
            total_funding_usd=_num(r.get("total_funding_usd")),
            employee_range=normalise_employees(r.get("employee_range")),
            last_funding_type=r.get("last_funding_type") or None,
            ipo_status=r.get("ipo_status") or None,
            source=r.get("source") or p.name,
        ))
    return out


def load_evidence(path: str | Path) -> dict[str, list[Evidence]]:
    """Evidence file: [{"company": "...", "text": "...", "source": "url", "level": 2, "domain": "..."}]"""
    out: dict[str, list[Evidence]] = {}
    for r in json.loads(Path(path).read_text()):
        out.setdefault(r["company"].lower(), []).append(Evidence(
            text=r["text"], source=r["source"], level=EvidenceLevel(int(r["level"])),
            domain_hint=r.get("domain"), retrieved_on=r.get("retrieved_on")))
    return out


def attach_evidence(companies: list[Company], evidence: dict[str, list[Evidence]]) -> list[str]:
    """Attach evidence to companies by case-insensitive name. Returns unmatched company names."""
    names = {c.name.lower(): c for c in companies}
    unmatched = []
    for cname, items in evidence.items():
        if cname in names:
            names[cname].extra_evidence.extend(items)
        else:
            unmatched.append(cname)
    return unmatched


def load_any(path: str | Path) -> list[Company]:
    p = Path(path)
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text())
        if isinstance(data, dict) and "columns" in data and "rows" in data:
            return load_crunchbase_query_answer(p)
        if isinstance(data, dict) and "entities" in data:
            return load_crunchbase_entities(p)
    return load_generic(p)


def dedupe(companies: list[Company]) -> tuple[list[Company], list[tuple[str, str]]]:
    """Drop exact duplicates by key (domain or normalised name). Returns (kept, [(dropped, kept_as)])."""
    seen: dict[str, Company] = {}
    dropped = []
    for c in companies:
        if c.key in seen:
            dropped.append((c.name, seen[c.key].name))
            seen[c.key].extra_evidence.extend(c.extra_evidence)
        else:
            seen[c.key] = c
    return list(seen.values()), dropped
