import json

import chainlit as cl
from chainlit.input_widget import Select
from client import OpenAIClientSingleton, thanosql_client
from task import prepare_sql_messages, prepare_summary_messages
from util import get_create_table_statement

from models.schema.base import Table
from utils.settings import redis


@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenAI - Model",
                values=[
                    "gpt-4o",
                    "gpt-3.5-turbo",
                    "gpt-3.5-turbo-16k",
                    "gpt-4",
                    "gpt-4-32k",
                ],
                initial_index=0,
            )
        ]
    ).send()
    await setup_agent(settings)


@cl.on_settings_update
async def setup_agent(settings):
    redis.set("openai_model", settings["Model"])


@cl.step(type="tool")
async def gen_query(human_query: str):
    current_step = cl.context.current_step
    current_step.name = "Generated SQL"
    current_step.show_input = False

    openai_client = OpenAIClientSingleton.get_async_client()
    model_settings = redis.get_all()

    udf_list = json.loads(model_settings.get("functions"))
    # TODO : create table list from UI
    table_list = [
        Table(table_name="agents", table_schema="public"),
        Table(table_name="calls", table_schema="public"),
        Table(table_name="transcript", table_schema="public"),
    ]
    create_table_statement = get_create_table_statement(table_list) or None
    sql_messages = prepare_sql_messages(human_query, create_table_statement, udf_list)
    settings = {
        "model": model_settings.get("openai_model"),
        "temperature": float(model_settings.get("temperature") or 1),
    }

    # Call OpenAI and stream the message
    stream_resp = await openai_client.chat.completions.create(
        messages=sql_messages, stream=True, **settings
    )
    async for part in stream_resp:
        token = part.choices[0].delta.content or ""
        if token:
            await current_step.stream_token(token)

    current_step.language = "sql"

    return current_step.output


@cl.step(type="tool")
async def execute_query(query):
    current_step = cl.context.current_step
    current_step.name = "Execute ThanoSQL"
    current_step.show_input = False

    try:
        query_log = thanosql_client.query.execute(query, max_results=10)
        results = query_log.records.to_df()
        markdown_table = results.to_markdown(index=False)
    except Exception as e:
        raise e

    current_step.output = markdown_table

    return query_log


@cl.step(type="tool")
async def analyze(query_log, human_query):
    openai_client = OpenAIClientSingleton.get_async_client()
    model_settings = redis.get_all()

    current_step = cl.context.current_step
    current_step.name = "Analyze Query Log"

    settings = {
        "model": model_settings.get("openai_model"),
        "temperature": float(model_settings.get("temperature") or 1),
    }

    messages = prepare_summary_messages(model_settings, query_log, human_query)

    final_answer = await cl.Message(content="").send()

    # Call OpenAI and stream the message
    stream = await openai_client.chat.completions.create(
        messages=messages, stream=True, **settings
    )
    async for part in stream:
        token = part.choices[0].delta.content or ""
        if token:
            await final_answer.stream_token(token)

    await final_answer.update()

    current_step.output = final_answer.content

    return current_step.output


@cl.step(type="run")
async def chain(human_query: str):
    sql_query = await gen_query(human_query)
    query_log = await execute_query(sql_query)
    analysis = await analyze(query_log, human_query)
    return analysis


@cl.on_message
async def main(message: cl.Message):
    await chain(message.content)


# @cl.on_message
# async def on_message(message: cl.Message):
#     client = OpenAIClientSingleton.get_async_client()
#     model_settings = redis_settings.get_all()
#     settings = {
#         "model": model_settings.get("openai_model"),
#         "temperature": float(model_settings.get("temperature") or 1)
#     }

#     response = await client.chat.completions.create(
#         messages=[
#             {
#                 "content": "You are a helpful bot, you always reply in Spanish",
#                 "role": "system"
#             },
#             {
#                 "content": message.content,
#                 "role": "user"
#             }
#         ],
#         stream=True,
#         **settings
#     )
#     final_answer = await cl.Message(content="").send()

#     async for part in response:
#         token = part.choices[0].delta.content or ""
#         if token:
#             await final_answer.stream_token(token)
#     await final_answer.update()
