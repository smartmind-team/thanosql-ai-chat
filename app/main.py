import asyncio
from typing import AsyncGenerator
from chainlit.utils import mount_chainlit

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from task import generate_chat_completion, generate_chat_title

import app.router as router
from app.utils import settings
from app.utils.logger import logger
from app.models import schema
from app.models.exception import StreamTerminated

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.fastapi.allow_origins,
    allow_credentials=settings.fastapi.allow_credentials,
    allow_methods=settings.fastapi.allow_methods,
    allow_headers=settings.fastapi.allow_headers,
)
app.include_router(router.default_router)
app.include_router(router.settings_router)
app.mount("/data/이지원", StaticFiles(directory="data/이지원"), name="data/이지원")
logger.debug("Initialized FastAPI App")

mount_chainlit(app=app, target="cl_app.py", path="/chainlit")
logger.debug("Initialized chainlit")

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
