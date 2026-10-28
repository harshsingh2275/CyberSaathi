"""
CyberSaathi AI — FastAPI application entry point.

Security invariants (enforced here and in every route):
  - Submitted URLs are never opened, fetched, resolved, or previewed.
  - Raw user input (URLs, messages) is never stored or logged by default.
  - CORS is restricted to the origins listed in the CORS_ORIGINS environment variable.
  - Input sizes are enforced at the schema and route layers.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router
from app.config import get_settings


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
