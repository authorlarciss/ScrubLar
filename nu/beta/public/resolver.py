"""Публичный резолвер модуля beta.

Используется psi.bootstrap для создания исполнителей из статических
параметров. Не импортирует _internal/ напрямую (кроме как для
создания экземпляров внутри своих методов).
"""

from typing import Any

from nu.beta.public.interfaces import IWorkflow


class BetaResolver:
    """Фабрика исполнителей модуля beta.

    В конкретном проекте расширяется: make_compiler(), make_executor() и т.д.
    """

    def __init__(self) -> None:
        # Статические параметры (конфиг) при необходимости.
        # Пока пусто — в реальном проекте здесь будет BetaConfig.
        pass

    # noinspection PyMethodMayBeStatic
    def make_workflow(self, **kwargs: Any) -> IWorkflow:
        """Создать workflow. kwargs пробрасываются в реализацию.

        Resolver — единственное место в beta, которому разрешён
        доступ к _internal/ (см. ADR-0002).
        """
        # noinspection PyProtectedMember
        from nu.beta._internal.workflow import PipelineWorkflow

        return PipelineWorkflow(**kwargs)


__all__ = ["BetaResolver"]
