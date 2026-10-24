"""Public interfaces of the epsilon module."""

from __future__ import annotations

from abc import ABC, abstractmethod

from nu.psi.contracts.alpha import PIIEntity

__all__ = ["INameDetector"]


class INameDetector(ABC):
    """NER-based person name detector.

    Returns PIIEntity(kind=PIIKind.NAME) for each full name found.
    Initials ("Сидоров А.П.") are NOT this detector's job — they go
    through iota.find_initials (structured regex). See ADR-0008.
    """

    @abstractmethod
    def detect(self, text: str) -> tuple[PIIEntity, ...]:
        """Detect full person names in text."""
