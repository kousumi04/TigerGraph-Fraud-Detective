# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import router as rest_router
from .api.streaming import router as ws_router
from .config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="Agentic Fraud Investigation API",
        description="Backend for the TigerGraph × Hacker House Goa 2026 solution.",
        version="1.0.0"
    )

    # Allow Next.js frontend to communicate with this API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(rest_router, prefix="/api")
    app.include_router(ws_router, prefix="/api")

    return app

app = create_app()