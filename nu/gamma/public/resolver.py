"""Public resolver for gamma — factory for the FastAPI app."""

from __future__ import annotations

from fastapi import FastAPI

from nu.gamma.public.interfaces import IScrubService

__all__ = ["GammaResolver"]


class GammaResolver:
    @staticmethod
    def make_app(scrub_service: IScrubService) -> FastAPI:
        # noinspection PyProtectedMember
        from nu.gamma._internal.api import make_app

        return make_app(scrub_service)
