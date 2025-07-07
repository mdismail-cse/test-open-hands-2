from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="API Sentinel",
    description="Intelligent API Security & Usage Monitor",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from api.ingest import router as ingest_router
from api.projects import router as projects_router
from api.anomalies import router as anomalies_router
from api.docs import router as docs_router
from api.auth import router as auth_router

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ingest_router, prefix="/api/ingest", tags=["Data Ingestion"])
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(anomalies_router, prefix="/api/anomalies", tags=["Anomalies"])
app.include_router(docs_router, prefix="/api/docs", tags=["API Documentation"])

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "API Sentinel"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)