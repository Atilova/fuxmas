from typing import NamedTuple
from uuid import UUID
from pathlib import Path
from datetime import timedelta

from src.mapping.entity import ExposedFileEntity
from src.mapping.exceptions import ExposeFileNotFound
from src.mapping.interfaces import (
    IRepository,
    IStorage,
)


class ExposeFilePortConfig(NamedTuple):
    ttl: timedelta = timedelta(minutes=5)


class ExposeFilePort:
    def __init__(
        self,
        *,
        config: ExposeFilePortConfig,
        storage: IStorage,
        repository: IRepository,
    ):
        self._config = config
        self._storage = storage
        self._repository = repository

    async def expose(self, file_path: Path) -> tuple[bool, UUID | None]:
        if not await self._storage.exists(file_path):
            return False, None

        entity = ExposedFileEntity(file_path=file_path)
        is_ok = await self._repository.save_exposed_file(
            entity, ttl=self._config.ttl
        )

        return is_ok, entity.id

    async def get_path(self, entity_id: UUID) -> Path:
        entity = await self._repository.get_exposed_file(entity_id)
        if entity is None:
           raise ExposeFileNotFound()

        if not await self._storage.exists(entity.file_path):
            await self._repository.delete_exposed_file(entity.id)
            raise ExposeFileNotFound()

        return entity.file_path
