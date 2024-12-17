import sys
from pathlib import Path
from threading import Lock
from typing import Optional

from openai import AsyncOpenAI, OpenAI

sys.path.append(Path(__file__).parents[3])
from utils import settings


class OpenAIClientSingleton:
    _instance: Optional["OpenAIClientSingleton"] = None
    _lock = Lock()
    _sync_client: Optional[OpenAI] = None
    _async_client: Optional[AsyncOpenAI] = None
    _current_api_key: Optional[str] = None
    _current_base_url: Optional[str] = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # Initialize Redis and OpenAI clients on first creation
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """Initialize Redis connection and OpenAI clients with settings from Redis"""
        # Get OpenAI settings from Redis
        self._current_api_key = settings.redis.get("openai_api_key")
        self._current_base_url = settings.redis.get("openai_base_url")

        if not self._current_api_key or not self._current_base_url:
            raise ValueError("Required OpenAI settings not found in Redis")

        # Initialize both sync and async OpenAI clients
        self._init_clients()

    def _init_clients(self):
        """Initialize or reinitialize both sync and async clients"""
        self._sync_client = OpenAI(
            api_key=self._current_api_key, base_url=self._current_base_url
        )
        self._async_client = AsyncOpenAI(
            api_key=self._current_api_key, base_url=self._current_base_url
        )

    def refresh_clients(self) -> None:
        """Refresh clients with latest Redis settings if they've changed"""
        with self._lock:
            new_api_key = settings.redis.get("openai_api_key")
            new_base_url = settings.redis.get("openai_base_url")

            if (
                new_api_key != self._current_api_key
                or new_base_url != self._current_base_url
            ):

                self._current_api_key = new_api_key
                self._current_base_url = new_base_url
                self._init_clients()

    @classmethod
    def get_sync_client(cls) -> OpenAI:
        """Get the synchronous OpenAI client instance"""
        instance = cls()
        instance.refresh_clients()
        return instance._sync_client

    @classmethod
    def get_async_client(cls) -> AsyncOpenAI:
        """Get the asynchronous OpenAI client instance"""
        instance = cls()
        instance.refresh_clients()
        return instance._async_client
