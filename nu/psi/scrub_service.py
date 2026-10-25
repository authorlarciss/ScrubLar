"""ScrubService: parse → detect → mask.

Orchestration lives in psi (composition root), not in gamma. Gamma
only defines `IScrubService` (what the HTTP layer needs). This class
implements it, using DeltaResolver, IDetector, IMasker from context.
See ADR-0011.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from nu.psi.contracts.alpha import DetectionConfig
from nu.psi.contracts.beta import IDetector, IMasker
from nu.psi.contracts.delta import DeltaResolver
from nu.psi.contracts.gamma import IScrubService, ScrubResult

__all__ = ["ScrubService"]


class ScrubService(IScrubService):
    def __init__(
        self,
        delta_resolver: DeltaResolver,
        detector: IDetector,
        masker: IMasker,
        config: DetectionConfig | None = None,
    ) -> None:
        self._delta = delta_resolver
        self._detector = detector
        self._masker = masker
        self._config = config or DetectionConfig()

    def scrub(self, filename: str, data: bytes) -> ScrubResult:
        path = PurePosixPath(filename)
        extension = path.suffix.lstrip(".").lower() or "txt"
        parser = self._delta.make_parser(extension)
        text = parser.parse(data)
        report = self._detector.detect(text, self._config)
        masked = self._masker.mask(text, report)
        return ScrubResult(
            original_filename=filename,
            original_extension=extension,
            original_text=text,
            masked_text=masked.masked_text,
            report=report,
            mapping=dict(masked.mapping),
        )
