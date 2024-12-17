import sys
from pathlib import Path

from fastapi import APIRouter

from utils import settings
from utils.logger import logger
from models.schema import chat
from router import router_utils

settings_router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


@settings_router.get("/")
def get_settings():
    # Retrieve chat control settings from Redis and pack into model
    def pack_chat_control_response() -> chat.ChatSettingsResponse:
        # Define the fields that need to be fetched from Redis
        field_names = chat.ChatSettingsResponse.keys()

        # Use a dictionary comprehension to fetch values from Redis
        configs = {
            field: (
                mask_string(settings.redis.get(field))
                if "api_key" in field
                else (settings.redis.get(field) or "")
            )
            for field in field_names
        }

        return chat.ChatSettingsResponse(**configs)

    return router_utils.exception_handler(pack_chat_control_response)


@settings_router.patch("/")
def update_settings(request: chat.ChatSettingsRequest):
    data = request.dict_without_none()

    def _update():
        for key, value in data.items():
            settings.redis.set(key, value)
        logger.info("Updated Redis Settings")
        logger.debug(f"Redis Settings: {settings.redis.get_all()}")
        return {"message": "Settings updated successfully"}

    return router_utils.exception_handler(_update)


@settings_router.get("/models")
def get_models():
    return router_utils.exception_handler({"models": settings.app.allowed_models})


@settings_router.get("/tags")
def get_tags():
    return router_utils.exception_handler({"tags": settings.app.system_tags})
