"""Конфигурация логирования."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class LoggingConfig:
    """Настройки логирования.

    level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL".
    format: "text" для разработки, "json" для production.
    include_context: добавлять ли request_id / user_id в записи.
    stream: куда писать — stdout или stderr.
    """

    level: str = "INFO"
    format: Literal["text", "json"] = "text"
    include_context: bool = True
    stream: Literal["stdout", "stderr"] = "stderr"


__all__ = ["LoggingConfig"]
