"""Публичные контракты модулей.

Модули импортируют контракты конкретных модулей через подмодули:
`nu.psi.contracts.alpha`, `nu.psi.contracts.beta` и т.д.

Агрегат `Contracts` — удобная точка доступа для инструментов и тестов.
"""

from . import alpha, beta, delta, epsilon, gamma, iota, mu, sigma, zeta


class Contracts:
    """Namespace со ссылками на модули-контракты."""

    alpha = alpha
    beta = beta
    gamma = gamma
    delta = delta
    epsilon = epsilon
    zeta = zeta
    iota = iota
    sigma = sigma
    mu = mu


__all__ = [
    "Contracts",
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "iota",
    "sigma",
    "mu",
]
