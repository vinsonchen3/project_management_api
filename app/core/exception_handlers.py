from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import APIException


async def api_exception_handler(
    request: Request,
    exc: APIException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
        },
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(
        APIException,
        api_exception_handler,
    )