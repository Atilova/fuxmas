from typing import NamedTuple

from src.mapping.interfaces import IStorage, IRepository


class GarbageCollectorPortConfig(NamedTuple):
    ...

# TODO: Implement to clean up files stored on disk/storage
class GarbageCollectorPort:
    def __init__(
        self,
        *,
        config: GarbageCollectorPortConfig,
        storage: IStorage,
        repository: IRepository,
    ):
        self._config = config
        self._storage = storage
        self._repository = repository

    async def clean(self):
        ...
