from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.users import router as user_router
import logging
import time
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
import signal
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB client initialization (ensure MongoDB is running)
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.mydatabase  # Adjust with your database name

app = FastAPI(
    title="User Management API",
    description="A FastAPI-based user management microservice",
    version="1.0.0"
)

# Basic CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Log requests and responses
@app.middleware("http")
async def log_request(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {request.headers}")
    body = await request.body()
    if body:
        logger.info(f"Body: {body.decode()}")

    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": app.version
    }

@app.get("/")
def read_root():
    return {
        "message": "FastAPI User Management Microservice",
        "docs_url": "/docs"
    }

# Include routers
app.include_router(user_router, prefix="/api")

# Handle HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail} - {request.method} {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

# Handle validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()} - {request.method} {request.url}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "status_code": 422}
    )

# General exception handler (catch unexpected errors)
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)} - {request.method} {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "status_code": 500}
    )

# MongoDB client shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Graceful shutdown on termination signal
def graceful_shutdown(signum, frame):
    logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)
