import sys
import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

sys.path.append(Path(__file__).parents[2])
from app.utils import settings, pack_chat_control_response
from app.utils.logger import logger
from app.models.schema import chat, feedback
from app.modules.client import OpenAIClientSingleton
from app.modules.feedback import process_feedback
from app.modules.chatbot.test import stream

from app.router import router_utils
from app.router.settings import settings_router


default_router = APIRouter()


@default_router.get("/health")
async def health_check():
    return await router_utils.exception_handler({"status": "healthy"})


@default_router.get("/settings")
async def get_settings():
    return await router_utils.exception_handler(pack_chat_control_response)


@default_router.patch("/settings")
async def update_settings(request: chat.ChatSettingsRequest):
    data = request.dict_without_none()

    async def _update():
        for key, value in data.items():
            settings.redis.set(key, value)
        return {"message": "Settings updated successfully"}

    return await router_utils.exception_handler(_update)


@default_router.get("/functions")
async def get_functions():
    async def _get_func():
        return json.loads(settings.redis.get("functions"))

    return await router_utils.exception_handler(_get_func)


@default_router.post("/feedback")
async def post_feedback(request: feedback.FeedbackRequest):

    return await process_feedback(request)


@default_router.get("/test-chat")
async def test_chat():
    # Example chat request
    chat_request = chat.ChatRequest(
        messages=[
            {"role": "user", "content": "Tell me a short joke about programming."},
        ],
        model="gpt-4o",
    )

    openai_client = OpenAIClientSingleton.get_sync_client()

    response = StreamingResponse(
        stream.chat_stream(chat_request, openai_client), media_type="text/event-stream"
    )
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return await response