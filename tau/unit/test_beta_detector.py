"""Tests for Detector (beta): structured + NER merge."""

import pytest

from nu.beta.public import BetaResolver, IDetector
from nu.epsilon.public import EpsilonResolver, INameDetector
from nu.psi.contracts.alpha import DetectionConfig, PIIKind


@pytest.fixture(scope="module")
def name_detector() -> INameDetector:
    return EpsilonResolver().make_name_detector()


@pytest.fixture(scope="module")
def detector(name_detector: INameDetector) -> IDetector:
    return BetaResolver().make_detector(name_detector)


def test_resolver_returns_interface(detector: IDetector) -> None:
    assert isinstance(detector, IDetector)


def test_detect_mixed_pii(detector: IDetector) -> None:
    text = (
        "Клиент Иванов Иван Иванович, телефон +79991234567, "
        "email test@example.com, СНИЛС 112-233-445 95."
    )
    report = detector.detect(text, DetectionConfig())
    kinds = {e.kind for e in report.entities}
    assert PIIKind.NAME in kinds
    assert PIIKind.PHONE in kinds
    assert PIIKind.EMAIL in kinds
    assert PIIKind.SNILS in kinds


def test_detect_initials_via_structured(detector: IDetector) -> None:
    report = detector.detect("Сидоров А.П.", DetectionConfig())
    assert len(report.entities) == 1
    assert report.entities[0].kind is PIIKind.NAME
    assert report.entities[0].value == "Сидоров А.П."


def test_detect_respects_enabled_kinds(detector: IDetector) -> None:
    text = "Иванов Иван Иванович, телефон +79991234567."
    config = DetectionConfig(enabled_kinds=frozenset({PIIKind.PHONE}))
    report = detector.detect(text, config)
    assert len(report.entities) == 1
    assert report.entities[0].kind is PIIKind.PHONE


def test_detect_name_skipped_when_disabled(detector: IDetector) -> None:
    """NER is not called when NAME is not in enabled_kinds."""
    text = "Иванов Иван Иванович"
    config = DetectionConfig(enabled_kinds=frozenset({PIIKind.PHONE}))
    report = detector.detect(text, config)
    assert report.entities == ()


def test_detect_empty_text(detector: IDetector) -> None:
    report = detector.detect("", DetectionConfig())
    assert report.entities == ()
    assert report.text_length == 0


def test_detect_no_pii(detector: IDetector) -> None:
    report = detector.detect("Сегодня хорошая погода.", DetectionConfig())
    assert report.entities == ()


def test_detect_sorted_non_overlapping(detector: IDetector) -> None:
    text = "Иванов Иван Иванович, +79991234567, test@example.com"
    report = detector.detect(text, DetectionConfig())
    for prev, curr in zip(report.entities, report.entities[1:], strict=False):
        assert prev.end <= curr.start
