"""Template tests for psi.bootstrap.

SPECIFIC TO THE BASE TEMPLATE's build_application(). When
build_application() is rewritten for your domain, either delete this
file or update the tests to match your bootstrap.

Marker: `template`. Skip with `pytest -m "not template"` while
refactoring.
"""

import logging

import pytest

from nu.psi.bootstrap import build_application

pytestmark = pytest.mark.template


def test_bootstrap_configures_logging() -> None:
    """bootstrap инициализирует логирование первым."""
    app = build_application()

    nu_logger = logging.getLogger("nu")
    assert len(nu_logger.handlers) >= 1

    # SigmaResolver зарегистрирован в контексте
    sigma_resolver = app.context.resolve("sigma_resolver")
    from nu.psi.contracts.sigma import SigmaResolver

    assert isinstance(sigma_resolver, SigmaResolver)


def test_bootstrap_registers_beta_resolver() -> None:
    """bootstrap регистрирует BetaResolver (из Phase 3a)."""
    from nu.psi.contracts.beta import BetaResolver

    app = build_application()
    resolver = app.context.resolve("beta_resolver")
    assert isinstance(resolver, BetaResolver)
