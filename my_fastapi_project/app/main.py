"""
FastAPI application entry point.

- Registers all routers
- Serves the dashboard HTML
- Prints startup banner
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import items, users
from app.core.config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI instance."""

    application = FastAPI(
        title="🚦 AI Traffic Monitoring System",
        description="CCTV Vehicle Monitoring API — powered by FastAPI & SQLAlchemy",
        version="1.0.0",
    )

    # --- CORS (izinkan semua origin untuk development) ---
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routers ---
    application.include_router(items.router)
    application.include_router(users.router)

    # --- Dashboard ---
    @application.get("/", tags=["Dashboard"])
    def dashboard():
        """Serve the dashboard HTML page."""
        return FileResponse("dashboard.html")

    return application


# Create the app instance used by uvicorn
app = create_app()


# ============================================================
# Run with: uvicorn app.main:app --reload
# Or:       python -m app.main
# ============================================================

if __name__ == "__main__":
    import uvicorn

    print("\n===================================")
    print("🚦 AI TRAFFIC MONITORING SYSTEM")
    print("===================================")
    print(f"Dashboard:      http://{settings.APP_HOST}:{settings.APP_PORT}")
    print(f"Swagger Docs:   http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    print(f"API Vehicles:   http://{settings.APP_HOST}:{settings.APP_PORT}/vehicles")
    print("===================================\n")

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )
