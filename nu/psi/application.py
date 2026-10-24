"""Базовая реализация IApplication."""

from nu.psi.context import Context
from nu.psi.contracts.mu import __version__ as __version__
from nu.psi.contracts.sigma import get_logger
from nu.psi.interfaces import IApplication

logger = get_logger(__name__)


class Application(IApplication):
    """Базовое приложение с DI-контекстом.

    В BaseLar-шаблоне run() — заглушка. В конкретном проекте —
    наследование и переопределение:

        from nu.psi.application import Application
        from nu.psi.bootstrap import build_application

        class MyApp(Application):
            async def run(self) -> None:
                resolver = self.context.resolve("beta_resolver")
                workflow = resolver.make_workflow(initial_data=...)
                await workflow.run([Processor1(), Processor2()])
                print(f"Result: {workflow.result}")

        app = MyApp(build_application().context)
        asyncio.run(app.run())

    Такой подход гарантирует, что:
    - резолвер получен из контекста (не создан напрямую);
    - реализация workflow скрыта за интерфейсом IWorkflow;
    - конкретные процессоры — в проекте, не в BaseLar.
    """

    def __init__(self, context: Context) -> None:
        self.context = context

    async def run(self) -> None:
        """Запуск проекта. В шаблоне — заглушка."""
        logger.info("Application starting, version=%s", __version__)
        print(f"BaseLar nu v{__version__} — шаблон готов к использованию.")
        logger.info("Application finished")


__all__ = ["Application"]
