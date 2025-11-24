from uuid import UUID

import redis.asyncio as aioredis
from msgspec import msgpack

from src.mapping.entity import StrategyEntity


def _get_strategy_hash_name(_id: UUID):
    return f"strategy:{_id}"


def _map_strategy_entity_to_redis(entity: StrategyEntity) -> dict[str, str]:
    return {
        "id": str(entity.id),
        "status": entity.status,
        "total_pixels": entity.total_pixels,
        "strategy": entity.strategy,
        "file_path": str(entity.file_path),
        "positions": msgpack.encode(entity.positions)
    }


def _map_redis_to_strategy_entity(data: dict[bytes, bytes]) -> StrategyEntity:
    def _decode_value(key: str, value_bytes: bytes):
        if key == "positions":
            return msgpack.decode(value_bytes)
        return value_bytes.decode()

    init_data = {}
    for key_bytes, value_bytes in data.items():
        key = key_bytes.decode()
        init_data[key] = _decode_value(key, value_bytes)

    return StrategyEntity(**init_data)


class RedisRepository:
    def __init__(
        self,
        *,
        client: aioredis.Redis,
    ):
        self._client = client

    async def save(self, entity: StrategyEntity, ttl: int = 0) -> bool:
        name = _get_strategy_hash_name(entity.id)
        mapping = _map_strategy_entity_to_redis(entity)

        pipe = self._client.pipeline()
        pipe.hset(name, mapping=mapping)
        pipe.expire(name, ttl)

        n_added, _ = await pipe.execute()

        return n_added > 0

    async def get(self, _id: UUID) -> StrategyEntity | None:
        name = _get_strategy_hash_name(_id)
        data = await self._client.hgetall(name)

        if not data:
            return None

        return _map_redis_to_strategy_entity(data)
