"""Tests for DOCX and TXT parsers."""

import io

import pytest

from nu.delta.public import DeltaResolver, IDocumentParser
from nu.psi.contracts.alpha import ParsingError, UnsupportedFormatError


@pytest.fixture(scope="module")
def resolver() -> DeltaResolver:
    return DeltaResolver()


def test_make_parser_docx(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("docx")
    assert isinstance(parser, IDocumentParser)
    assert "docx" in parser.supported_extensions


def test_make_parser_txt(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("txt")
    assert isinstance(parser, IDocumentParser)


def test_make_parser_with_dot(resolver: DeltaResolver) -> None:
    assert resolver.make_parser(".docx").supported_extensions == ("docx",)


def test_make_parser_uppercase(resolver: DeltaResolver) -> None:
    assert resolver.make_parser("DOCX").supported_extensions == ("docx",)


def test_make_parser_unsupported(resolver: DeltaResolver) -> None:
    with pytest.raises(UnsupportedFormatError):
        resolver.make_parser("pdf")


# --- TXT ---


def test_txt_parses_utf8(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("txt")
    text = "Привет, Иванов Иван."
    assert parser.parse(text.encode("utf-8")) == text


def test_txt_parses_cp1251(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("txt")
    text = "Привет, Иванов Иван."
    assert parser.parse(text.encode("cp1251")) == text


def test_txt_empty(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("txt")
    assert parser.parse(b"") == ""


def test_txt_bad_encoding(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("txt")
    # 0x98 is undefined in cp1251 and an invalid UTF-8 start byte,
    # so both fallbacks fail.
    with pytest.raises(ParsingError):
        parser.parse(b"\x98")


# --- DOCX ---


def _make_docx(paragraphs: list[str], table: list[list[str]] | None = None) -> bytes:
    from docx import Document

    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    if table:
        t = doc.add_table(rows=len(table), cols=len(table[0]))
        for i, row in enumerate(table):
            for j, cell in enumerate(row):
                t.cell(i, j).text = cell
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def test_docx_parses_paragraphs(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("docx")
    data = _make_docx(["Первый", "Второй", "Третий"])
    result = parser.parse(data)
    assert "Первый" in result
    assert "Второй" in result
    assert "Третий" in result


def test_docx_parses_table(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("docx")
    data = _make_docx(["Документ"], [["Иванов", "Иван"], ["Петров", "Пётр"]])
    result = parser.parse(data)
    assert "Иванов" in result
    assert "Петров" in result


def test_docx_invalid_bytes(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("docx")
    with pytest.raises(ParsingError):
        parser.parse(b"not a docx")


def test_docx_empty_paragraphs(resolver: DeltaResolver) -> None:
    parser = resolver.make_parser("docx")
    data = _make_docx([])
    assert parser.parse(data) == ""
