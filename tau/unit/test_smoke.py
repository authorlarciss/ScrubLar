"""Smoke-тесты: проверяют, что базовые точки входа проекта работают."""

import nu
from nu.psi import Application, Context
from nu.psi.bootstrap import build_application


def test_nu_importable() -> None:
    """Пакет nu должен импортироваться без ошибок."""
    assert nu is not None


def test_version_available() -> None:
    """Версия должна быть доступна через публичный API."""
    assert isinstance(nu.__version__, str)
    assert nu.__version__  # не пустая


def test_application_constructible() -> None:
    """Application должен собираться через bootstrap."""
    app = build_application()
    assert isinstance(app, Application)


def test_context_register_and_resolve() -> None:
    """Context должен регистрировать и возвращать экземпляры."""
    ctx = Context()
    sentinel = object()
    ctx.register("test", sentinel)
    assert ctx.resolve("test") is sentinel


def test_context_raises_on_unknown() -> None:
    """Context должен бросать KeyError для незарегистрированного имени."""
    import pytest

    ctx = Context()
    with pytest.raises(KeyError):
        ctx.resolve("unknown")
