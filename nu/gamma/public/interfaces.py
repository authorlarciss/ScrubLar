"""Public interfaces of the gamma module.

`IScrubService` — what the HTTP layer needs: scrub a document,
return masked text and report. Implementation lives in `psi`
(composition root). Gamma does not know about delta/beta/epsilon.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from nu.psi.contracts.alpha import DetectionReport, PIIEntity

__all__ = ["IScrubService", "ScrubResult"]


@dataclass(frozen=True, slots=True)
class ScrubResult:
    """Result of scrubbing a document."""

    original_filename: str
    original_extension: str
    original_text: str
    masked_text: str
    report: DetectionReport
    mapping: dict[str, PIIEntity]

    @property
    def entity_count(self) -> int:
        return len(self.report.entities)


class IScrubService(ABC):
    """Parse bytes → detect PII → mask. Orchestration is in psi."""

    @abstractmethod
    def scrub(self, filename: str, data: bytes) -> ScrubResult:
        """Raises UnsupportedFormatError / ParsingError / DetectionError."""
