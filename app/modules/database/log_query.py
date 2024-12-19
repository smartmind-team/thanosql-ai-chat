"This script was created for backuping query log"
from models import schema

create_log_query = """
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
    history TEXT [],                 -- 이전 질문 및 응답 (배열 형태)
    validate_intention TEXT,         -- new vs continue vs general
    validate_additional TEXT,     -- continue + 추가로 데이터 필요한지 yes/no
    validate_tag TEXT,            -- 태그 유효성
    validate_rdb BOOLEAN,            -- RDB 유효성
    validate_rag BOOLEAN,            -- RAG 유효성
    validate_rfc BOOLEAN           -- RFC 유효성
);
"""

# insert_log_query = f"""
#             INSERT INTO samchully_log (
#                 session_id,
#                 message_id,
#                 question,
#                 tag,
#                 query,
#                 rdb,
#                 rag,
#                 rfc,
#                 response,
#                 history,
#                 validate_intention,
#                 validate_additional,
#                 validate_tag,
#                 validate_rdb,
#                 validate_rag,
#                 validate_rfc
#             )
#             VALUES (
#                 '{schema.chat.ChatLogSchema.session_id}',
#                 '{schema.chat.ChatLogSchema.message_id}',
#                 '{schema.chat.ChatLogSchema.question}',
#                 '{schema.chat.ChatLogSchema.tag}',
#                 {null_check(schema.chat.ChatLogSchema.query)},
#                 {null_check(schema.chat.ChatLogSchema.rdb)},
#                 ARRAY{schema.chat.ChatLogSchema.rag},
#                 {null_check(schema.chat.ChatLogSchema.rfc)},
#                 '{schema.chat.ChatLogSchema.response}',
#                 ARRAY{schema.chat.ChatLogSchema.history},
#                 '{schema.chat.ChatLogSchema.validate_intention}',
#                 '{schema.chat.ChatLogSchema.validate_additional}',
#                 '{schema.chat.ChatLogSchema.validate_tag}',
#                 {schema.chat.ChatLogSchema.validate_rdb},
#                 {schema.chat.ChatLogSchema.validate_rag},
#                 {schema.chat.ChatLogSchema.validate_rfc}
#             );
#         """
