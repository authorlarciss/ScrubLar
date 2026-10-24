"""Интерфейсы модуля beta: процессоры, workflow, event bus.

Все интерфейсы async — future-proof. Синхронная реализация просто
не содержит await.
"""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from nu.psi.contracts.alpha import IEvent


class IProcessor(ABC):
    """Один шаг обработки.

    Может быть sync или async внутри. Интерфейс async, чтобы не
    переписывать при появлении async-шагов.
    """

    @abstractmethod
    async def process(self, data: Any) -> Any: ...


class IWorkflow(ABC):
    """Оркестрирует последовательность процессоров.

    Единый обработчик для проектов, где взаимодействия статичны.
    Для динамических взаимодействий — IEventBus.
    """

    @abstractmethod
    async def run(self, stages: Sequence[IProcessor]) -> None: ...

    @abstractmethod
    def get_result(self) -> Any:
        """Результат после выполнения всех процессоров."""


class IEventBus(ABC):
    """Асинхронная шина событий.

    Использовать только если:
    - у события несколько обработчиков, И
    - обработчики могут меняться в рантайме.

    Во всех остальных случаях — direct call или workflow.
    Реализация — в конкретном проекте, не в BaseLar core.
    """

    @abstractmethod
    async def publish(self, event: IEvent) -> None: ...

    @abstractmethod
    def subscribe(
        self,
        event_type: type[IEvent],
        handler: Callable[[IEvent], Awaitable[None]],
    ) -> None: ...


__all__ = ["IProcessor", "IWorkflow", "IEventBus"]
