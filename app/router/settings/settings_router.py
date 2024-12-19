from fastapi import APIRouter
from models.schema import chat
from router import router_utils
from utils import logger, mask_string, settings

settings_router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


@settings_router.get("")
async def get_settings():
    # Retrieve chat control settings from Redis and pack into model
    logger.debug("Retrieving Redis Settings")

    def pack_chat_control_response() -> chat.ChatSettingsResponse:
        # Define the fields that need to be fetched from Redis
        field_names = chat.ChatSettingsResponse.model_fields.keys()
        log_msg = "Redis Fields:"
        for f in field_names:
            log_msg += f"\n   - {f}"
        logger.debug(log_msg)

        # Use a dictionary comprehension to fetch values from Redis
        configs = {}
        for field in field_names:
            value = settings.redis.get(field)
            if value is None:
                logger.warning(f"Missing Redis Setting: {field} ({type(value)})")
                value = ""  # 기본값 설정

            if "api_key" in field:
                logger.debug(f"Masking Redis Setting: {field} ({type(value)})")
                value = mask_string(value)

            configs[field] = value

        logger.debug(f"Redis Settings: {configs}")

        return chat.ChatSettingsResponse(**configs)

    return await router_utils.exception_handler(pack_chat_control_response)


@settings_router.patch("")
async def update_settings(request: chat.ChatSettingsRequest):
    data = request.dict_without_none()

    def _update():
        for key, value in data.items():
            settings.redis.set(key, value)
        logger.info("Updated Redis Settings")
        logger.debug(f"Redis Settings: {settings.redis.get_all()}")
        return {"message": "Settings updated successfully"}

    return await router_utils.exception_handler(_update)


@settings_router.get("/models")
async def get_models():
    return await router_utils.exception_handler({"models": settings.app.allowed_models})


@settings_router.get("/tags")
async def get_tags():
    return await router_utils.exception_handler({"tags": settings.app.system_tags})
