"""Public interfaces of the beta module.

- `IDetector` — structured PII (iota) + NER names (epsilon).
- `IMasker` — replace detected PII with placeholders.

See ADR-0007 (core contract), ADR-0009 (scaffold removal).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from nu.psi.contracts.alpha import (
    DetectionConfig,
    DetectionReport,
    MaskResult,
)

__all__ = ["IDetector", "IMasker"]


class IDetector(ABC):
    """Detect PII in text: structured (regex + checksums) and NER names.

    Returns a DetectionReport with non-overlapping entities, sorted by
    start. Structured PII wins over NER on overlap (deterministic vs
    statistical). See ADR-0007, ADR-0008.
    """

    @abstractmethod
    def detect(self, text: str, config: DetectionConfig) -> DetectionReport:
        """Detect PII in text according to config."""


class IMasker(ABC):
    """Replace PII entities with placeholders.

    Placeholder format: `<KIND_N>` where KIND is PIIKind.value
    (NAME, PHONE, EMAIL, SNILS, INN, PASSPORT) and N is a per-kind
    counter starting at 1. Example: `<NAME_1>`, `<PHONE_1>`,
    `<PHONE_2>`.

    Mapping placeholder -> PIIEntity lives in memory only, never
    persisted. See ADR-0007.
    """

    @abstractmethod
    def mask(self, text: str, report: DetectionReport) -> MaskResult:
        """Replace entities in text with placeholders, return mapping."""
