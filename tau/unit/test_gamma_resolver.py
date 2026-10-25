"""Tests for GammaResolver factory."""

from fastapi import FastAPI

from nu.beta.public import BetaResolver
from nu.delta.public import DeltaResolver
from nu.epsilon.public import EpsilonResolver
from nu.gamma.public import GammaResolver
from nu.psi.scrub_service import ScrubService


def test_make_app_returns_fastapi() -> None:
    name_detector = EpsilonResolver().make_name_detector()
    detector = BetaResolver().make_detector(name_detector)
    masker = BetaResolver().make_masker()
    service = ScrubService(
        delta_resolver=DeltaResolver(),
        detector=detector,
        masker=masker,
    )
    app = GammaResolver().make_app(service)
    assert isinstance(app, FastAPI)
