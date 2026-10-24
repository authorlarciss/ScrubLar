"""Integration test: bootstrap → context → resolver → workflow → result."""

from typing import Any

from nu.psi.bootstrap import build_application
from nu.psi.contracts.beta import BetaResolver, IProcessor


class AddOne(IProcessor):
    async def process(self, data: Any) -> Any:
        return data + 1


class MultiplyByTwo(IProcessor):
    async def process(self, data: Any) -> Any:
        return data * 2


async def test_full_pattern_via_bootstrap() -> None:
    """Полный паттерн: bootstrap → context → resolver → workflow → result.

    Демонстрирует, как проект должен собирать workflow:
    1. build_application() создаёт контекст с зарегистрированным BetaResolver.
    2. Резолвер достаётся из контекста (не создаётся напрямую).
    3. Резолвер создаёт IWorkflow (реализация — PipelineWorkflow, скрыта).
    4. Workflow выполняет процессоры последовательно.
    """
    app = build_application()

    resolver = app.context.resolve("beta_resolver")
    assert isinstance(resolver, BetaResolver)

    workflow = resolver.make_workflow(initial_data=5)
    await workflow.run([AddOne(), MultiplyByTwo()])

    # (5 + 1) * 2 = 12
    assert workflow.get_result() == 12
