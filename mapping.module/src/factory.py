from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import fuxmas_router, include_exception_handlers
from src.common.config import service_config


def app_factory() -> FastAPI:
    app = FastAPI(
        title=service_config.name,
        summary=service_config.description,
        version=service_config.version,
        docs_url="/docs/",
        redoc_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(fuxmas_router)
    include_exception_handlers(app)

    return app
