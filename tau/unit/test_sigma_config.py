"""Тесты LoggingConfig."""

from dataclasses import FrozenInstanceError

import pytest

from nu.psi.contracts.sigma import LoggingConfig


def test_logging_config_defaults() -> None:
    """Дефолтные значения."""
    cfg = LoggingConfig()
    assert cfg.level == "INFO"
    assert cfg.format == "text"
    assert cfg.include_context is True
    assert cfg.stream == "stderr"


def test_logging_config_frozen() -> None:
    """LoggingConfig — frozen dataclass."""
    cfg = LoggingConfig()
    with pytest.raises(FrozenInstanceError):
        setattr(cfg, "level", "DEBUG")  # noqa: B010


def test_logging_config_custom() -> None:
    """Кастомные значения."""
    cfg = LoggingConfig(level="DEBUG", format="json", stream="stdout")
    assert cfg.level == "DEBUG"
    assert cfg.format == "json"
    assert cfg.stream == "stdout"
