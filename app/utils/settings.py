from pydantic import field_validator
from pydantic_settings import BaseSettings
from redis import Redis


class AppSetting(BaseSettings):
    max_retries: int = 1
    max_temperature: int = 1
    default_temperature: int = 1
    system_prompt: str = ""
    allowed_models: list[str] = []
    system_tags: list[str] = []
    max_memory: int = 4

    class Config:
        env_prefix = "app_"


class ThanoSQLSettings(BaseSettings):
    api_token: str = "thanosql_api_token"
    engine_url: str = "thanosql_engine_url"

    class Config:
        env_prefix = "thanosql_"


class FastAPISettings(BaseSettings):
    allow_origins: list[str] = []
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]

    class Config:
        env_prefix = "fastapi_"

    @field_validator("allow_origins", mode="before")
    def split_allow_origins(cls, v: list[str]) -> list[str]:
        if not v:
            return ["*"]
        else:
            return v.split(",")


class OpenAISettings(BaseSettings):
    base_url: str = "https://api.openai.com/v1"
    api_key: str = "NEED_TO_SET_KEY"
    model: str = "NEED_TO_SET_MODEL"
    embedding_model: str = "NEED_TO_SET_EMBEDDING_MODEL"

    class Config:
        env_prefix = "openai_"

    def set_local(self):
        self.base_url = "http://192.168.10.1:8827/v1"
        self.model = (
            "/vllm-workspace/model/Linkbricks-Horizon-AI-Korean-llama-3.1-sft-dpo-8B"
        )
        self.api_key = "EMPTY"


class TEXT2SQLSettings(BaseSettings):
    model: str = "NEED_TO_SET_MODEL"
    api_key: str = "EMPTY"
    base_url: str = "NEED_TO_SET_BASE_URL"

    class Config:
        env_prefix = "text2sql_"


class PostgresSettings(BaseSettings):
    host: str = "NEED_TO_SET_HOST"
    port: int = 5432
    db: str = "NEED_TO_SET_DB"
    user: str = "NEED_TO_SET_USER"
    password: str = "NEED_TO_SET_PASSWORD"

    class Config:
        env_prefix = "postgres_"


class RedisEnvSettings(BaseSettings):
    host: str = "NEED_TO_SET_HOST"
    port: int = 6379
    decode_responses: bool = True

    class Config:
        env_prefix = "redis_"


class RedisSettings:
    def __init__(self):
        self.redis_client = Redis(
            port=RedisEnvSettings().port,
            host=RedisEnvSettings().host,
            decode_responses=RedisEnvSettings().decode_responses,
        )

    def get(self, key: str) -> str:
        value = self.redis_client.get(key)
        return value

    def set(self, key: str, value: str) -> None:
        self.redis_client.set(key, value)

    def get_all(self) -> dict:
        keys = self.redis_client.keys("*")
        return {key: self.get(key) for key in keys}


app = AppSetting()
thanosql = ThanoSQLSettings()
fastapi = FastAPISettings()
openai = OpenAISettings()
text2sql = TEXT2SQLSettings()
db = PostgresSettings()
redis = RedisSettings()

__all__ = [
    "app",
    "thanosql",
    "fastapi",
    "openai",
    "text2sql",
    "db",
    "redis",
]
