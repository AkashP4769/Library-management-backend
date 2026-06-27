from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from exceptions import (
    AppException,
    NotFoundException,
    ConflictException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    DBException 
)


_STATUS_MAP: dict[type[AppException], int] = {
    NotFoundException: status.HTTP_404_NOT_FOUND,
    ConflictException: status.HTTP_409_CONFLICT,
    BadRequestException: status.HTTP_400_BAD_REQUEST,
    UnauthorizedException: status.HTTP_401_UNAUTHORIZED,
    ForbiddenException: status.HTTP_403_FORBIDDEN,
    DBException: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def value_error_handler(request: Request, exc: AppException):
        code = _STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(status_code=code, content={"detail": str(exc)})
