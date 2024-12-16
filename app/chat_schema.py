from pydantic import BaseModel

class log_schema(BaseModel):
    session_id: str
    message_id: str
    question: str
    tag: str | None = None
    query: str | None = None
    rdb: str | None = None
    rag: list[str] | None = None
    rfc: str | None = None
    response: str | None = None
    history: list[str] | None = None
    validate_intention: str | None = None
    validate_additional: str | None = None
    validate_tag: str | None = None
    validate_rdb: bool | None = None
    validate_rag: bool | None = None
    validate_rfc: bool | None = None
