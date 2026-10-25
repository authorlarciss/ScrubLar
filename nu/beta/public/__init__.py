"""Public API of the beta module."""

from nu.beta.public.interfaces import IDetector as IDetector
from nu.beta.public.resolver import BetaResolver as BetaResolver

__all__ = ["BetaResolver", "IDetector"]
