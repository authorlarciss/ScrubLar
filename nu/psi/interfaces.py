"""Интерфейсы композиционного корня.

Psi остаётся плоским (без public/_internal), но интерфейсы живут
отдельно от реализации — для чистоты.
"""

from abc import ABC, abstractmethod


class IApplication(ABC):
    """Единая точка входа проекта.

    Реализация — в psi/application.py (базовая) или в конкретном
    проекте (наследование с переопределением run()).

    async def run() — future-proof. Проект может быть полностью
    синхронным: async def run() без await внутри — валидно.
    """

    @abstractmethod
    async def run(self) -> None: ...


__all__ = ["IApplication"]
