import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from utils.logger import logger
from utils import settings
from data import prompt


class QuestionAnalyzer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def check_general_chat(self, question: str) -> dict:
        special_tags = ["납부자 번호", "고객 번호", "공급규정"]
        system_tags = [
            tag.replace("문의", "")
            for tag in settings.app.system_tags
            if tag != "기타문의"
        ]
        word_list = ", ".join(system_tags + special_tags)
        check_general_prompt = PromptTemplate(
            template=prompt.general_prompt.format_map(
                {"word_list": word_list, "question": question}
            )
        )
        check_general_chain = check_general_prompt | self.llm | JsonOutputParser()
        return check_general_chain.invoke({})

    async def response_general_chat(self, question: str) -> str:
        general_chat_prompt = PromptTemplate(
            template=prompt.general_chat_prompt.replace("{question}", question)
        )
        general_chat_chain = general_chat_prompt | self.llm | StrOutputParser()

        async for event in general_chat_chain.astream_events({}, version="v2"):
            if event["event"] == "on_chat_model_stream":
                yield event["data"]["chunk"].content

    def check_new_question(self, question: str, history_list: list = []) -> dict:
        history = "\n".join(history_list)
        check_new_prompt = PromptTemplate(
            template=prompt.check_new_prompt.replace("{history}", history).replace(
                "{question}", question
            )
        )
        check_new_chain = check_new_prompt | self.llm | JsonOutputParser()
        return check_new_chain.invoke({})

    def classify_question(self, question, collection_dict):
        result = collection_dict["QC"].similarity_search(question, k=1)
        return result[0].metadata["group"]
