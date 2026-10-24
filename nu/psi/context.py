"""Общий контекст приложения — DI-контейнер."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    """Хранит созданные экземпляры модулей и общие данные."""

    registry: dict[str, Any] = field(default_factory=dict)

    def register(self, name: str, instance: Any) -> None:
        """Зарегистрировать экземпляр под именем."""
        self.registry[name] = instance

    def resolve(self, name: str) -> Any:
        """Получить экземпляр по имени. Бросает KeyError, если не зарегистрирован."""
        if name not in self.registry:
            raise KeyError(f"'{name}' не зарегистрирован в Context")
        return self.registry[name]
