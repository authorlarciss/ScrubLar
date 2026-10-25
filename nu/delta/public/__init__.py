"""Public API of the delta module."""

from nu.delta.public.interfaces import IDocumentParser as IDocumentParser
from nu.delta.public.resolver import DeltaResolver as DeltaResolver

__all__ = ["DeltaResolver", "IDocumentParser"]
