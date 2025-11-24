from typing import Protocol, runtime_checkable
from pathlib import Path
from uuid import UUID

from src.mapping.enums import FileMIME
from src.mapping.entity import StrategyEntity


@runtime_checkable
class IFile(Protocol):
    name: str
    size: int
    extension: str

    async def read(self, chunk_size: int) -> bytes: ...

    async def seek(self, offset: int) -> None: ...


class IStorage(Protocol):
    async def download(self, file: IFile, filename: str | None = None) -> Path: ...

    async def delete(self, file_path: Path) -> bool: ...


class IRepository(Protocol):
    async def save(self, entity: StrategyEntity, ttl: int = 0) -> bool: ...

    async def get(self, _id: UUID) -> StrategyEntity | None: ...


class IStrategyPort(Protocol):
    async def init(self, entity: StrategyEntity) -> None: ...

    def is_supported_mime(self, mime: FileMIME) -> bool: ...
