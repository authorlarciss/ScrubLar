"""Evaluate Detector on synthetic fixtures; emit JSON report.

Usage:
    python omega/scripts/evaluate.py [--seed 42] [--count 50] [--out report.json]

Report includes per-kind precision/recall/F1 and per-document misses
for manual inspection. Used for coursework and ADR verification.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from nu.beta.public import BetaResolver
from nu.epsilon.public import EpsilonResolver
from nu.psi.contracts.alpha import DetectionConfig, PIIEntity, PIIKind
from tau.fixtures.generator import generate_documents


def _score(
    detected: tuple[PIIEntity, ...],
    truth: tuple[tuple[PIIKind, str, int, int], ...],
) -> dict[str, tuple[int, int, int]]:
    """Per-kind (tp, fp, fn)."""
    stats: dict[str, tuple[int, int, int]] = {}
    for kind in PIIKind:
        det = [e for e in detected if e.kind is kind]
        gt = [t for t in truth if t[0] is kind]
        matched_gt: set[int] = set()
        matched_det: set[int] = set()
        for di, d in enumerate(det):
            for gi, (_gk, _gv, gs, ge) in enumerate(gt):
                if gi in matched_gt:
                    continue
                if d.start < ge and gs < d.end:
                    matched_gt.add(gi)
                    matched_det.add(di)
                    break
        tp = len(matched_gt)
        fn = len(gt) - tp
        fp = len(det) - len(matched_det)
        stats[kind.value] = (tp, fp, fn)
    return stats


def _prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return {"precision": p, "recall": r, "f1": f}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    docs = generate_documents(seed=args.seed, count=args.count)
    name_detector = EpsilonResolver().make_name_detector()
    detector = BetaResolver().make_detector(name_detector)

    overall = defaultdict(lambda: [0, 0, 0])
    per_doc: list[dict] = []
    for doc in docs:
        report = detector.detect(doc.text, DetectionConfig())
        stats = _score(report.entities, doc.spans)
        for kind, (tp, fp, fn) in stats.items():
            overall[kind][0] += tp
            overall[kind][1] += fp
            overall[kind][2] += fn
        misses = [
            t
            for t in doc.spans
            if not any(d.start < t[3] and t[2] < d.end for d in report.entities)
        ]
        if misses:
            per_doc.append(
                {
                    "name": doc.name,
                    "misses": [
                        {"kind": k.value, "value": v, "start": s, "end": e}
                        for (k, v, s, e) in misses
                    ],
                }
            )

    report = {
        "seed": args.seed,
        "count": args.count,
        "overall": {
            kind: {**_prf(tp, fp, fn), "tp": tp, "fp": fp, "fn": fn}
            for kind, (tp, fp, fn) in overall.items()
        },
        "documents_with_misses": per_doc,
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
