"""Tests for Masker (beta): placeholder replacement."""

import pytest

from nu.beta.public import BetaResolver, IMasker
from nu.psi.contracts.alpha import (
    DetectionReport,
    PIIEntity,
    PIIKind,
)


@pytest.fixture(scope="module")
def masker() -> IMasker:
    return BetaResolver().make_masker()


def test_resolver_returns_interface(masker: IMasker) -> None:
    assert isinstance(masker, IMasker)


def test_empty_report_returns_text_unchanged(masker: IMasker) -> None:
    text = "Ничего личного."
    report = DetectionReport(entities=(), text_length=len(text))
    result = masker.mask(text, report)
    assert result.masked_text == text
    assert dict(result.mapping) == {}
    assert result.report is report


def test_single_entity_replaced(masker: IMasker) -> None:
    text = "Звоните: +79991234567"
    entity = PIIEntity(kind=PIIKind.PHONE, value="+79991234567", start=9, end=21)
    report = DetectionReport(entities=(entity,), text_length=len(text))
    result = masker.mask(text, report)
    assert result.masked_text == "Звоните: <PHONE_1>"
    assert dict(result.mapping) == {"<PHONE_1>": entity}


def test_multiple_same_kind_numbered(masker: IMasker) -> None:
    text = "+79991234567 и +79997654321"
    e1 = PIIEntity(kind=PIIKind.PHONE, value="+79991234567", start=0, end=12)
    e2 = PIIEntity(kind=PIIKind.PHONE, value="+79997654321", start=15, end=27)
    report = DetectionReport(entities=(e1, e2), text_length=len(text))
    result = masker.mask(text, report)
    assert result.masked_text == "<PHONE_1> и <PHONE_2>"
    assert dict(result.mapping) == {"<PHONE_1>": e1, "<PHONE_2>": e2}


def test_multiple_kinds_each_counted_separately(masker: IMasker) -> None:
    text = "Иванов +79991234567 test@example.com"
    e_name = PIIEntity(kind=PIIKind.NAME, value="Иванов", start=0, end=6)
    e_phone = PIIEntity(kind=PIIKind.PHONE, value="+79991234567", start=7, end=19)
    e_email = PIIEntity(kind=PIIKind.EMAIL, value="test@example.com", start=20, end=36)
    report = DetectionReport(entities=(e_name, e_phone, e_email), text_length=len(text))
    result = masker.mask(text, report)
    assert result.masked_text == "<NAME_1> <PHONE_1> <EMAIL_1>"
    assert set(result.mapping.keys()) == {"<NAME_1>", "<PHONE_1>", "<EMAIL_1>"}


def test_entity_at_start(masker: IMasker) -> None:
    text = "Иванов Иван, привет"
    entity = PIIEntity(kind=PIIKind.NAME, value="Иванов Иван", start=0, end=11)
    report = DetectionReport(entities=(entity,), text_length=len(text))
    result = masker.mask(text, report)
    assert result.masked_text == "<NAME_1>, привет"


def test_entity_at_end(masker: IMasker) -> None:
    text = "Привет, Иванов Иван"
    entity = PIIEntity(kind=PIIKind.NAME, value="Иванов Иван", start=8, end=19)
    report = DetectionReport(entities=(entity,), text_length=len(text))
    result = masker.mask(text, report)
    assert result.masked_text == "Привет, <NAME_1>"


def test_consecutive_entities_no_separator(masker: IMasker) -> None:
    text = "+79991234567+79997654321"
    e1 = PIIEntity(kind=PIIKind.PHONE, value="+79991234567", start=0, end=12)
    e2 = PIIEntity(kind=PIIKind.PHONE, value="+79997654321", start=12, end=24)
    report = DetectionReport(entities=(e1, e2), text_length=len(text))
    result = masker.mask(text, report)
    assert result.masked_text == "<PHONE_1><PHONE_2>"


def test_mapping_is_readonly(masker: IMasker) -> None:
    text = "+79991234567"
    entity = PIIEntity(kind=PIIKind.PHONE, value="+79991234567", start=0, end=12)
    report = DetectionReport(entities=(entity,), text_length=len(text))
    result = masker.mask(text, report)
    from collections.abc import MutableMapping

    assert not isinstance(result.mapping, MutableMapping)


def test_mask_is_idempotent(masker: IMasker) -> None:
    text = "Иванов Иван, +79991234567"
    e1 = PIIEntity(kind=PIIKind.NAME, value="Иванов Иван", start=0, end=11)
    e2 = PIIEntity(kind=PIIKind.PHONE, value="+79991234567", start=13, end=25)
    report = DetectionReport(entities=(e1, e2), text_length=len(text))
    r1 = masker.mask(text, report)
    r2 = masker.mask(text, report)
    assert r1.masked_text == r2.masked_text
    assert dict(r1.mapping) == dict(r2.mapping)
