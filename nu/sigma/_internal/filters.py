"""Фильтр для добавления контекстных полей в записи лога."""

import logging

from nu.sigma.public.context import request_id_var, user_id_var


class ContextFilter(logging.Filter):
    """Добавляет request_id и user_id в запись, если они установлены."""

    def filter(self, record: logging.LogRecord) -> bool:
        request_id = request_id_var.get()
        user_id = user_id_var.get()

        if request_id is not None:
            record.request_id = request_id
        if user_id is not None:
            record.user_id = user_id

        return True


__all__ = ["ContextFilter"]
