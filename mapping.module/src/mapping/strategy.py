from uuid import uuid4
from typing import NamedTuple
from datetime import timedelta

import magic

from src.mapping.enums import Strategy, Status
from src.mapping.interfaces import IStorage, IRepository, IStrategyPort
from src.mapping.exceptions import (
    InvalidStrategy,
    UnsupportedFileMIME,
    StrategyNotFound,
)
from src.mapping.dto import (
    StrategyInit,
    StrategyInitResult,
    StrategyRead,
    StrategyReadResult,
)
from src.mapping.entity import StrategyEntity


class StrategyPortConfig(NamedTuple):
    entity_retention_period: timedelta = timedelta(minutes=7)
    validate_mime_buffer_size: int = 4096
    download_file_name: str = "download"


class StrategyPort:
    def __init__(
        self,
        *,
        config: StrategyPortConfig,
        storage: IStorage,
        repository: IRepository,
        strategies: dict[Strategy, IStrategyPort],
    ):
        self._config = config
        self._storage = storage
        self._repository = repository
        self._strategies = strategies

    async def init(self, dto: StrategyInit) -> StrategyInitResult:
        strategy = self._strategies.get(dto.strategy, None)
        if strategy is None:
            raise InvalidStrategy()

        buffer = await dto.file.read(self._config.validate_mime_buffer_size)
        mime = magic.from_buffer(buffer, mime=True)
        if not strategy.is_supported_mime(mime):
            raise UnsupportedFileMIME()

        entity = StrategyEntity(
            status=Status.QUEUED,
            total_pixels=dto.total_pixels,
            strategy=dto.strategy,
            positions=[],
        )

        await dto.file.seek(0)
        downloaded_file_path = await self._storage.download_file(
            path=entity.path_dir,
            name=self._config.download_file_name,
            file=dto.file,
        )

        await strategy.init(entity, downloaded_file_path)
        await self._repository.save(
            entity, ttl=self._config.entity_retention_period.seconds
        )

        return StrategyInitResult(id=entity.id)

    async def read(self, dto: StrategyRead) -> StrategyReadResult:
        entity = await self._repository.get(dto.id)
        if entity is None:
            raise StrategyNotFound()

        return StrategyReadResult.from_entity(entity)
