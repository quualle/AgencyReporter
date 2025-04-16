from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from .routes import agencies, quotas, reaction_times, profile_quality, quotas_with_reasons
from .dependencies import get_settings

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Agency Reporter API",
    description="API for the Agency Reporter Dashboard",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agencies.router, prefix="/api/agencies", tags=["agencies"])
app.include_router(quotas.router, prefix="/api/quotas", tags=["quotas"])
app.include_router(quotas_with_reasons.router, prefix="/api/quotas_with_reasons", tags=["quotas with reasons"])
app.include_router(reaction_times.router, prefix="/api/reaction_times", tags=["reaction times"])
app.include_router(profile_quality.router, prefix="/api/profile_quality", tags=["profile quality"])

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "ok", "message": "API is running"}

@app.get("/")
async def root():
    """
    Root endpoint redirecting to API documentation
    """
    return {"message": "Welcome to Agency Reporter API. Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run("app.main:app", host=host, port=port, reload=True) 