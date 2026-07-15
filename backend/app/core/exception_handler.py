from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.domain.exceptions.base_exception import BusinessException

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(BusinessException)
    async def business_exception_handler(
        request: Request, 
        exc: BusinessException
        ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message},
        )