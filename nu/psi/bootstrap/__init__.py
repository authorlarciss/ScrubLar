"""Сборка приложения: создание контекста и регистрация модулей."""

from nu.psi.application import Application
from nu.psi.context import Context
from nu.psi.contracts.beta import BetaResolver
from nu.psi.contracts.sigma import LoggingConfig, SigmaResolver


def build_application() -> Application:
    """Создать Application со всеми зарегистрированными модулями."""
    context = Context()

    # 1. Логирование — первым, до всех остальных модулей
    sigma_resolver = SigmaResolver()
    sigma_resolver.setup_logging(LoggingConfig(level="INFO", format="text"))
    context.register("sigma_resolver", sigma_resolver)

    # 2. Остальные модули
    beta_resolver = BetaResolver()
    context.register("beta_resolver", beta_resolver)

    return Application(context)


__all__ = ["build_application"]
