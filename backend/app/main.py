from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.telemetry import setup_opentelemetry
from app.api import health, websocket_scribe, ledger_routes, billing_routes

def create_app() -> FastAPI:
    app = FastAPI(
        title="Doctors Copilot Enterprise API",
        description="Production-grade, HIPAA-compliant ambient clinical documentation and revenue cycle platform.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS for Next.js frontend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict to exact frontend domain in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize OpenTelemetry distributed tracing and Azure Application Insights export
    setup_opentelemetry(app)

    # Register API Routers
    app.include_router(health.router, prefix="/health", tags=["Health & Status"])
    app.include_router(websocket_scribe.router, prefix="/v1", tags=["Audio Ingestion & Scribe"])
    app.include_router(ledger_routes.router, prefix="/v1/ledger", tags=["Cosmos Ledger & FHIR R4"])
    app.include_router(billing_routes.router, prefix="/v1/billing", tags=["Revenue Cycle & CMS-1500/837P"])

    return app

app = create_app()

@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "online",
        "service": "Doctors Copilot Enterprise Backend",
        "version": "1.0.0",
        "docs": "/docs"
    }
