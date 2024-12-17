import sys
import asyncio
from pathlib import Path
from typing import AsyncGenerator

from openai import OpenAI

sys.path.append(Path(__file__).parents[4])
from app.utils.logger import logger
from app.models import schema
from app.models.exception import StreamTerminated

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
        return
