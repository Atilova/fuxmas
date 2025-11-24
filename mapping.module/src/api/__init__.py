from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.api.v1 import (
    router as v1_router,
    include_exception_handlers as v1_include_exception_handlers,
)


fuxmas_router = APIRouter(prefix="/fuxmas")
fuxmas_router.include_router(v1_router)


def include_exception_handlers(app: FastAPI):
    v1_include_exception_handlers(app)


__all__ = (
    "fuxmas_router",
    "include_exception_handlers",
)
