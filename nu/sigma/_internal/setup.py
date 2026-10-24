"""Реализация ILoggingSetup.

Настраивает корневой логгер "nu" — все дочерние логгеры
("nu.beta.compiler" и т.д.) наследуют handlers и level.
"""

import logging
import sys

from nu.sigma._internal.filters import ContextFilter
from nu.sigma._internal.formatters import JsonFormatter, TextFormatter
from nu.sigma.public.config import LoggingConfig
from nu.sigma.public.interfaces import ILoggingSetup


class LoggingSetup(ILoggingSetup):
    """Настройка корневого логгера "nu"."""

    def setup(self, config: LoggingConfig) -> None:
        """Настроить корневой логгер "nu".

        Идемпотентно: повторный вызов заменяет handlers, не дублирует.
        """
        root_nu_logger = logging.getLogger("nu")

        # Идемпотентность: убираем старые handlers, если были
        for handler in list(root_nu_logger.handlers):
            root_nu_logger.removeHandler(handler)

        stream = sys.stderr if config.stream == "stderr" else sys.stdout
        handler = logging.StreamHandler(stream)

        if config.format == "json":
            formatter: logging.Formatter = JsonFormatter(include_context=config.include_context)
        else:
            formatter = TextFormatter(include_context=config.include_context)

        handler.setFormatter(formatter)
        handler.addFilter(ContextFilter())

        root_nu_logger.addHandler(handler)
        root_nu_logger.setLevel(config.level)
        root_nu_logger.propagate = False


__all__ = ["LoggingSetup"]
