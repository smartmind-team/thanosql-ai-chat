import sys
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

sys.path.append(Path(__file__).parents[1])
from utils.logger import logger
from resource import prompt


class AnswerGenerator:
    def __init__(self, llm: ChatOpenAI, question: str):
        self.llm = llm
        self.question = question

    # RAG 결과 하나로 답변
    def answer_by_rag(self, result: str) -> str:
        chat_prompt = PromptTemplate(template=prompt.rag_prompt)
        chain = chat_prompt | self.llm | StrOutputParser()
        return chain.invoke(
            {
                "today": datetime.now().strftime("%Y-%m-%d"),
                "result": result,
                "question": self.question,
            }
        )

    # RDB 결과 하나로 답변
    def answer_by_rdb(self, result: str) -> str:
        chat_prompt = PromptTemplate(template=prompt.rdb_prompt)
        chain = chat_prompt | self.llm | StrOutputParser()
        return chain.invoke(
            {
                "today": datetime.now().strftime("%Y-%m-%d"),
                "result": result,
                "question": self.question,
            }
        )

    # rfc 결과 하나로 답변
    def answer_by_rfc(
        self, result: str, rfc_input: str, input_info: str, output_info: str
    ) -> str:
        chat_prompt = PromptTemplate(
            template=prompt.rfc_prompt,
            input_variables=[
                "today",
                "result",
                "rfc_input",
                "input_info",
                "output_info",
                "question",
            ],
        )
        chain = chat_prompt | self.llm | StrOutputParser()
        return chain.invoke(
            {
                "today": datetime.now().strftime("%Y-%m-%d"),
                "result": result,
                "rfc_input": rfc_input,
                "input_info": input_info[["변수명", "설명"]],
                "output_info": output_info[["변수명", "설명", "비고"]],
                "question": self.question,
            }
        )

    # 검색 결과 평가
    def evaluate_search(self, response: str) -> str:
        chat_prompt = PromptTemplate(
            template=prompt.eval_search_prompt,
            input_variables=["question", "response"],
        )
        chain = chat_prompt | self.llm | JsonOutputParser()
        return chain.invoke({"question": self.question, "response": response})

    async def generate_answer(self, references: list) -> str:
        chat_prompt = PromptTemplate(template=prompt.answer_prompt)
        chain = chat_prompt | self.llm | StrOutputParser()
        async for event in chain.astream_events(
            {
                "today": datetime.now().strftime("%Y-%m-%d"),
                "question": self.question,
                "references": "\n".join(
                    [f"{i['source']}: {i['content']}" for i in references]
                ),
            },
            version="v2",
        ):
            yield event["data"]["chunk"].content
