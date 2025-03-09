from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from .routers import github, files, analysis
from .core.config import settings
from .core.logger import setup_logging

# Setup logging
logger = logging.getLogger(__name__)
setup_logging()

app = FastAPI(
    title="CodeLens Source Code Service",
    description="Service for retrieving and analyzing source code from various sources",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(github.router, prefix="/github", tags=["GitHub"])
app.include_router(files.router, prefix="/files", tags=["Files"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "source-code-service"}

@app.get("/health/readiness", tags=["Health"])
async def readiness():
    return {"status": "ready"}

@app.get("/health/liveness", tags=["Health"])
async def liveness():
    return {"status": "alive"}

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "CodeLens Source Code Service",
        "version": "0.1.0",
        "description": "Service for retrieving and analyzing source code"
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)