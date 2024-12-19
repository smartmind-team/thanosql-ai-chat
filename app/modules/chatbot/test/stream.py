import asyncio
from typing import AsyncGenerator

from models import schema
from models.exception import StreamTerminated
from modules.chatbot import chatbot
from openai import OpenAI
from utils import logger


async def chat_stream(
    chat_request: schema.chat.ChatRequest, openai_client: OpenAI
) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()

    async def producer(generator):
        try:
            async for item in generator:
                await queue.put(item)
            await queue.put(None)  # Signal completion
        except Exception as e:
            # If an error occurs in a task, put an error signal in the queue and stop
            await queue.put(None)  # To stop further queue processing
            raise e  # Re-raise the exception to be caught in the main try block

    try:
        async for item in chatbot(chat_request):
            yield item
    except StreamTerminated:
        logger.debug("Stream terminated")
        return
