import logging
import psycopg2
from chat_schema import log_schema

logger = logging.getLogger(__name__)
# connection = "postgresql+psycopg://thanosql_user:thanosql@18.119.33.153:8821/default_database"


def create_log_table():
    connection = psycopg2.connect(host='18.119.33.153', dbname='default_database', user='thanosql_user', password='thanosql', port=8821)
    cursor = connection.cursor()
    try:
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
            history TEXT [],                 -- 이전 질문 및 응답 (배열 형태)
            validate_intention TEXT,         -- new vs continue vs general
            validate_additional TEXT,     -- continue + 추가로 데이터 필요한지 yes/no
            validate_tag TEXT,            -- 태그 유효성
            validate_rdb BOOLEAN,            -- RDB 유효성
            validate_rag BOOLEAN,            -- RAG 유효성
            validate_rfc BOOLEAN           -- RFC 유효성
        );
        """
        cursor.execute(query)
    except Exception as e:
        logger.error(f'log table create error: {e}')

def null_check(value):
    if not value:
        return "NULL"
    return f"'{value}'"

def array_pg(value):
    if not value:
        return "NULL"
    return f"'{{{','.join(value)}}}'"

def preprocess_log(value: str):
    return value.replace("'", '\'')
def insert_log(Log_schema: log_schema):
    # PostgreSQL 데이터베이스에 연결
    connection = psycopg2.connect(host='18.119.33.153', dbname='default_database', user='thanosql_user', password='thanosql', port=8821)
    cursor = connection.cursor()
    try:
        query = f"""
            INSERT INTO samchully_log (
                session_id,
                message_id,
                question,
                tag,
                query,
                rdb,
                rag,
                rfc,
                response,
                history,
                validate_intention,
                validate_additional,
                validate_tag,
                validate_rdb,
                validate_rag,
                validate_rfc
            )
            VALUES (
                '{Log_schema.session_id}',
                '{Log_schema.message_id}',
                '{Log_schema.question}',
                '{Log_schema.tag}',
                {null_check(Log_schema.query)},
                {null_check(Log_schema.rdb)},
                ARRAY{Log_schema.rag},
                {null_check(Log_schema.rfc)},
                '{Log_schema.response}',
                ARRAY{Log_schema.history},
                '{Log_schema.validate_intention}',
                '{Log_schema.validate_additional}',
                '{Log_schema.validate_tag}',
                {Log_schema.validate_rdb},
                {Log_schema.validate_rag},
                {Log_schema.validate_rfc}
            );
        """
        logger.info(f'insert parameters: {Log_schema}')
        logger.info(f'insert query: {query}')
        response=cursor.execute(query)
        logger.info(f'log insert: {response}')

        # 커밋 및 연결 종료
        connection.commit()
        cursor.close()
        connection.close()

    except Exception as e:
        logger.error(f'log insert error: {e}')