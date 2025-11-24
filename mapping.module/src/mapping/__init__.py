from typing import NamedTuple

from src.common.redis import redis_client_factory
from src.mapping.interfaces import IStorage, IRepository
from src.mapping.enums import Strategy
from src.mapping.graylabel import GrayLabelStrategyPort
from src.mapping.repository import RedisRepository
from src.mapping.strategy import StrategyPort, StrategyPortConfig
from src.mapping.storage import FilesystemStorage, FilesystemStorageConfig


class MappingApp(NamedTuple):
    storage: IStorage
    repository: IRepository
    strategy_port: StrategyPort
    gray_label_strategy_port: GrayLabelStrategyPort


_redis_client = redis_client_factory(db=0)
_filesystem_storage = FilesystemStorage(
    config=FilesystemStorageConfig(
        download_path="uploads/",
    )
)
_redis_repository = RedisRepository(
    client=_redis_client,
)
_gray_label_strategy_port = GrayLabelStrategyPort(
    storage=_filesystem_storage,
    repository=_redis_repository,
)
_strategy_port = StrategyPort(
    config=StrategyPortConfig(),
    storage=_filesystem_storage,
    repository=_redis_repository,
    strategies={
        Strategy.GRAY_LABEL: _gray_label_strategy_port,
    }
)
_mapping_app = MappingApp(
    storage=_filesystem_storage,
    repository=_redis_repository,
    strategy_port=_strategy_port,
    gray_label_strategy_port=_gray_label_strategy_port,
)


def get_mapping_app() -> MappingApp:
    return _mapping_app


__all__ = (
    "get_mapping_app",
)
