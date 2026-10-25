"""Public interfaces of the beta module.

`IDetector` — structured PII (iota) + NER names (epsilon).
See ADR-0007 (core contract), ADR-0009 (scaffold removal).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from nu.psi.contracts.alpha import DetectionConfig, DetectionReport

__all__ = ["IDetector"]


class IDetector(ABC):
    """Detect PII in text: structured (regex + checksums) and NER names.

    Returns a DetectionReport with non-overlapping entities, sorted by
    start. Structured PII wins over NER on overlap (deterministic vs
    statistical). See ADR-0007, ADR-0008.
    """

    @abstractmethod
    def detect(self, text: str, config: DetectionConfig) -> DetectionReport:
        """Detect PII in text according to config."""
