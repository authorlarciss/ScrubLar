"""Tests for PII domain types in nu.alpha.public.types."""

from collections.abc import MutableMapping
from dataclasses import FrozenInstanceError

import pytest

from nu.psi.contracts.alpha import (
    DetectionConfig,
    DetectionError,
    DetectionReport,
    MaskingError,
    MaskResult,
    ParsingError,
    PIIEntity,
    PIIKind,
    ScrubLarError,
    UnsupportedFormatError,
)


def test_pii_kind_members() -> None:
    assert set(PIIKind) == {
        PIIKind.NAME,
        PIIKind.PHONE,
        PIIKind.EMAIL,
        PIIKind.SNILS,
        PIIKind.INN,
        PIIKind.PASSPORT,
    }


def test_pii_kind_is_str_enum() -> None:
    assert PIIKind.NAME == "NAME"
    assert isinstance(PIIKind.NAME, str)


# --- PIIEntity ---


def test_pii_entity_valid() -> None:
    e = PIIEntity(kind=PIIKind.PHONE, value="+79991234567", start=5, end=17)
    assert e.kind is PIIKind.PHONE
    assert e.value == "+79991234567"
    assert e.start == 5
    assert e.end == 17


def test_pii_entity_frozen() -> None:
    e = PIIEntity(kind=PIIKind.PHONE, value="+7999", start=0, end=5)
    with pytest.raises(FrozenInstanceError):
        setattr(e, "value", "other")  # noqa: B010


def test_pii_entity_rejects_negative_start() -> None:
    with pytest.raises(ValueError, match="start must be >= 0"):
        PIIEntity(kind=PIIKind.EMAIL, value="x", start=-1, end=0)


def test_pii_entity_rejects_end_le_start() -> None:
    with pytest.raises(ValueError, match="end must be > start"):
        PIIEntity(kind=PIIKind.EMAIL, value="", start=5, end=5)


def test_pii_entity_rejects_span_value_mismatch() -> None:
    with pytest.raises(ValueError, match="span.*!=.*value length"):
        PIIEntity(kind=PIIKind.EMAIL, value="ab", start=0, end=5)


# --- DetectionReport ---


def test_detection_report_empty() -> None:
    report = DetectionReport(entities=(), text_length=100)
    assert report.entities == ()
    assert report.text_length == 100


def test_detection_report_non_overlapping() -> None:
    e1 = PIIEntity(kind=PIIKind.EMAIL, value="a@b", start=0, end=3)
    e2 = PIIEntity(kind=PIIKind.PHONE, value="+7", start=5, end=7)
    report = DetectionReport(entities=(e1, e2), text_length=20)
    assert len(report.entities) == 2


def test_detection_report_rejects_negative_text_length() -> None:
    with pytest.raises(ValueError, match="text_length must be >= 0"):
        DetectionReport(entities=(), text_length=-1)


def test_detection_report_rejects_overlap() -> None:
    e1 = PIIEntity(kind=PIIKind.EMAIL, value="a@b", start=0, end=3)
    e2 = PIIEntity(kind=PIIKind.PHONE, value="bcd", start=2, end=5)
    with pytest.raises(ValueError, match="entities overlap"):
        DetectionReport(entities=(e1, e2), text_length=20)


def test_detection_report_rejects_out_of_bounds() -> None:
    e = PIIEntity(kind=PIIKind.EMAIL, value="a@b", start=0, end=3)
    with pytest.raises(ValueError, match="entity end 3 > text_length 2"):
        DetectionReport(entities=(e,), text_length=2)


# --- MaskResult ---


def _one_entity_report() -> tuple[PIIEntity, DetectionReport]:
    e = PIIEntity(kind=PIIKind.EMAIL, value="a@b", start=0, end=3)
    return e, DetectionReport(entities=(e,), text_length=3)


def test_mask_result_valid() -> None:
    e, report = _one_entity_report()
    result = MaskResult(
        masked_text="<EMAIL_1>",
        mapping={"<EMAIL_1>": e},
        report=report,
    )
    assert result.masked_text == "<EMAIL_1>"
    assert result.mapping["<EMAIL_1>"] == e


def test_mask_result_mapping_is_readonly() -> None:
    e, report = _one_entity_report()
    result = MaskResult(
        masked_text="<EMAIL_1>",
        mapping={"<EMAIL_1>": e},
        report=report,
    )
    assert not isinstance(result.mapping, MutableMapping), "mapping must be read-only"


# --- DetectionConfig ---


def test_detection_config_defaults() -> None:
    cfg = DetectionConfig()
    assert cfg.enabled_kinds == frozenset(PIIKind)
    assert cfg.ner_model_version is None


def test_detection_config_custom() -> None:
    cfg = DetectionConfig(
        enabled_kinds=frozenset({PIIKind.EMAIL}),
        ner_model_version="gl ner-v1",
    )
    assert cfg.enabled_kinds == frozenset({PIIKind.EMAIL})
    assert cfg.ner_model_version == "gl ner-v1"


# --- Errors ---


def test_errors_hierarchy() -> None:
    assert issubclass(DetectionError, ScrubLarError)
    assert issubclass(MaskingError, ScrubLarError)
    assert issubclass(ParsingError, ScrubLarError)
    assert issubclass(UnsupportedFormatError, ParsingError)
