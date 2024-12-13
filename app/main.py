import asyncio
import json
from typing import AsyncGenerator

from chainlit.utils import mount_chainlit
from client import OpenAIClientSingleton
from exception import StreamTerminated
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from schema import ChatRequest, ChatSettingsRequest
from settings import redis_settings, settings
from feedback import FeedbackRequest, process_feedback
from task import generate_chat_completion
from util import pack_chat_control_response
from chatbot import chatbot
import logging

logger = logging.getLogger("thanosql-ai-chat")

app = FastAPI()

origins = settings.cors_origins.split(",") if settings.cors_origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/data/이지원", StaticFiles(directory="data/이지원"), name="data/이지원")

mount_chainlit(app=app, target="cl_app.py", path="/chainlit")


async def chat_stream(
    chat_request: ChatRequest, openai_client: OpenAI
) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()

    async def producer(generator):
        try:
            async for item in generator:
                logger.info(f'item: {item}')
                await queue.put(item)
            await queue.put(None)  # Signal completion
        except Exception as e:
            # If an error occurs in a task, put an error signal in the queue and stop
            await queue.put(None)  # To stop further queue processing
            raise e  # Re-raise the exception to be caught in the main try block

    try:
        # Task 1
        # Generate title of message(query)
        # title_task = asyncio.create_task(
        #     producer(generate_chat_title(chat_request.messages, openai_client))
        # )

        # Task 2
        # Generate SQL from message(Text-to-SQL) and execute SQL with ThanoSQL Client,
        # then analyze Query Log from client and generate answer
        main_task = asyncio.create_task(
            producer(generate_chat_completion(chat_request, openai_client))
        )

        active_tasks = 1
        while active_tasks > 0:
            item = await queue.get()
            if item is None:
                active_tasks -= 1
            else:
                yield item

        # Wait for tasks to finish
        # await title_task
        await main_task

    except StreamTerminated:
        # title_task.cancel()
        main_task.cancel()

        # The stream has been terminated, we can stop here
        return


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat")
async def chat(chat_request: ChatRequest):
    openai_client = OpenAIClientSingleton.get_sync_client()

    response = StreamingResponse(
        chat_stream(chat_request, openai_client), media_type="text/event-stream"
    )
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response


@app.get("/settings")
async def get_settings():
    try:
        return pack_chat_control_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/settings")
async def update_settings(request: ChatSettingsRequest):
    try:
        # Get only fields that are not None
        data = request.dict_without_none()

        # Set each key-value pair in Redis
        for key, value in data.items():
            redis_settings.set(key, value)

        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/functions")
async def get_functions():
    try:
        functions = json.loads(redis_settings.get("functions"))
        return functions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test-chat")
async def test_chat():
    # Example chat request
    chat_request = ChatRequest(
        messages=[
            {"role": "user", "content": "Tell me a short joke about programming."},
        ],
        model="gpt-4o",
    )

    openai_client = OpenAIClientSingleton.get_sync_client()

    response = StreamingResponse(
        chat_stream(chat_request, openai_client), media_type="text/event-stream"
    )
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response


@app.post("/feedback")
async def post_feedback(request: FeedbackRequest):
    """
    Handle feedback request by delegating to process_feedback function.
    """
    
    return process_feedback(request)
