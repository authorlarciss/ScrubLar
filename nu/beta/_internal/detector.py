"""Hybrid PII detector: structured (iota) + NER names (epsilon).

Merge rule: structured PII wins over NER on overlap. Structured is
deterministic (regex + checksums); NER is statistical. See ADR-0007,
ADR-0008, ADR-0009.
"""

from __future__ import annotations

from nu.beta.public.interfaces import IDetector
from nu.psi.contracts.alpha import (
    DetectionConfig,
    DetectionReport,
    PIIEntity,
    PIIKind,
)
from nu.psi.contracts.epsilon import INameDetector
from nu.psi.contracts.iota import find_structured_pii

__all__ = ["Detector"]


class Detector(IDetector):
    def __init__(self, name_detector: INameDetector) -> None:
        self._name_detector = name_detector

    def detect(self, text: str, config: DetectionConfig) -> DetectionReport:
        structured = tuple(e for e in find_structured_pii(text) if e.kind in config.enabled_kinds)
        ner_entities: tuple[PIIEntity, ...] = ()
        if PIIKind.NAME in config.enabled_kinds:
            ner_entities = self._name_detector.detect(text)
        merged = _merge(structured, ner_entities)
        return DetectionReport(entities=merged, text_length=len(text))


def _merge(structured: tuple[PIIEntity, ...], ner: tuple[PIIEntity, ...]) -> tuple[PIIEntity, ...]:
    """Structured wins on overlap. NER entities not overlapping structured
    are kept. Result sorted by start."""
    chosen = list(structured)
    for ner_entity in ner:
        if not any(_overlaps(ner_entity, kept) for kept in chosen):
            chosen.append(ner_entity)
    chosen.sort(key=lambda item: item.start)
    return tuple(chosen)


def _overlaps(a: PIIEntity, b: PIIEntity) -> bool:
    return a.start < b.end and b.start < a.end
