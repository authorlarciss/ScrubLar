"""Публичный резолвер модуля sigma."""

from nu.sigma.public.config import LoggingConfig
from nu.sigma.public.interfaces import ILoggingSetup


class SigmaResolver:
    """Фабрика для настройки логирования.

    Используется psi.bootstrap. Инициализирует логирование первым —
    до всех остальных модулей, чтобы ранние логи не терялись.
    """

    def __init__(self) -> None:
        self._setup: ILoggingSetup | None = None

    def setup_logging(self, config: LoggingConfig) -> None:
        """Настроить корневой логгер "nu"."""
        # noinspection PyProtectedMember
        from nu.sigma._internal.setup import LoggingSetup

        setup = LoggingSetup()
        setup.setup(config)
        self._setup = setup


__all__ = ["SigmaResolver"]
