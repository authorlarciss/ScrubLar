"""Тесты Application, ScrubLarApplication и bootstrap."""

from fastapi import FastAPI

from nu.psi.application import Application, ScrubLarApplication
from nu.psi.bootstrap import build_application
from nu.psi.context import Context
from nu.psi.contracts.gamma import GammaResolver, IScrubService
from nu.psi.interfaces import IApplication


def test_scrublar_application_implements_interface() -> None:
    """ScrubLarApplication реализует IApplication."""
    app = build_application()
    assert isinstance(app, IApplication)
    assert isinstance(app, ScrubLarApplication)


async def test_base_application_run_does_not_hang() -> None:
    """Базовый Application.run() — заглушка, не запускает uvicorn."""
    app = Application(Context())
    await app.run()  # печатает версию, не блокирует


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


def test_scrublar_application_builds_fastapi() -> None:
    """ScrubLarApplication exposes FastAPI app via gamma_resolver.

    Does not call run() — that would launch uvicorn and block.
    HTTP behavior is tested in test_gamma_api.py with TestClient.
    """
    app = build_application()
    resolver: GammaResolver = app.context.resolve("gamma_resolver")
    service: IScrubService = app.context.resolve("scrub_service")
    fastapi_app = resolver.make_app(service)
    assert isinstance(fastapi_app, FastAPI)


def test_bootstrap_registers_beta_resolver() -> None:
    """bootstrap регистрирует BetaResolver в контексте."""
    from nu.psi.contracts.beta import BetaResolver

    app = build_application()
    resolver = app.context.resolve("beta_resolver")
    assert isinstance(resolver, BetaResolver)
