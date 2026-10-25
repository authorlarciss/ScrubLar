"""Public API of the gamma module."""

from nu.gamma.public.interfaces import IScrubService as IScrubService
from nu.gamma.public.interfaces import ScrubResult as ScrubResult
from nu.gamma.public.resolver import GammaResolver as GammaResolver

__all__ = ["GammaResolver", "IScrubService", "ScrubResult"]
