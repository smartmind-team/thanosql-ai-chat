import sys
import asyncio
from pathlib import Path
from typing import AsyncGenerator

from openai import OpenAI

from utils.logger import logger
from models import schema
from models.exception import StreamTerminated
from modules.chatbot import chatbot

async def chat_stream(
    chat_request: schema.chat.ChatRequest, openai_client: OpenAI
) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()

    try:
        # chatbot 함수의 결과를 동기적으로 처리
        for item in chatbot(chat_request):
            yield item

    except StreamTerminated:
        return
