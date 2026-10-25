"""Tests for FastAPI app (gamma)."""

import io
from typing import Never

import pytest
from docx import Document
from fastapi.testclient import TestClient

from nu.beta.public import BetaResolver
from nu.delta.public import DeltaResolver
from nu.epsilon.public import EpsilonResolver
from nu.gamma.public import GammaResolver
from nu.psi.scrub_service import ScrubService


@pytest.fixture(scope="module")
def client() -> TestClient:
    name_detector = EpsilonResolver().make_name_detector()
    detector = BetaResolver().make_detector(name_detector)
    masker = BetaResolver().make_masker()
    service = ScrubService(
        delta_resolver=DeltaResolver(),
        detector=detector,
        masker=masker,
    )
    app = GammaResolver().make_app(service)
    return TestClient(app)


def test_index_returns_html(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "ScrubLar" in response.text
    assert "152-ФЗ" in response.text


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_mask_txt(client: TestClient) -> None:
    data = "Клиент Иванов Иван, телефон +79991234567.".encode()
    response = client.post(
        "/mask",
        files={"file": ("doc.txt", data, "text/plain")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["original_filename"] == "doc.txt"
    assert payload["original_extension"] == "txt"
    assert "Иванов" not in payload["masked_text"]
    assert len(payload["entities"]) >= 1


def test_mask_docx(client: TestClient) -> None:
    doc = Document()
    doc.add_paragraph("Клиент Иванов Иван Иванович")
    buf = io.BytesIO()
    doc.save(buf)
    response = client.post(
        "/mask",
        files={
            "file": (
                "doc.docx",
                buf.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 200
    assert "Иванов" not in response.json()["masked_text"]


def test_mask_unsupported_format(client: TestClient) -> None:
    response = client.post(
        "/mask",
        files={"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert response.status_code == 415


def test_mask_empty_file(client: TestClient) -> None:
    response = client.post(
        "/mask",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 400


def test_mask_file_too_large(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """413 when file exceeds _MAX_UPLOAD_BYTES."""
    import nu.gamma._internal.api as api_module

    monkeypatch.setattr(api_module, "_MAX_UPLOAD_BYTES", 10)
    response = client.post(
        "/mask",
        files={"file": ("big.txt", b"x" * 100, "text/plain")},
    )
    assert response.status_code == 413


def test_mask_domain_error_returns_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generic ScrubLarError (e.g. DetectionError) → 500."""
    from fastapi.testclient import TestClient

    from nu.gamma.public import GammaResolver
    from nu.psi.contracts.alpha import DetectionError

    class FailingService:
        def scrub(self, filename: str, data: bytes) -> Never:
            raise DetectionError("boom")

    app = GammaResolver().make_app(FailingService())  # type: ignore[arg-type]
    client = TestClient(app)
    response = client.post(
        "/mask",
        files={"file": ("doc.txt", b"text", "text/plain")},
    )
    assert response.status_code == 500
    assert "boom" in response.json()["detail"]


def test_mask_invalid_docx_returns_422(client: TestClient) -> None:
    """Invalid DOCX bytes -> DocxParser raises ParsingError -> 422."""
    response = client.post(
        "/mask",
        files={
            "file": (
                "bad.docx",
                b"this is not a valid zip / docx file",
                "application/octet-stream",
            )
        },
    )
    assert response.status_code == 422
    assert "invalid DOCX" in response.json()["detail"]
