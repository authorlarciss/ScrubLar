"""Тесты публичного API sigma."""

import logging

from nu.psi.contracts.sigma import clear_context, get_logger, set_request_id, set_user_id


def test_get_logger_returns_logger() -> None:
    """get_logger возвращает logging.Logger."""
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)


def test_get_logger_has_nu_prefix() -> None:
    """Логгеры проекта — под префиксом "nu."."""
    logger = get_logger("test.module")
    assert logger.name == "nu.test.module"


def test_get_logger_no_double_prefix() -> None:
    """Если name уже под "nu.", префикс не дублируется."""
    logger = get_logger("nu.psi.application")
    assert logger.name == "nu.psi.application"


def test_get_logger_exact_nu() -> None:
    """get_logger("nu") возвращает корневой логгер без изменений."""
    logger = get_logger("nu")
    assert logger.name == "nu"


def test_get_logger_can_be_called_before_setup() -> None:
    """get_logger работает без настройки — дефолтное поведение logging."""
    logger = get_logger("before_setup")
    logger.info("this should not raise")


def test_set_get_context() -> None:
    """Установка request_id / user_id."""
    from nu.sigma.public.context import request_id_var, user_id_var

    clear_context()
    assert request_id_var.get() is None
    assert user_id_var.get() is None

    set_request_id("req-123")
    set_user_id(42)

    assert request_id_var.get() == "req-123"
    assert user_id_var.get() == 42

    clear_context()
    assert request_id_var.get() is None
    assert user_id_var.get() is None
