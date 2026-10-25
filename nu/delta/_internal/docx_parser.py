"""DOCX parser via python-docx."""

from __future__ import annotations

import io

from nu.delta.public.interfaces import IDocumentParser
from nu.psi.contracts.alpha import ParsingError

__all__ = ["DocxParser"]


class DocxParser(IDocumentParser):
    supported_extensions = ("docx",)

    def parse(self, data: bytes) -> str:
        from docx import Document

        try:
            document = Document(io.BytesIO(data))
        except Exception as exc:
            raise ParsingError(f"invalid DOCX: {exc}") from exc
        parts: list[str] = [p.text for p in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    parts.append(cell.text)
        return "\n".join(parts)
