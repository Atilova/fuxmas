from src.mapping.enums import FileMIME
from src.mapping.interfaces import IStorage, IRepository
from src.mapping.entity import StrategyEntity
from src.mapping.dto import (
   StrategyGrayLabelTry,
   StrategyGrayLabelTryResult,
   StrategyGrayLabelContinue,
   StrategyGrayLabelContinueResult
)


class GrayLabelStrategyPort:
    def __init__(
        self,
        *,
        storage: IStorage,
        repository: IRepository,
    ):
        self._storage = storage
        self._repository = repository

    async def init(self, entity: StrategyEntity):
        print("Handle gray label:", entity)

    def is_supported_mime(self, mime: FileMIME) -> bool:
        return mime in (FileMIME.MP4, FileMIME.MOV, FileMIME.AVI)

    async def try_analyze(
        self, dto: StrategyGrayLabelTry,
    ) -> StrategyGrayLabelTryResult:
        ...

    async def continue_analyze(
        self, dto: StrategyGrayLabelContinue
    ) -> StrategyGrayLabelContinueResult:
        ...
