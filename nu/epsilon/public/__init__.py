"""Public API of the epsilon module.

NER-based PII detectors (currently: person names via Natasha).
"""

from nu.epsilon.public.interfaces import INameDetector as INameDetector
from nu.epsilon.public.resolver import EpsilonResolver as EpsilonResolver

__all__ = ["EpsilonResolver", "INameDetector"]
