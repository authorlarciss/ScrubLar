"""Bootstrap: build the ScrubLar application."""

from __future__ import annotations

from nu.psi.application import Application
from nu.psi.context import Context

__all__ = ["build_application"]


def build_application() -> Application:
    from nu.beta.public import BetaResolver
    from nu.epsilon.public import EpsilonResolver
    from nu.sigma.public import LoggingConfig, SigmaResolver

    context = Context()

    sigma_resolver = SigmaResolver()
    sigma_resolver.setup_logging(LoggingConfig(level="INFO", format="text"))
    context.register("sigma_resolver", sigma_resolver)

    epsilon_resolver = EpsilonResolver()
    context.register("epsilon_resolver", epsilon_resolver)

    beta_resolver = BetaResolver()
    context.register("beta_resolver", beta_resolver)

    name_detector = epsilon_resolver.make_name_detector()
    detector = beta_resolver.make_detector(name_detector)
    context.register("detector", detector)

    masker = beta_resolver.make_masker()
    context.register("masker", masker)

    return Application(context)
