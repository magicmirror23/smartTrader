# Entry point for FastAPI application

"""StockTrader Backend – FastAPI application."""

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.routers import health, predict, model, backtest, trade, admin, paper, stream, market

app = FastAPI(
    title="StockTrader API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – restrict origins in production via ALLOWED_ORIGINS env var
_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Routers -----
app.include_router(health.router, prefix="/api/v1")
app.include_router(predict.router, prefix="/api/v1")
app.include_router(model.router, prefix="/api/v1")
app.include_router(backtest.router, prefix="/api/v1")
app.include_router(trade.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(paper.router, prefix="/api/v1")
app.include_router(stream.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")


# ----- Serve Angular frontend (production builds) -----
_STATIC_DIR = Path(__file__).resolve().parents[2] / "static"

if _STATIC_DIR.is_dir():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=_STATIC_DIR / "assets"), name="assets") \
        if (_STATIC_DIR / "assets").is_dir() else None
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static-root")

    @app.get("/{full_path:path}")
    async def serve_angular(full_path: str):
        """Catch-all: serve Angular index.html for client-side routing."""
        file_path = _STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_STATIC_DIR / "index.html")
