"""Recall/precision on synthetic fixtures (50 docs, seed=42).

Metrics are computed per PII kind, overlap-based: a detected span is
TP if it overlaps a ground truth span of the same kind. Extra detected
spans count as FP; missed ground truth spans count as FN.

Targets from the project brief: recall >= 0.90, precision >= 0.85
(overall). Per-kind thresholds are stricter for structured PII (regex
+ checksums, should be near 1.0) and looser for NAME (NER).
"""

from __future__ import annotations

import pytest

from nu.beta.public import BetaResolver
from nu.epsilon.public import EpsilonResolver
from nu.psi.contracts.alpha import DetectionConfig, PIIEntity, PIIKind
from tau.fixtures.generator import FixtureDocument, generate_documents


@pytest.fixture(scope="module")
def detector():  # type: ignore[no-untyped-def]
    name_detector = EpsilonResolver().make_name_detector()
    return BetaResolver().make_detector(name_detector)


@pytest.fixture(scope="module")
def documents() -> list[FixtureDocument]:
    return generate_documents(seed=42, count=50)


def _score(
    detected: tuple[PIIEntity, ...],
    truth: tuple[tuple[PIIKind, str, int, int], ...],
    kind: PIIKind | None = None,
) -> tuple[int, int, int]:
    """Return (tp, fp, fn), optionally filtered by kind."""
    det = [e for e in detected if kind is None or e.kind is kind]
    gt = [t for t in truth if kind is None or t[0] is kind]
    matched_gt: set[int] = set()
    matched_det: set[int] = set()
    for di, d in enumerate(det):
        for gi, (_gk, _gv, gs, ge) in enumerate(gt):
            if gi in matched_gt:
                continue
            if d.start < ge and gs < d.end:  # overlap
                matched_gt.add(gi)
                matched_det.add(di)
                break
    tp = len(matched_gt)
    fn = len(gt) - tp
    fp = len(det) - len(matched_det)
    return tp, fp, fn


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


@pytest.fixture(scope="module")
def overall_metrics(detector, documents):  # type: ignore[no-untyped-def]
    tp = fp = fn = 0
    for doc in documents:
        report = detector.detect(doc.text, DetectionConfig())
        d_tp, d_fp, d_fn = _score(report.entities, doc.spans)
        tp += d_tp
        fp += d_fp
        fn += d_fn
    return _prf(tp, fp, fn)


def test_overall_recall(overall_metrics) -> None:  # type: ignore[no-untyped-def]
    _p, recall, _f1 = overall_metrics
    assert recall >= 0.90, f"overall recall {recall:.3f} < 0.90"


def test_overall_precision(overall_metrics) -> None:  # type: ignore[no-untyped-def]
    precision, _r, _f1 = overall_metrics
    assert precision >= 0.85, f"overall precision {precision:.3f} < 0.85"


@pytest.mark.parametrize(
    "kind",
    [PIIKind.EMAIL, PIIKind.PHONE, PIIKind.SNILS, PIIKind.INN, PIIKind.PASSPORT],
)
def test_structured_recall_high(detector, documents, kind) -> None:  # type: ignore[no-untyped-def]
    """Structured PII (regex + checksums) must be near-perfect."""
    tp = fp = fn = 0
    for doc in documents:
        report = detector.detect(doc.text, DetectionConfig())
        d_tp, d_fp, d_fn = _score(report.entities, doc.spans, kind=kind)
        tp += d_tp
        fp += d_fp
        fn += d_fn
    precision, recall, _f1 = _prf(tp, fp, fn)
    assert recall >= 0.95, f"{kind.value} recall {recall:.3f} < 0.95"
    assert precision >= 0.95, f"{kind.value} precision {precision:.3f} < 0.95"


def test_name_recall_acceptable(detector, documents) -> None:  # type: ignore[no-untyped-def]
    """NER (Natasha) is statistical — threshold lower than structured."""
    tp = fp = fn = 0
    for doc in documents:
        report = detector.detect(doc.text, DetectionConfig())
        d_tp, d_fp, d_fn = _score(report.entities, doc.spans, kind=PIIKind.NAME)
        tp += d_tp
        fp += d_fp
        fn += d_fn
    _p, recall, _f1 = _prf(tp, fp, fn)
    assert recall >= 0.85, f"NAME recall {recall:.3f} < 0.85"
