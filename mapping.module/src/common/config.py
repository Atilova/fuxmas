from typing import Literal
from urllib.parse import quote, urlunparse

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseModel):
    name: str = "Fuxmas"
    description: str = "Fuxmas LED pixel-mapping service"
    version: str = "0.0.0"
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    enabled_access_logs: bool = True


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    username: str = ""
    password: str = ""

    def url(self, db: int = 0) -> str:
        username, password = (
            self._quote_or_empty_str(self.username),
            self._quote_or_empty_str(self.password),
        )
        auth = f"{username}:{password}@" if username or password else ""

        return urlunparse((
            "redis",
            f"{auth}{self.host}:{self.port}",
            f"/{db}",
            "",
            "",
            "",
        ))

    def _quote_or_empty_str(self, value: str):
        return quote(value) if value else ""


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="cf__",
        env_nested_delimiter="__",
    )

    service: ServiceConfig = Field(default_factory=ServiceConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)


_config = Config()
service_config = _config.service
redis_config = _config.redis
