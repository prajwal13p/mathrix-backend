from pydoc import text
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
import time
import os
from app.routers import auth, participants, teams, team_formation, admin
from app.core.database import create_missing_tables, migrate_existing_tables

app = FastAPI(
    title="Mathrix API",
    description="AI-Powered Team Formation Platform API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEBUG", "false").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "false").lower() == "true" else None
)

# Production security middleware
if os.getenv("DEBUG", "false").lower() != "true":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]  # Configure this based on your domain
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://mathrix-frontend.onrender.com",
        "https://*.onrender.com",
        "https://*.vercel.app",
        "https://*.netlify.app",
        "*"  # Allow all origins for now (you can restrict this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# Database health check endpoint
@app.get("/health/db")
async def database_health_check():
    try:
        from app.core.database import get_db
        db = next(get_db())
        # Try a simple query
        result = db.execute(text("SELECT 1"))
        result.scalar()
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# Manual migration trigger endpoint
@app.post("/admin/migrate-db")
async def trigger_migration():
    try:
        from app.core.database import migrate_existing_tables
        migrate_existing_tables()
        return {
            "status": "success",
            "message": "Database migration completed",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Migration failed: {str(e)}",
            "timestamp": time.time()
        }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Mathrix API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(participants.router, prefix="/api/participants", tags=["Participants"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(team_formation.router, prefix="/api/team-formation", tags=["Team Formation"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Mathrix API...")
    try:
        create_missing_tables()
        migrate_existing_tables()
        print("✅ Database tables initialized successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Database initialization failed: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down Mathrix API...")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": time.time(),
            "path": str(request.url)
        }
    )
