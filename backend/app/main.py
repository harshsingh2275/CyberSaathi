"""
CyberSaathi AI — FastAPI application entry point.

Security invariants (enforced here and in every route):
  - Submitted URLs are never opened, fetched, resolved, or previewed.
  - Raw user input (URLs, messages) is never stored or logged by default.
  - Validation error responses never reflect raw submitted user inputs.
  - CORS is restricted to the origins listed in the CORS_ORIGINS environment variable.
  - Input sizes and types are enforced at the schema and route layers.
  - Stack traces and internal exception details are never exposed to clients.
"""

from __future__ import annotations

import logging
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router
from app.config import get_settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CyberSaathi AI",
        description=(
            "Cybersecurity awareness API for college students and beginner internet users. "
            "Analyzes URL and message strings locally — submitted URLs are never opened."
        ),
        version="0.1.0",
        # Disable automatic redirect from /path to /path/ to avoid CORS issues.
        redirect_slashes=False,
    )

    # ── Security headers middleware ───────────────────────────────────────────
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    # ── Exception handlers (prevent secret / input reflection) ────────────────
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Sanitize validation errors: strip the raw user input to ensure that
        sensitive tokens, credentials, or personal data submitted by users
        are never echoed back in HTTP 422 error payloads.
        """
        cleaned_errors = []
        for err in exc.errors():
            clean_err = {k: v for k, v in err.items() if k != "input"}
            if "ctx" in clean_err and isinstance(clean_err["ctx"], dict):
                clean_err["ctx"] = {
                    k: v for k, v in clean_err["ctx"].items() if k != "input"
                }
            cleaned_errors.append(clean_err)
        return JSONResponse(
            status_code=422,
            content={"detail": jsonable_encoder(cleaned_errors)},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all for unhandled exceptions: return a generic 500 error
        without exposing stack traces or internal variable states.
        """
        logger.error(
            "Unhandled exception processing %s %s: %s",
            request.method,
            request.url.path,
            type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."},
        )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(analysis_router)

    return app


app = create_app()
