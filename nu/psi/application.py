"""Application entry points."""

from __future__ import annotations

from nu.psi.context import Context
from nu.psi.contracts.mu import __version__ as __version__
from nu.psi.contracts.sigma import get_logger
from nu.psi.interfaces import IApplication

logger = get_logger(__name__)

__all__ = ["Application", "ScrubLarApplication"]


class Application(IApplication):
    """BaseLar base. In ScrubLar, use ScrubLarApplication."""

    def __init__(self, context: Context) -> None:
        self.context = context

    async def run(self) -> None:
        logger.info("Application starting, version=%s", __version__)
        print(f"BaseLar nu v{__version__} — template ready.")
        logger.info("Application finished")


class ScrubLarApplication(Application):
    """Run FastAPI app via uvicorn on asyncio event loop.

    The app is built from `gamma_resolver.make_app(scrub_service)` —
    both are in context. Bootstrap registers `gamma_resolver` and
    `scrub_service`.

    `run()` is not unit-tested: it blocks on uvicorn.Server.serve().
    HTTP behavior is covered in `test_gamma_api.py` via TestClient;
    full serve() is exercised manually with `make run`.
    """

    def __init__(
        self,
        context: Context,
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> None:
        super().__init__(context)
        self._host = host
        self._port = port

    async def run(self) -> None:  # pragma: no cover
        import uvicorn

        from nu.psi.contracts.gamma import GammaResolver, IScrubService

        resolver: GammaResolver = self.context.resolve("gamma_resolver")
        service: IScrubService = self.context.resolve("scrub_service")
        app = resolver.make_app(service)
        config = uvicorn.Config(app, host=self._host, port=self._port, log_level="info")
        server = uvicorn.Server(config)
        logger.info("ScrubLar starting at http://%s:%s", self._host, self._port)
        await server.serve()
