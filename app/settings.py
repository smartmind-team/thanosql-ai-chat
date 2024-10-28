import os

from pydantic_settings import BaseSettings
from redis import Redis


class Setting(BaseSettings):
    thanosql_api_token: str = os.environ.get("THANOSQL_API_TOKEN")
    thaonsql_engine_url: str = os.environ.get("THANOSQL_ENGINE_URL")

    max_retries: int = os.environ.get("MAX_RETRIES", 1)

    cors_origins: str = os.environ.get("CORS_ORIGINS")


class RedisSettings:
    def __init__(self):
        self.redis_client = Redis(host="redis", port=6379, decode_responses=True)

    def get(self, key: str) -> str:
        value = self.redis_client.get(key)
        return value

    def set(self, key: str, value: str) -> None:
        self.redis_client.set(key, value)

    def get_all(self) -> dict:
        keys = self.redis_client.keys("*")
        return {key: self.get(key) for key in keys}


settings = Setting()
redis_settings = RedisSettings()
