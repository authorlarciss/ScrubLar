"""Tests for ScrubService (psi): parse -> detect -> mask."""

import io

import pytest
from docx import Document

from nu.beta.public import BetaResolver
from nu.delta.public import DeltaResolver
from nu.epsilon.public import EpsilonResolver
from nu.psi.contracts.alpha import UnsupportedFormatError
from nu.psi.contracts.gamma import IScrubService
from nu.psi.scrub_service import ScrubService


@pytest.fixture(scope="module")
def scrub_service() -> IScrubService:
    name_detector = EpsilonResolver().make_name_detector()
    detector = BetaResolver().make_detector(name_detector)
    masker = BetaResolver().make_masker()
    return ScrubService(
        delta_resolver=DeltaResolver(),
        detector=detector,
        masker=masker,
    )


def test_scrub_service_implements_interface(
    scrub_service: IScrubService,
) -> None:
    assert isinstance(scrub_service, IScrubService)


def test_scrub_txt(scrub_service: IScrubService) -> None:
    data = "Клиент Иванов Иван, телефон +79991234567.".encode()
    result = scrub_service.scrub("doc.txt", data)
    assert result.original_extension == "txt"
    assert "Иванов" not in result.masked_text
    assert result.entity_count >= 1


def test_scrub_docx(scrub_service: IScrubService) -> None:
    doc = Document()
    doc.add_paragraph("Клиент: Иванов Иван Иванович")
    doc.add_paragraph("Телефон: +79991234567")
    buf = io.BytesIO()
    doc.save(buf)
    result = scrub_service.scrub("doc.docx", buf.getvalue())
    assert result.original_extension == "docx"
    assert "Иванов" not in result.masked_text


def test_scrub_no_extension_defaults_txt(
    scrub_service: IScrubService,
) -> None:
    result = scrub_service.scrub("noext", "Иванов Иван".encode())
    assert result.original_extension == "txt"


def test_scrub_unsupported_extension(scrub_service: IScrubService) -> None:
    with pytest.raises(UnsupportedFormatError):
        scrub_service.scrub("doc.pdf", b"%PDF-1.4")


def test_scrub_mapping_matches_entities(scrub_service: IScrubService) -> None:
    result = scrub_service.scrub("doc.txt", "Иванов Иван, +79991234567".encode())
    assert len(result.mapping) == result.entity_count
