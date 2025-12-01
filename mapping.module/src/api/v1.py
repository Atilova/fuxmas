from pathlib import Path
from uuid import UUID
from functools import cached_property

from fastapi import (
    Form,
    File,
    UploadFile,
    Depends,
    FastAPI,
    Request,
)
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from starlette import status

from src.mapping import MappingApp, get_mapping_app
from src.mapping import dto as mapping_dto
from src.mapping.enums import Strategy as MappingStrategy
from src.mapping.exceptions import MappingException
from pkg.snake_case import from_pascal_to_snake_case


router = APIRouter(
    prefix='/v1',
    tags=["Mapping"],
)


def include_exception_handlers(app: FastAPI):
    app.add_exception_handler(MappingException, _handle_mapping_exception)


async def _handle_mapping_exception(request: Request, exc: MappingException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": [
                {
                    "type": from_pascal_to_snake_case(type(exc).__name__),
                    "loc": "non_fields_error",
                    "msg": str(exc),
                },
            ],
        },
    )


class MappingFileAdapter:
    def __init__(self, file: UploadFile):
        self._file = file

    async def read(self, chunk_size: int):
        return await self._file.read(chunk_size)

    async def seek(self, offset: int):
        return await self._file.seek(offset)

    @cached_property
    def name(self):
        return Path(self._file.filename).with_suffix("").name

    @property
    def size(self):
        return self._file.size

    @cached_property
    def extension(self):
        return Path(self._file.filename).suffix


@router.get("/mapping/file/{file_id}/")
async def mapping_file(
    file_id: UUID,
    mapping_app: MappingApp = Depends(get_mapping_app),
) -> FileResponse:
    file_path = await mapping_app.expose_file_port.get_path(file_id)
    filesystem_path = mapping_app.storage.get_local_filesystem_path(file_path)

    return FileResponse(filesystem_path)


@router.post("/mapping/strategy/init/")
async def mapping_strategy_init(
    file: UploadFile = File(...),
    total_pixels: int = Form(...),
    strategy: MappingStrategy = Form(...),
    mapping_app: MappingApp = Depends(get_mapping_app),
) -> mapping_dto.StrategyInitResult:
    request = mapping_dto.StrategyInit(
        total_pixels=total_pixels,
        strategy=strategy,
        file=MappingFileAdapter(file)
    )

    return await mapping_app.strategy_port.init(request)


@router.post("/mapping/strategy/read/")
async def mapping_strategy_result(
    request: mapping_dto.StrategyRead,
    mapping_app: MappingApp = Depends(get_mapping_app),
) -> mapping_dto.StrategyReadResult:
    return await mapping_app.strategy_port.read(request)


@router.post("/mapping/strategy/grayLabel/try/")
async def mapping_strategy_gray_label_try(
    request: mapping_dto.StrategyGrayLabelTry,
    mapping_app: MappingApp = Depends(get_mapping_app),
) -> mapping_dto.StrategyGrayLabelTryResult:
    return await mapping_app.gray_label_strategy_port.try_analyze(request)


@router.post("/mapping/strategy/grayLabel/continue/")
async def mapping_strategy_gray_label_continue(
    request: mapping_dto.StrategyGrayLabelContinue,
    mapping_app: MappingApp = Depends(get_mapping_app),
) -> mapping_dto.StrategyGrayLabelContinueResult:
    return await mapping_app.gray_label_strategy_port.continue_analyze(request)
