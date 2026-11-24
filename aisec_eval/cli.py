"""Command line: python -m aisec_eval evaluate --input FILE [--input FILE ...] --out DIR"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from .evaluate import evaluate_all, load_config
from .ingest import attach_evidence, dedupe, load_any, load_evidence
from .report import summarise, write_csv, write_json, write_markdown
from .validate import compare, load_labels


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="aisec_eval", description="Evaluate AI security vendors")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ev = sub.add_parser("evaluate")
    ev.add_argument("--input", action="append", required=True, help="Crunchbase JSON, CSV or JSON list")
    ev.add_argument("--evidence", help="Evidence JSON adding L2-L4 evidence")
    ev.add_argument("--labels", help="Ground-truth CSV to validate against")
    ev.add_argument("--config", help="Config JSON overriding defaults")
    ev.add_argument("--out", required=True)
    ev.add_argument("--as-of", help="Evaluation date YYYY-MM-DD (default today)")
    a = ap.parse_args(argv)

    cfg = load_config(a.config)
    today = dt.date.fromisoformat(a.as_of) if a.as_of else dt.date.today()
    companies = []
    provenance = [f"Evaluation date: {today.isoformat()}"]
    for p in a.input:
        loaded = load_any(p)
        provenance.append(f"Input `{Path(p).name}`: {len(loaded)} records")
        companies += loaded
    companies, dropped = dedupe(companies)
    if dropped:
        provenance.append(f"Duplicates removed: {len(dropped)} ({', '.join(f'{d}→{k}' for d, k in dropped)})")
    if a.evidence:
        unmatched = attach_evidence(companies, load_evidence(a.evidence))
        provenance.append(f"Evidence file `{Path(a.evidence).name}` attached" +
                          (f"; unmatched companies: {unmatched}" if unmatched else ""))
    cards = evaluate_all(companies, cfg, today)
    validation = compare(cards, load_labels(a.labels)) if a.labels else None

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = summarise(cards)
    write_json(cards, out / "scorecards.json")
    write_csv(cards, out / "scorecards.csv")
    (out / "summary.json").write_text(json.dumps({"summary": summary, "validation": validation}, indent=2, default=str))
    write_markdown(cards, summary, validation, out / "report.md", provenance)
    print(f"Evaluated {len(cards)} companies ({summary['in_scope']} in scope) -> {out}")
    if validation:
        for s in ("all", "dev", "heldout"):
            m = validation[s]
            print(f"  {s:8s} n={m['n']:3d} segment_acc={m['segment_accuracy']:.3f} "
                  f"macroF1={m['segment_macro_f1']:.3f} in_scope_P={m['in_scope_precision']:.3f} "
                  f"R={m['in_scope_recall']:.3f}")
    return 0
