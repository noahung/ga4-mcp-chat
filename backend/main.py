from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import logging
from mcp_client import query_ga

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("ga4-mcp-chat")

# Define request model
class QueryRequest(BaseModel):
    password: str
    message: str

app = FastAPI(
    title="GA4 MCP Chat API",
    description="API for querying Google Analytics 4 data using natural language",
    version="1.0.0"
)

# Configure CORS
origins = [
    "https://noahung.github.io",
    "https://noahung.github.io/ga4-mcp-chat/"
]

# Add localhost for development
if os.environ.get("ENVIRONMENT") == "development":
    origins.append("http://localhost:3000")
    origins.append("http://127.0.0.1:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)

# Get password from environment variable
CHAT_PASSWORD = os.environ.get("CHAT_PASSWORD", "changeme")

# Warn if using default password
if CHAT_PASSWORD == "changeme":
    logger.warning("Using default password! Set CHAT_PASSWORD environment variable in production.")

# Authentication dependency
def verify_password(request: QueryRequest):
    if request.password != CHAT_PASSWORD:
        logger.warning("Invalid password attempt")
        raise HTTPException(status_code=401, detail="Access denied")
    return True

@app.post("/query")
async def query_endpoint(request: QueryRequest, authenticated: bool = Depends(verify_password)):
    try:
        logger.info(f"Processing query: {request.message[:50]}...")
        reply = query_ga(request.message)
        return {"reply": reply}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"reply": f"Error processing your query: {str(e)}"})

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Add startup event
@app.on_event("startup")
async def startup_event():
    logger.info("GA4 MCP Chat API starting up")
    # Check if MCP server is installed
    try:
        test_query = query_ga("test")
        logger.info("MCP server connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {str(e)}")
        logger.error("Make sure google-analytics-mcp is installed and configured correctly")

# Add shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("GA4 MCP Chat API shutting down")
