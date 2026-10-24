"""Форматтеры логов: text (dev) и json (prod)."""

import json
import logging
from datetime import UTC, datetime


class TextFormatter(logging.Formatter):
    """Человекочитаемый формат.

    Пример:
        2026-10-21 12:34:56,789 | INFO     | nu.beta.compiler | Compiling...
        (с контекстом) 2026-10-21 12:34:56,789 | INFO     | nu.beta.compiler | [req=abc user=42] Compiling...
    """

    def __init__(self, include_context: bool = True) -> None:
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.include_context = include_context

    def format(self, record: logging.LogRecord) -> str:
        if self.include_context:
            parts = []
            request_id = getattr(record, "request_id", None)
            user_id = getattr(record, "user_id", None)
            if request_id is not None:
                parts.append(f"req={request_id}")
            if user_id is not None:
                parts.append(f"user={user_id}")
            if parts:
                record.msg = f"[{' '.join(parts)}] {record.msg}"

        return super().format(record)


class JsonFormatter(logging.Formatter):
    """JSON-формат для production.

    Пример:
        {"ts": "2026-10-21T12:34:56.789Z", "level": "INFO",
         "logger": "nu.beta.compiler", "message": "Compiling...",
         "request_id": "abc", "user_id": 42}
    """

    def __init__(self, include_context: bool = True) -> None:
        super().__init__()
        self.include_context = include_context

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if self.include_context:
            request_id = getattr(record, "request_id", None)
            user_id = getattr(record, "user_id", None)
            if request_id is not None:
                payload["request_id"] = request_id
            if user_id is not None:
                payload["user_id"] = user_id

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


__all__ = ["TextFormatter", "JsonFormatter"]
