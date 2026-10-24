"""Интерфейсы логирования."""

from abc import ABC, abstractmethod

from nu.sigma.public.config import LoggingConfig


class ILoggingSetup(ABC):
    """Настройка логирования."""

    @abstractmethod
    def setup(self, config: LoggingConfig) -> None: ...


__all__ = ["ILoggingSetup"]
