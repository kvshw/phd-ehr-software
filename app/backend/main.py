"""
EHR Research Platform - Backend API
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routes import (
    auth, patients, vitals, labs, imaging, ai, monitor, mape_k, audit, admin,
    clinical_notes, problems, medications, allergies, conversations, feedback, visits,
    research
)

app = FastAPI(
    title="EHR Research Platform API",
    description="Self-Adaptive AI-Assisted EHR Research Platform Backend",
    version="0.1.0"
)

# CORS middleware - Allow all origins in development
import os
cors_origins = settings.CORS_ORIGINS
if os.getenv("ENVIRONMENT", "development") == "development":
    # In development, allow all origins to avoid CORS issues
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,  # Important for cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(patients.router, prefix=settings.API_V1_PREFIX)
app.include_router(vitals.router, prefix=settings.API_V1_PREFIX)
app.include_router(labs.router, prefix=settings.API_V1_PREFIX)
app.include_router(imaging.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai.router, prefix=settings.API_V1_PREFIX)
app.include_router(monitor.router, prefix=settings.API_V1_PREFIX)
app.include_router(mape_k.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(clinical_notes.router, prefix=settings.API_V1_PREFIX)
app.include_router(problems.router, prefix=settings.API_V1_PREFIX)
app.include_router(medications.router, prefix=settings.API_V1_PREFIX)
app.include_router(allergies.router, prefix=settings.API_V1_PREFIX)
app.include_router(conversations.router, prefix=settings.API_V1_PREFIX)
app.include_router(feedback.router, prefix=settings.API_V1_PREFIX)
app.include_router(visits.router, prefix=settings.API_V1_PREFIX)
app.include_router(research.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "EHR Research Platform API",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

