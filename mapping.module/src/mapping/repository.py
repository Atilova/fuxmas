from uuid import UUID
from pathlib import Path

import redis.asyncio as aioredis
from msgspec import msgpack

from src.mapping.entity import StrategyEntity, ExposedFileEntity


def _get_strategy_hash_name(entity_id: UUID):
    return f"strategy:{entity_id}"


def _get_exposed_file_key_name(entity_id: UUID):
    return f"file:{entity_id}"


def _map_strategy_entity_to_redis(entity: StrategyEntity) -> dict[str, str]:
    return {
        "id": str(entity.id),
        "status": entity.status,
        "total_pixels": entity.total_pixels,
        "strategy": entity.strategy,
        "positions": msgpack.encode(entity.positions)
    }


def _map_redis_to_strategy_entity(data: dict[bytes, bytes]) -> StrategyEntity:
    def _decode_value(key: str, value_bytes: bytes):
        if key == "positions":
            return msgpack.decode(value_bytes)

        value = value_bytes.decode()
        if key == "total_pixels":
            return int(value)

        return value

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

    async def save(self, entity: StrategyEntity, ttl: int | None = None) -> bool:
        name = _get_strategy_hash_name(entity.id)
        mapping = _map_strategy_entity_to_redis(entity)

        pipe = self._client.pipeline()
        pipe.hset(name, mapping=mapping)

        if ttl is not None:
            pipe.expire(name, ttl)

        n_added, *_ = await pipe.execute()

        return n_added > 0

    async def get(self, entity_id: UUID) -> StrategyEntity | None:
        name = _get_strategy_hash_name(entity_id)
        data = await self._client.hgetall(name)

        if not data:
            return None

        return _map_redis_to_strategy_entity(data)

    async def save_exposed_file(self, entity: ExposedFileEntity, ttl: int = 0) -> bool:
        name = _get_exposed_file_key_name(entity.id)
        is_ok = await self._client.set(
            name,
            msgpack.encode(entity),
            nx=True,
            ex=ttl,
        )

        return is_ok

    async def get_exposed_file(self, entity_id: UUID) -> ExposedFileEntity | None:
        name = _get_exposed_file_key_name(entity_id)
        data = await self._client.get(name)
        if data is None:
            return None

        decoded_data = msgpack.decode(data)
        entity = ExposedFileEntity(
            file_path=Path(decoded_data["file_path"]),
        )

        return entity

    async def delete_exposed_file(self, entity_id: UUID) -> bool:
        name = _get_exposed_file_key_name(entity_id)
        n_delete = await self._client.delete(name)

        return n_delete > 0
