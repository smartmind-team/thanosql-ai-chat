import json
from typing import Any, AsyncGenerator, Dict, List

from client import thanosql_client
from exception import StreamTerminated
from pglast import parse_sql
from pglast.stream import IndentedStream
from prompt import (
    system_prompt_generate_query_result_summary,
    system_prompt_generate_sql,
    user_prompt_generate_message_title,
)
from schema import ChatRequest, StreamProtocolHandler, Table
from settings import redis_settings, settings
from util import get_create_table_statement, merge_list
from chatbot import chatbot

import logging

logger = logging.getLogger("uvicorn.error")

############
# Tasks
############
async def generate_chat_completion(
    chat_request: ChatRequest | None, openai_client
) -> AsyncGenerator[str, None]:
    model_settings = redis_settings.get_all()
    try:
        message = chatbot(chat_request)
        yield f"0:{json.dumps(message['content'])}\n"
        yield f"8:{json.dumps(message['annotations'])}\n"

    except Exception as e:
        logger.error(f'generate_chat_completion: {e}')
        yield f"0:{json.dumps('Something went wrong generating')}\n"
        raise StreamTerminated()

    # create_table_statement = prepare_table_statement(chat_request)

    # if create_table_statement is None:
    #     async for message in handle_regular_chat(
    #         chat_request, openai_client, model_settings
    #     ):
    #         yield message
    # else:
    #     async for message in handle_sql_chat(
    #         chat_request, openai_client, model_settings, create_table_statement
    #     ):
    #         yield message
    

# ############
# # Utils
# ############
# async def handle_regular_chat(
#     chat_request: ChatRequest, openai_client, model_settings: Dict[str, Any]
# ) -> AsyncGenerator[str, None]:
#     messages = prepare_messages(
#         chat_request.messages, model_settings.get("system_prompt")
#     )

#     try:
#         async for chunk in stream_openai_response(
#             openai_client, messages, model_settings
#         ):
#             yield chunk
#     except Exception as e:
#         yield StreamProtocolHandler.yield_error(e)
#         yield StreamProtocolHandler.yield_finish_message("error")
#         raise StreamTerminated()


# async def handle_sql_chat(
#     chat_request: ChatRequest,
#     openai_client,
#     model_settings: Dict[str, Any],
#     create_table_statement: str,
# ) -> AsyncGenerator[str, None]:
#     question = chat_request.messages[-1]["content"]
#     udf_list = json.loads(model_settings.get("functions"))
#     sql_messages = prepare_sql_messages(question, create_table_statement, udf_list)

#     try:
#         query_log = generate_and_execute_sql(sql_messages, model_settings)
#         yield StreamProtocolHandler.yield_annotation(
#             data=query_log, annotation="query_log"
#         )

#         summary_messages = prepare_summary_messages(model_settings, query_log, question)
#         async for chunk in stream_openai_response(
#             openai_client, summary_messages, model_settings
#         ):
#             yield chunk
#     except Exception as e:
#         yield StreamProtocolHandler.yield_error(e)
#         yield StreamProtocolHandler.yield_finish_message("error")
#         raise StreamTerminated()


# def prepare_table_statement(chat_request: ChatRequest) -> str | None:
#     if chat_request.base_tables or chat_request.prompt_tables:
#         table_list: list[Table] = merge_list(
#             chat_request.base_tables, chat_request.prompt_tables
#         )
#         if table_list:
#             return get_create_table_statement(table_list)
#     return None


# def prepare_messages(
#     messages: List[Dict[str, str]], system_prompt: str | None
# ) -> List[Dict[str, str]]:
#     if system_prompt:
#         return [{"role": "system", "content": system_prompt}] + messages
#     return messages


# def prepare_sql_messages(
#     question: str, create_table_statement: str, udf_list: List[Dict[str, Any]]
# ) -> List[Dict[str, str]]:
#     return [
#         {
#             "role": "system",
#             "content": system_prompt_generate_sql.format(
#                 create_table_statement=create_table_statement, udf_list=udf_list
#             ),
#         },
#         {"role": "user", "content": question},
#     ]


# def generate_and_execute_sql(
#     sql_messages: List[Dict[str, str]], model_settings: Dict[str, Any]
# ):
#     text2sql_model = model_settings.get("text2sql_model")
#     text2sql_api_key = model_settings.get("text2sql_api_key")
#     text2sql_base_url = model_settings.get("text2sql_base_url")

#     thanosql_text2sql_query = f"""
#     SELECT
#         thanosql.generate(
#             input := $$'{json.dumps(sql_messages)}'$$,
#             engine := 'openai',
#             model := '{text2sql_model}',
#             token := '{text2sql_api_key}',
#             base_url := '{text2sql_base_url}'
#         ) AS reply
#     LIMIT 1
#     """

#     query_log = {}
#     max_retries = settings.max_retries
#     for _ in range(max_retries):
#         try:
#             # Generate SQL
#             response = thanosql_client.query.execute(
#                 thanosql_text2sql_query, max_results=10
#             )
#             raw_query_string = response.records.data[0]["reply"]
#             query_string = IndentedStream()(parse_sql(raw_query_string))

#             # Execute SQL
#             query_log = thanosql_client.query.execute(query_string, max_results=10)
#             if not query_log.error_result:
#                 if query_log.records:
#                     query_log.records = dict(query_log.records)
#                 return query_log
#         except Exception:
#             continue
#     else:
#         # This block is executed if the loop completes without finding a successful result
#         return query_log
#         # TODO Decide whether raise Error or not
#         # raise Exception("Max retries reached. Failed to generate or execute SQL query.")


# def prepare_summary_messages(
#     model_settings: Dict[str, Any], query_log: Any, question: str
# ) -> List[Dict[str, str]]:
#     return [
#         {
#             "role": "system",
#             "content": system_prompt_generate_query_result_summary.format(
#                 system_prompt=model_settings.get("system_prompt"),
#                 query_log=str(query_log),
#             ),
#         },
#         {"role": "user", "content": question},
#     ]


# async def stream_openai_response(
#     openai_client, messages: List[Dict[str, str]], model_settings: Dict[str, Any]
# ) -> AsyncGenerator[str, None]:
#     logger.info(messages)
#     response = openai_client.chat.completions.create(
#         messages=messages,
#         model=model_settings.get("openai_model"),
#         stream=True,
#         temperature=float(model_settings.get("temperature") or 1),
#     )
#     logger.info(response)
#     response = 'hi junyoung'
#     for chunk in response:
#         payload = chunk.choices[0].delta.content
#         if payload and isinstance(payload, str):
#             yield StreamProtocolHandler.yield_content(payload)
