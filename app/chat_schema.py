from pydantic import BaseModel

query = """
        CREATE TABLE samchully_log(
            session_id TEXT PRIMARY KEY,  -- 세션 ID, 기본 키
            message_id TEXT NOT NULL,     -- 메시지 ID
            question TEXT,                  -- 질문
            tag TEXT,                    -- 태그
            query TEXT,                      -- 쿼리
            RDB TEXT,                      -- RDB(단가표)
            RAG TEXT [],                    -- RAG(Retrieval 자료)
            RFC TEXT,                      -- RFC 함수 결과
            response TEXT,                   -- 응답
            history TEXT [],                 -- message_id 리스트
            validate_intention TEXT,         -- new vs continue vs general
            validate_additional TEXT,     -- continue + 추가로 데이터 필요한지 yes/no
            validate_tag TEXT,            -- 태그 유효성
            validate_rdb BOOLEAN,            -- RDB 유효성
            validate_rag BOOLEAN,            -- RAG 유효성
            validate_rfc BOOLEAN           -- RFC 유효성
        );
    """

class log_schema(BaseModel):
    session_id: str
    message_id: str
    question: str
    tag: str
    query: str
    rdb: str
    rag: list[str]
    rfc: str
    response: str
    history: list[str]
    validate_intention: str
    validate_additional: str
    validate_tag: str
    validate_rdb: bool
    validate_rag: bool
    validate_rfc: bool
