"""Public resolver for beta — factory for the PII detector."""

from __future__ import annotations

from nu.beta.public.interfaces import IDetector, IMasker
from nu.psi.contracts.epsilon import INameDetector

__all__ = ["BetaResolver"]


class BetaResolver:
    @staticmethod
    def make_detector(name_detector: INameDetector) -> IDetector:
        # noinspection PyProtectedMember
        from nu.beta._internal.detector import Detector

        return Detector(name_detector=name_detector)

    @staticmethod
    def make_masker() -> IMasker:
        # noinspection PyProtectedMember
        from nu.beta._internal.masker import Masker

        return Masker()
