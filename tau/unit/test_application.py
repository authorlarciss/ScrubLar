"""Тесты базового Application и IApplication."""

from nu.psi.application import Application
from nu.psi.bootstrap import build_application
from nu.psi.context import Context
from nu.psi.interfaces import IApplication


def test_application_implements_interface() -> None:
    """Application реализует IApplication."""
    app = build_application()
    assert isinstance(app, IApplication)


async def test_application_run() -> None:
    """Application.run — async, выполняется без ошибок."""
    app = build_application()
    await app.run()  # не должно бросать


async def test_custom_application_override() -> None:
    """Наследование Application с переопределением run()."""
    called = False

    class MyApp(Application):
        async def run(self) -> None:
            nonlocal called
            called = True

    ctx = Context()
    app = MyApp(ctx)
    await app.run()
    assert called is True


def test_bootstrap_registers_beta_resolver() -> None:
    """bootstrap регистрирует BetaResolver в контексте."""
    from nu.psi.contracts.beta import BetaResolver

    app = build_application()
    resolver = app.context.resolve("beta_resolver")
    assert isinstance(resolver, BetaResolver)
