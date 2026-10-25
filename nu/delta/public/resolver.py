"""Public resolver for delta — factory for document parsers."""

from __future__ import annotations

from nu.delta.public.interfaces import IDocumentParser
from nu.psi.contracts.alpha import UnsupportedFormatError

__all__ = ["DeltaResolver"]


class DeltaResolver:
    @staticmethod
    def make_parser(extension: str) -> IDocumentParser:
        """Return parser for the given file extension (no dot, lowercase).

        Raises `UnsupportedFormatError` for unsupported extensions.
        """
        ext = extension.lower().lstrip(".")
        if ext == "docx":
            # noinspection PyProtectedMember
            from nu.delta._internal.docx_parser import DocxParser

            return DocxParser()
        if ext == "txt":
            # noinspection PyProtectedMember
            from nu.delta._internal.txt_parser import TxtParser

            return TxtParser()
        raise UnsupportedFormatError(f"unsupported extension: {extension!r}")
