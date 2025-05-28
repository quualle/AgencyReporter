from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv
from .routes import agencies, quotas, reaction_times, profile_quality, quotas_with_reasons, problematic_stays, cache, care_stays
from .dependencies import get_settings
from .utils.database_connection import initialize_database

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agency Reporter API",
    description="API for the Agency Reporter Dashboard with Database-backed Caching",
    version="0.2.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables on startup."""
    try:
        logger.info("Initializing database...")
        db_manager = initialize_database()
        logger.info("Database initialized successfully")
        
        # Test database connection
        connection_ok = await db_manager.test_connection()
        if connection_ok:
            logger.info("Database connection test successful")
        else:
            logger.error("Database connection test failed")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown."""
    try:
        from .utils.database_connection import get_database_manager
        db_manager = get_database_manager()
        db_manager.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Include routers
app.include_router(agencies.router, prefix="/api/agencies", tags=["agencies"])
app.include_router(quotas.router, prefix="/api/quotas", tags=["quotas"])
app.include_router(quotas_with_reasons.router, prefix="/api/quotas_with_reasons", tags=["quotas with reasons"])
app.include_router(reaction_times.router, prefix="/api/reaction_times", tags=["reaction times"])
app.include_router(profile_quality.router, prefix="/api/profile_quality", tags=["profile quality"])
app.include_router(problematic_stays.router, prefix="/api/problematic_stays", tags=["problematic stays"])
app.include_router(care_stays.router, prefix="/api/care_stays", tags=["care stays"])
app.include_router(cache.router, prefix="/api/cache", tags=["cache management"])

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