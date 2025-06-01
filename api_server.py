"""
API Server for Audris (formerly DORA Assessment Agent).

This module starts the FastAPI server for Audris API integration
with the SyntechAI ecosystem.
"""
import uvicorn
import logging
import os
from app.api.api import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("audris_api_server")

# API server configuration
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", 8000))

if __name__ == "__main__":
    logger.info(f"Starting Audris API server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "app.api.api:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )