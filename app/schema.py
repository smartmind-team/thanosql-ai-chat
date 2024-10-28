import json
from typing import Literal, Optional

from pydantic import BaseModel


class Message(BaseModel):
    type: Literal["ai", "system", "user"] = "user"
    content: str


class Table(BaseModel):
    table_schema: str = "public"
    table_name: str


class ChatRequest(BaseModel):
    messages: list[dict]
    base_tables: list[Table] | None = None
    prompt_tables: list[Table] | None = None


class ChatSettingsResponse(BaseModel):
    openai_model: str
    openai_base_url: str
    openai_api_key: str
    text2sql_model: str
    text2sql_base_url: str
    text2sql_api_key: str
    temperature: str
    max_temperature: str
    system_prompt: str


class ChatSettingsRequest(BaseModel):
    openai_model: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    text2sql_model: Optional[str] = None
    text2sql_base_url: Optional[str] = None
    text2sql_api_key: Optional[str] = None
    temperature: Optional[str] = None
    system_prompt: Optional[str] = None

    # Method to convert the model to a dict, excluding None values
    def dict_without_none(self):
        return {k: v for k, v in self.dict().items() if v is not None}


class MessageAnnotation:
    def __init__(self, type: str, data=None):
        self.type = type
        self.data = data

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value: str):
        valid_type_list = ["title", "query_log", "error"]
        if value in valid_type_list:
            self._type = value
        else:
            raise ValueError(
                f"Invalid type. Must be one of: {', '.join(valid_type_list)}"
            )

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def payload(self):
        # TODO modify list to single dict
        return [{"type": self._type, "data": self._data}]

    def __str__(self):
        return str(self.payload)

    def __repr__(self):
        return f"MessageAnnotation(type='{self._type}', data={repr(self._data)})"


class StreamProtocolHandler:
    """
    A class to handle the stream protocol for AI responses.

    This class provides methods to format and process streaming responses
    according to the specified protocol, including handling titles, content chunks,
    and errors.

    https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol
    """

    @staticmethod
    def yield_annotation(data, annotation) -> str:
        if annotation == "title":
            msg = MessageAnnotation("title", data)
            return f"8:{json.dumps(msg.payload)}\n"

        elif annotation == "query_log":
            msg = MessageAnnotation("query_log", dict(data))
            return f"8:{json.dumps(msg.payload, default=str)}\n"

    @staticmethod
    def yield_content(content: str) -> str:
        return f"0:{json.dumps(content)}\n"

    @staticmethod
    def yield_error(e: Exception) -> str:
        """
        Generate error message and finish message parts for streaming.

        Args:
            e: The exception to be reported

        Returns:
            Error message followed by finish message
        """
        return f"3:{json.dumps(str(e))}\n"

    @staticmethod
    def yield_finish_message(
        finish_reason: str = "stop",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> str:
        """
        Generate a finish message part for streaming.

        Args:
            finish_reason: The reason for finishing ('stop' or 'error')
            prompt_tokens: Optional number of tokens in the prompt
            completion_tokens: Optional number of tokens in the completion

        Returns:
            A formatted string representing the finish message part
        """
        if finish_reason not in ["stop", "error"]:
            raise ValueError("finish_reason must be either 'stop' or 'error'")

        return 'd:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}}}}\n'.format(
            reason=finish_reason, prompt=prompt_tokens, completion=completion_tokens
        )
