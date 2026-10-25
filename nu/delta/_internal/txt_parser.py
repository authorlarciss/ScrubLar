"""TXT parser: UTF-8 with cp1251 fallback."""

from __future__ import annotations

from nu.delta.public.interfaces import IDocumentParser
from nu.psi.contracts.alpha import ParsingError

__all__ = ["TxtParser"]


class TxtParser(IDocumentParser):
    supported_extensions = ("txt",)

    def parse(self, data: bytes) -> str:
        if not data:
            return ""
        for encoding in ("utf-8", "cp1251"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise ParsingError("TXT is neither UTF-8 nor cp1251")
