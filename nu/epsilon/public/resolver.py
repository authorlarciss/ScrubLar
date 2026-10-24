"""Public resolver for epsilon — factory for NER detector."""

from __future__ import annotations

from nu.epsilon.public.interfaces import INameDetector

__all__ = ["EpsilonResolver"]


class EpsilonResolver:
    @staticmethod
    def make_name_detector() -> INameDetector:
        # noinspection PyProtectedMember
        from nu.epsilon._internal.natasha_detector import NatashaNameDetector

        return NatashaNameDetector()
