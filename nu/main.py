"""Точка входа текущей версии проекта."""

import asyncio

from nu.psi.bootstrap import build_application


def main() -> None:
    """Запуск проекта."""
    app = build_application()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
