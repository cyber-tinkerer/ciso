"""Write scorecards and a landscape summary (JSON, CSV, Markdown)."""
from __future__ import annotations

import csv
import json
import statistics
from collections import Counter
from pathlib import Path

from . import taxonomy as T
from .models import Scorecard

CSV_FIELDS = ["name", "segment", "in_scope", "capability_index", "breadth_pct", "assurance_pct",
              "framework_coverage_pct", "confidence", "maturity_tier", "age_years", "capabilities",
              "owasp_llm_2025", "nist_ai_rmf", "nist_csf_2", "data_quality_flags"]


def write_json(cards: list[Scorecard], path: Path) -> None:
    path.write_text(json.dumps([c.to_dict() for c in cards], indent=2, default=str))


def write_csv(cards: list[Scorecard], path: Path) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for c in cards:
            w.writerow({
                "name": c.name, "segment": c.segment, "in_scope": c.in_scope,
                "capability_index": c.capability_index, "breadth_pct": c.breadth_pct,
                "assurance_pct": c.assurance_pct, "framework_coverage_pct": c.framework_coverage_pct,
                "confidence": c.confidence, "maturity_tier": c.maturity_tier, "age_years": c.age_years,
                "capabilities": ";".join(f.domain_id for f in c.capabilities),
                "owasp_llm_2025": ";".join(c.framework_coverage["owasp_llm_2025"]),
                "nist_ai_rmf": ";".join(c.framework_coverage["nist_ai_rmf"]),
                "nist_csf_2": ";".join(c.framework_coverage["nist_csf_2"]),
                "data_quality_flags": ";".join(c.data_quality_flags),
            })


def summarise(cards: list[Scorecard]) -> dict:
    ins = [c for c in cards if c.in_scope]
    seg = Counter(c.segment for c in cards)
    tiers = Counter(c.maturity_tier for c in ins)
    by_tier_seg = Counter((c.maturity_tier, c.segment) for c in ins)
    dom = Counter(f.domain_id for c in ins for f in c.capabilities
                  if f.domain_id in {d.id for d in T.domains_for_segment(c.segment)})
    owasp = Counter(r for c in ins if c.segment == T.SECURITY_FOR_AI for r in c.framework_coverage["owasp_llm_2025"])
    n_sfai = seg[T.SECURITY_FOR_AI]
    idx = [c.capability_index for c in ins if c.capability_index is not None]
    flags = Counter(f.split("(")[0] for c in cards for f in c.data_quality_flags)
    return {
        "companies_evaluated": len(cards), "in_scope": len(ins), "segments": dict(seg),
        "maturity_tiers_in_scope": dict(tiers),
        "maturity_by_segment": {f"{t}|{s}": n for (t, s), n in sorted(by_tier_seg.items())},
        "capability_domain_prevalence": dict(dom.most_common()),
        "owasp_llm_2025_claimed_coverage_among_security_for_ai": {
            k: {"companies": owasp.get(k, 0), "pct": round(100 * owasp.get(k, 0) / n_sfai, 1) if n_sfai else None,
                "risk": v} for k, v in T.OWASP_LLM_2025.items()},
        "capability_index": ({"median": statistics.median(idx), "min": min(idx), "max": max(idx)} if idx else None),
        "confidence": dict(Counter(c.confidence for c in ins)),
        "data_quality_flags": dict(flags.most_common()),
    }


def _fmt(v):
    if v is None:
        return "n/a"
    return f"{v:.2f}" if isinstance(v, float) else str(v)


def write_markdown(cards: list[Scorecard], summary: dict, validation: dict | None, path: Path,
                   provenance: list[str]) -> None:
    L = ["# AI Security Vendor Landscape — Evaluation Run", ""]
    L += ["## Provenance", ""] + [f"- {p}" for p in provenance] + [""]
    L += ["## What these scores are (and are not)", "",
          "- **Segment** and **capabilities** are derived from text the vendor wrote about itself "
          "(evidence level L1) unless an evidence file adds higher-level evidence. They are *claims*, not verified capabilities.",
          "- **Capability index** = 0.4 × breadth + 0.4 × assurance + 0.2 × framework coverage (weights configurable). "
          "With L1-only evidence, assurance is 25 for every claimed capability, so the index mostly reflects how many "
          "capabilities a one-line description mentions.",
          "- **Maturity tier** comes only from structured fields (employees, funding, IPO status). Unknown data → `unknown`, not a low tier.",
          "- A missing capability means *not evidenced in the sources used*, not *absent from the product*.", ""]
    L += ["## Landscape summary", "", f"- Companies evaluated: **{summary['companies_evaluated']}**",
          f"- In scope (security for AI / AI for security / AI governance): **{summary['in_scope']}**", "",
          "| Segment | Companies |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in sorted(summary["segments"].items(), key=lambda kv: -kv[1])]
    L += ["", "| Maturity tier (in scope) | Companies |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in sorted(summary["maturity_tiers_in_scope"].items(), key=lambda kv: -kv[1])]
    L += ["", "### Claimed capability prevalence (in-scope companies)", "", "| Domain | Companies |", "|---|---|"]
    L += [f"| {T.DOMAIN_BY_ID[k].name} | {v} |" for k, v in summary["capability_domain_prevalence"].items()]
    L += ["", "### OWASP Top 10 for LLM Applications 2025 — share of security-for-AI vendors whose description claims a mapped capability", "",
          "| Risk | Name | Vendors | % |", "|---|---|---|---|"]
    L += [f"| {k} | {v['risk']} | {v['companies']} | {_fmt(v['pct'])} |"
          for k, v in summary["owasp_llm_2025_claimed_coverage_among_security_for_ai"].items()]
    L += ["", "### Data-quality flags raised", "", "| Flag | Count |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in summary["data_quality_flags"].items()]
    if validation:
        L += ["", "## Validation against hand-labelled ground truth", "",
              f"Labelled: {validation['labelled']}, matched to scorecards: {validation['matched']}.",
              "Labels are analyst judgement from the same descriptions (see `validation/LABELING.md`). "
              "`heldout` rows were not inspected while refining patterns.", "",
              "| Split | n | Segment accuracy | Segment macro-F1 | In-scope precision | In-scope recall | In-scope F1 |",
              "|---|---|---|---|---|---|---|"]
        for s in ("all", "dev", "heldout", "high_confidence_labels_only"):
            m = validation[s]
            L.append(f"| {s} | {m['n']} | {_fmt(m.get('segment_accuracy'))} | {_fmt(m.get('segment_macro_f1'))} | "
                     f"{_fmt(m.get('in_scope_precision'))} | {_fmt(m.get('in_scope_recall'))} | {_fmt(m.get('in_scope_f1'))} |")
        L += ["", "Per-segment (all labelled rows):", "", "| Segment | Support | Precision | Recall | F1 |", "|---|---|---|---|---|"]
        for s, v in validation["all"]["per_segment"].items():
            L.append(f"| {s} | {v['support']} | {_fmt(v['precision'])} | {_fmt(v['recall'])} | {_fmt(v['f1'])} |")
        L += ["", "Most frequent confusions (gold → predicted):", ""]
        L += [f"- {k}: {v}" for k, v in sorted(validation["all"]["confusion"].items(), key=lambda kv: -kv[1])[:10]]
    seg_order = {s: i for i, s in enumerate(T.IN_SCOPE_SEGMENTS)}
    top = sorted([c for c in cards if c.in_scope],
                 key=lambda c: (seg_order[c.segment], -(c.capability_index or 0), c.name))
    L += ["", "## In-scope scorecards (grouped by segment, ranked by capability index within segment)", "",
          "Each segment is measured against its own set of capability domains, so the index is only "
          "comparable *within* a segment, not across segments.", "",
          "| Company | Segment | Index | Breadth % | Maturity | Claimed capabilities | Flags |", "|---|---|---|---|---|---|---|"]
    for c in top:
        caps = ", ".join(f.domain_id for f in c.capabilities if f.domain_id in {d.id for d in T.domains_for_segment(c.segment)})
        L.append(f"| {c.name} | {c.segment} | {_fmt(c.capability_index)} | {_fmt(c.breadth_pct)} | {c.maturity_tier} | "
                 f"{caps or '—'} | {', '.join(x.split('(')[0] for x in c.data_quality_flags) or '—'} |")
    excl = [c for c in cards if not c.in_scope]
    L += ["", "## Excluded by the scope gate", "", "| Company | Segment | Why |", "|---|---|---|"]
    for c in sorted(excl, key=lambda c: (c.segment, c.name)):
        L.append(f"| {c.name} | {c.segment} | {'; '.join(c.segment_rationale)[:160]} |")
    path.write_text("\n".join(L) + "\n")
