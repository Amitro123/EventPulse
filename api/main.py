"""EventPulse API - Event Discovery Platform."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import events_router
from api.models.event import HealthResponse
from api import config
import os

app = FastAPI(
    title="EventPulse API",
    description="Event discovery platform for concerts and sports with affiliate monetization",
    version=config.API_VERSION
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS if config.CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(events_router)


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="ok", version=config.API_VERSION)


@app.get("/")
async def root():
    """Root endpoint - serve frontend or API info."""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "src", "ui", "frontend", "build", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {
        "message": "EventPulse API",
        "version": config.API_VERSION,
        "docs": "/docs",
        "events": "/api/events?date=2025-12-15&city=Tel%20Aviv"
    }


# Serve static frontend files in production
frontend_build = os.path.join(os.path.dirname(__file__), "..", "src", "ui", "frontend", "build")
if os.path.exists(frontend_build):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_build, "static")), name="static")
