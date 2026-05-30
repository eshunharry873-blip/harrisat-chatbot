from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.logger import logger
import traceback

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

def setup_error_handlers(app: FastAPI):
    app.add_exception_handler(Exception, general_exception_handler)
