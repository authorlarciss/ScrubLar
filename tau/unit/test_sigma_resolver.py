"""Тесты SigmaResolver."""

import logging

from nu.psi.contracts.sigma import LoggingConfig, SigmaResolver


def test_setup_logging_configures_nu_logger() -> None:
    """setup_logging настраивает корневой логгер "nu"."""
    resolver = SigmaResolver()
    resolver.setup_logging(LoggingConfig(level="DEBUG", format="text"))

    nu_logger = logging.getLogger("nu")
    assert nu_logger.level == logging.DEBUG
    assert len(nu_logger.handlers) >= 1


def test_setup_logging_idempotent() -> None:
    """Повторный setup заменяет handlers, не дублирует."""
    resolver = SigmaResolver()

    resolver.setup_logging(LoggingConfig(level="INFO"))
    count_first = len(logging.getLogger("nu").handlers)

    resolver.setup_logging(LoggingConfig(level="DEBUG"))
    count_second = len(logging.getLogger("nu").handlers)

    assert count_first == count_second


def test_setup_logging_json_format() -> None:
    """setup_logging с json-форматом."""
    resolver = SigmaResolver()
    resolver.setup_logging(LoggingConfig(level="INFO", format="json"))

    nu_logger = logging.getLogger("nu")
    handler = nu_logger.handlers[0]
    formatter = handler.formatter
    assert formatter is not None
    assert type(formatter).__name__ == "JsonFormatter"
