from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from http import HTTPStatus
from datetime import datetime
from app.exceptions.custom_exceptions import InvalidRequestException


app = FastAPI()

@app.exception_handler(InvalidRequestException)
async def invalid_request_exception_handler(request: Request, exc: InvalidRequestException):
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={
            "endpoint": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
            "status": HTTPStatus.BAD_REQUEST.value,
            "statusCode": HTTPStatus.BAD_REQUEST.name,
            "message": exc.detail,
        }
    )

