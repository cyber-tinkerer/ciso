"""Measure the classifier against hand-labelled ground truth.

The labelled rows are split deterministically by row order: even rows = `dev`
(may be inspected when refining patterns), odd rows = `heldout` (only metrics
are looked at). Reporting both makes over-fitting visible.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from . import taxonomy as T
from .models import Scorecard


def load_labels(path: str | Path) -> list[dict]:
    with Path(path).open(newline="") as f:
        rows = list(csv.DictReader(f))
    for i, r in enumerate(rows):
        r["split"] = "dev" if i % 2 == 0 else "heldout"
    return rows


def _prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else None
    return p, r, f


def metrics(pairs: list[tuple[str, str]]) -> dict:
    """pairs = [(gold, predicted)]"""
    n = len(pairs)
    out = {"n": n}
    if not n:
        return out
    out["segment_accuracy"] = sum(g == p for g, p in pairs) / n
    gin = [(g in T.IN_SCOPE_SEGMENTS, p in T.IN_SCOPE_SEGMENTS) for g, p in pairs]
    tp = sum(g and p for g, p in gin); fp = sum(p and not g for g, p in gin); fn = sum(g and not p for g, p in gin)
    out["in_scope_precision"], out["in_scope_recall"], out["in_scope_f1"] = _prf(tp, fp, fn)
    out["in_scope_accuracy"] = sum(g == p for g, p in gin) / n
    per = {}
    for s in T.ALL_SEGMENTS:
        tp = sum(g == s and p == s for g, p in pairs)
        fp = sum(g != s and p == s for g, p in pairs)
        fn = sum(g == s and p != s for g, p in pairs)
        pr, rc, f1 = _prf(tp, fp, fn)
        per[s] = {"support": tp + fn, "precision": pr, "recall": rc, "f1": f1}
    out["per_segment"] = per
    f1s = [v["f1"] or 0.0 for v in per.values() if v["support"]]
    out["segment_macro_f1"] = sum(f1s) / len(f1s) if f1s else None
    out["confusion"] = {f"{g}->{p}": c for (g, p), c in sorted(Counter(pairs).items()) if g != p}
    return out


def compare(scorecards: list[Scorecard], labels: list[dict]) -> dict:
    by_name = {s.name: s for s in scorecards}
    missing = [r["name"] for r in labels if r["name"] not in by_name]
    rows = [(r, by_name[r["name"]]) for r in labels if r["name"] in by_name]
    res = {"labelled": len(labels), "matched": len(rows), "unmatched_labels": missing}
    for split in ("all", "dev", "heldout"):
        sel = [(r["segment"], s.segment) for r, s in rows if split == "all" or r["split"] == split]
        res[split] = metrics(sel)
    hi = [(r["segment"], s.segment) for r, s in rows if r["label_confidence"] == "high"]
    res["high_confidence_labels_only"] = metrics(hi)
    res["errors"] = [{"name": r["name"], "gold": r["segment"], "pred": s.segment, "split": r["split"],
                      "label_confidence": r["label_confidence"]}
                     for r, s in rows if r["segment"] != s.segment]
    return res
