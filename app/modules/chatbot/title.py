import sys
import asyncio
from typing import AsyncGenerator
from pathlib import Path

(Path(__file__).parents[3])
from utils import settings
from models import schema
from data import prompt


async def generate_chat_title(
    messages: list[dict], openai_client
) -> AsyncGenerator[str, None]:
    model = settings.redis.get("openai_model")
    question = messages[-1]["content"]
    current_messages = [
        {
            "role": "user",
            "content": prompt.user_prompt_generate_message_title.format(
                question=question
            ),
        }
    ]
    try:
        response = openai_client.chat.completions.create(
            messages=current_messages, model=model
        )
        title = response.choices[0].message.content
    except Exception:
        # If creation fails, only first 30 characters of the question are returned.
        title = question[:30]
    yield schema.base.StreamProtocolHandler.yield_annotation(title, "title")
