"""Простая реализация IWorkflow: последовательное выполнение.

Пример. Проекты могут делать свои реализации.
"""

from collections.abc import Sequence
from typing import Any

from nu.psi.contracts.beta import IProcessor, IWorkflow


class PipelineWorkflow(IWorkflow):
    """Последовательно выполняет процессоры. Fail-fast при ошибке.

    Данные текут через процессоры: initial_data → processor1 →
    processor2 → ... → final_result.

    Если процессор бросает исключение — пайплайн останавливается,
    исключение пробрасывается наружу. Проекты, которым нужно
    «продолжить при ошибке», наследуют и переопределяют run().
    """

    def __init__(self, initial_data: Any = None) -> None:
        self._data = initial_data

    async def run(self, stages: Sequence[IProcessor]) -> None:
        data = self._data
        for stage in stages:
            data = await stage.process(data)
        self._data = data

    def get_result(self) -> Any:
        """Результат после последнего процессора."""
        return self._data


__all__ = ["PipelineWorkflow"]
