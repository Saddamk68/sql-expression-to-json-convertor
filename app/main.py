import logging

# from app.main import app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.exceptions.handler.exception_handler import invalid_request_exception_handler
from app.exceptions.custom_exceptions import InvalidRequestException

app = FastAPI(
    title="SQL Expression to JSON Converter",
    description="API for converting SQL expressions to JSON format",
    version="1.0.0"
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler()
    ]
)

# Config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

from app.api import json_convertor

app.include_router(json_convertor.router, prefix="/api", tags=["json-convertor"])

#  Register exception handlers
app.add_exception_handler(InvalidRequestException, invalid_request_exception_handler)


@app.get("/")
async def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the SQL Expression to JSON Converter API!"}

