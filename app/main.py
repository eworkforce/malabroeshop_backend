from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MALABRO eShop API",
    description="API for MALABRO online grocery store with AI Assistant MCP Server",
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Initialize MCP Server for AI Assistant
try:
    from fastapi_mcp import FastApiMCP
    
    # Create MCP server based on our FastAPI app
    mcp = FastApiMCP(app)
    
    # Mount the MCP server at /mcp endpoint
    mcp.mount_http()
    
    print("✅ MCP Server initialized successfully at /mcp")
    
except ImportError:
    print("⚠️  FastAPI-MCP not installed. AI Assistant features disabled.")
    print("   Run: pip install fastapi-mcp")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to MALABRO eShop API", 
        "features": ["REST API", "AI Assistant MCP Server"],
        "mcp_endpoint": "/mcp"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "mcp_enabled": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
app.include_router(api_router, prefix=settings.API_V1_STR)
