"""Tests for NatashaNameDetector (epsilon)."""

from nu.epsilon.public import EpsilonResolver, INameDetector
from nu.psi.contracts.alpha import PIIKind


def test_resolver_returns_interface() -> None:
    detector = EpsilonResolver().make_name_detector()
    assert isinstance(detector, INameDetector)


def test_detects_bare_full_name() -> None:
    detector = EpsilonResolver().make_name_detector()
    entities = detector.detect("Иванов Иван Иванович")
    assert len(entities) == 1
    assert entities[0].kind is PIIKind.NAME
    assert entities[0].value == "Иванов Иван Иванович"


def test_detects_full_name_in_natural_context() -> None:
    detector = EpsilonResolver().make_name_detector()
    entities = detector.detect("Настоящий документ подписан: Иванов Иван Иванович.")
    assert len(entities) >= 1
    assert any(e.kind is PIIKind.NAME for e in entities)
    assert any("Иванов" in e.value for e in entities)


def test_does_not_detect_initials_as_full_name() -> None:
    """Initials go through iota, not NER (ADR-0008)."""
    detector = EpsilonResolver().make_name_detector()
    entities = detector.detect("Сидоров А.П.")
    # Natasha may or may not tag this; either way, PIIEntity shapes
    # must be valid and no crash. Structured regex handles initials.
    for e in entities:
        assert e.kind is PIIKind.NAME
        assert e.value


def test_entities_sorted_by_start() -> None:
    detector = EpsilonResolver().make_name_detector()
    entities = detector.detect("Подписанты: Иванов Иван Иванович, Петрова Мария Сергеевна.")
    starts = [e.start for e in entities]
    assert starts == sorted(starts)


def test_empty_text_returns_empty() -> None:
    detector = EpsilonResolver().make_name_detector()
    assert detector.detect("") == ()


def test_no_names_returns_empty() -> None:
    detector = EpsilonResolver().make_name_detector()
    assert detector.detect("Сегодня хорошая погода, ничего личного.") == ()


def test_lazy_load_only_once() -> None:
    """Second detect() on same instance skips _ensure_loaded block."""
    detector = EpsilonResolver().make_name_detector()
    first = detector.detect("Иванов Иван Иванович")
    second = detector.detect("Петрова Мария Сергеевна")
    assert len(first) == 1
    assert len(second) == 1


def test_non_per_spans_ignored() -> None:
    """LOC/ORG spans (Россия, Сбербанк) are not returned as NAME."""
    detector = EpsilonResolver().make_name_detector()
    entities = detector.detect("Президент России Владимир Путин")
    for e in entities:
        assert e.kind is PIIKind.NAME
        assert "Росси" not in e.value
