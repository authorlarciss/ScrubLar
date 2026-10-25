"""FastAPI application for ScrubLar.

Endpoints:
- GET  /        — single-page UI (upload form + preview + download).
- POST /mask    — upload file, return JSON with masked_text and entities.
- GET  /health  — health check.

The app is built via `make_app(scrub_service)`. Gamma does not build
services; psi/bootstrap does. See ADR-0011.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from nu.gamma._internal.templates import INDEX_HTML
from nu.gamma.public.interfaces import IScrubService
from nu.psi.contracts.alpha import (
    ParsingError,
    ScrubLarError,
    UnsupportedFormatError,
)

__all__ = ["make_app"]

_MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def make_app(scrub_service: IScrubService) -> FastAPI:
    app = FastAPI(title="ScrubLar", version="0.1.0")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return INDEX_HTML

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/mask")
    async def mask_endpoint(
        file: Annotated[UploadFile, File()],
    ) -> JSONResponse:
        data = await file.read()
        if len(data) > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"file too large (max {_MAX_UPLOAD_BYTES} bytes)",
            )
        if not data:
            raise HTTPException(status_code=400, detail="empty file")
        filename = file.filename or "document.txt"
        try:
            result = scrub_service.scrub(filename, data)
        except UnsupportedFormatError as exc:
            raise HTTPException(status_code=415, detail=str(exc)) from exc
        except ParsingError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ScrubLarError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return JSONResponse(
            {
                "original_filename": result.original_filename,
                "original_extension": result.original_extension,
                "original_text": result.original_text,
                "masked_text": result.masked_text,
                "text_length": result.report.text_length,
                "entities": [
                    {
                        "kind": e.kind.value,
                        "value": e.value,
                        "start": e.start,
                        "end": e.end,
                    }
                    for e in result.report.entities
                ],
            }
        )

    return app
