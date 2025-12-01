from typing import NamedTuple
from datetime import timedelta

from src.common.redis import redis_client_factory
from src.mapping.interfaces import IStorage, IRepository, IExposeFilePort
from src.mapping.enums import Strategy
from src.mapping.graylabel import GrayLabelStrategyPort
from src.mapping.repository import RedisRepository
from src.mapping.strategy import StrategyPort, StrategyPortConfig
from src.mapping.storage import FilesystemStorage, FilesystemStorageConfig
from src.mapping.expose_file import ExposeFilePort, ExposeFilePortConfig


class MappingApp(NamedTuple):
    storage: IStorage
    repository: IRepository
    expose_file_port: IExposeFilePort
    strategy_port: StrategyPort
    gray_label_strategy_port: GrayLabelStrategyPort


_redis_client = redis_client_factory(db=0)
_filesystem_storage = FilesystemStorage(
    config=FilesystemStorageConfig(
        path="storage/",
    )
)
_redis_repository = RedisRepository(
    client=_redis_client,
)
_expose_file_port = ExposeFilePort(
    config=ExposeFilePortConfig(),
    storage=_filesystem_storage,
    repository=_redis_repository,
)
_gray_label_strategy_port = GrayLabelStrategyPort(
    storage=_filesystem_storage,
    repository=_redis_repository,
    expose_file_port=_expose_file_port,
)
_strategy_port = StrategyPort(
    config=StrategyPortConfig(
        entity_retention_period=timedelta(hours=1),
    ),
    storage=_filesystem_storage,
    repository=_redis_repository,
    strategies={
        Strategy.GRAY_LABEL: _gray_label_strategy_port,
    }
)
_mapping_app = MappingApp(
    storage=_filesystem_storage,
    repository=_redis_repository,
    expose_file_port=_expose_file_port,
    strategy_port=_strategy_port,
    gray_label_strategy_port=_gray_label_strategy_port,
)


def get_mapping_app() -> MappingApp:
    return _mapping_app


__all__ = (
    "get_mapping_app",
)
