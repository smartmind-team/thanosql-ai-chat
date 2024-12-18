import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from router import router_utils
from utils import settings, pack_chat_control_response
from utils.logger import logger
from models.schema import chat, feedback
from modules import chatbot
# from modules.chatbot.test import stream
from modules.client import OpenAIClientSingleton
from modules.feedback import process_feedback

default_router = APIRouter()


@default_router.get("/health")
async def health_check():
    return await router_utils.exception_handler({"status": "healthy"})


@default_router.get("/functions")
async def get_functions():
    async def _get_func():
        return json.loads(settings.redis.get("functions"))

    return await router_utils.exception_handler(_get_func)


@default_router.post("/feedback")
async def post_feedback(request: feedback.FeedbackRequest):

    return await process_feedback(request)

@default_router.post("/chat")
async def post_chat(request: chat.ChatRequest):
    # openai_client = OpenAIClientSingleton.get_sync_client()
    # response = StreamingResponse(
    #     stream.(request, openai_client), media_type="text/event-stream"
    # )
    request = request
    def _response():
        response = JSONResponse(content=chatbot.chatbot(request), media_type="application/json")
        response.headers["x-vercel-ai-data-stream"] = "v1"
        return response
    return router_utils.exception_handler(_response) 

# @default_router.get("/test-chat")
# async def test_chat():
#     # Example chat request
#     chat_request = chat.ChatRequest(
#         messages=[
#             {"role": "user", "content": "Tell me a short joke about programming."},
#         ],
#         model="gpt-4o",
#     )

#     openai_client = OpenAIClientSingleton.get_sync_client()

#     response = StreamingResponse(
#         stream.chat_stream(chat_request, openai_client), media_type="text/event-stream"
#     )
#     response.headers["x-vercel-ai-data-stream"] = "v1"
#     return await response
