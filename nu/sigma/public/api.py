"""Публичный API модуля sigma.

get_logger — работает всегда (даже без настройки).
Остальное (context) — опционально.
"""

import logging

from nu.sigma.public.context import request_id_var, user_id_var


def get_logger(name: str) -> logging.Logger:
    """Получить логгер по имени.

    Если name уже начинается с "nu." — не добавляет префикс повторно.

    Пример:
        get_logger(__name__) в nu.beta.compiler
        → logging.getLogger("nu.beta.compiler")
        get_logger("custom") → logging.getLogger("nu.custom")
    """
    if name.startswith("nu.") or name == "nu":
        return logging.getLogger(name)
    return logging.getLogger(f"nu.{name}")


def set_request_id(request_id: str) -> None:
    """Установить request_id для текущей задачи.

    В async-коде изолировано между задачами.
    """
    request_id_var.set(request_id)


def set_user_id(user_id: int) -> None:
    """Установить user_id для текущей задачи."""
    user_id_var.set(user_id)


def clear_context() -> None:
    """Сбросить контекстные поля (request_id, user_id)."""
    request_id_var.set(None)
    user_id_var.set(None)


__all__ = ["get_logger", "set_request_id", "set_user_id", "clear_context"]
