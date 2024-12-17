import sys
from pathlib import Path

from typing import Literal, Optional
from pydantic import BaseModel

(Path(__file__).parents[4])
from utils import settings
from models.schema import base
from utils.logger import logger


class ChatRequest(BaseModel):
    messages: list[dict]
    model: Literal[settings.app.allowed_models]
    session_id: str
    tag: str | None = None
    base_tables: list[base.Table] | None = None
    prompt_tables: list[base.Table] | None = None


class ChatSettingsResponse(BaseModel):
    openai_model: str
    openai_base_url: str
    openai_api_key: str
    text2sql_model: str
    text2sql_base_url: str
    text2sql_api_key: str
    temperature: str
    max_temperature: str
    system_prompt: str


class ChatSettingsRequest(BaseModel):
    openai_model: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    text2sql_model: Optional[str] = None
    text2sql_base_url: Optional[str] = None
    text2sql_api_key: Optional[str] = None
    temperature: Optional[str] = None
    system_prompt: Optional[str] = None

    # Method to convert the model to a dict, excluding None values
    def dict_without_none(self):
        return {k: v for k, v in self.model_dump().items() if v is not None}


class ChatLogSchema(BaseModel):
    session_id: str
    message_id: str
    question: str
    tag: str | None = None
    query: str | None = None
    rdb: str | None = None
    rag: list[str] | None = None
    rfc: str | None = None
    response: str | None = None
    history: list[str] | None = None
    validate_intention: str | None = None
    validate_additional: str | None = None
    validate_tag: str | None = None
    validate_rdb: bool | None = None
    validate_rag: bool | None = None
    validate_rfc: bool | None = None
