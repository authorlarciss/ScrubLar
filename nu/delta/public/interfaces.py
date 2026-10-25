"""Public interfaces of the delta module.

`IDocumentParser` — file bytes -> text. Implementations differ by
format (DOCX, TXT). Dispatch by extension is in DeltaResolver.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

__all__ = ["IDocumentParser"]


class IDocumentParser(ABC):
    """Parse document bytes into plain text.

    `supported_extensions` — lowercase, no dot (e.g. ("docx",)).
    Raises `ParsingError` (or subclass) if bytes cannot be parsed.
    """

    supported_extensions: tuple[str, ...] = ()

    @abstractmethod
    def parse(self, data: bytes) -> str:
        """Return plain text extracted from document bytes."""
