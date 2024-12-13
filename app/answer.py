from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnswerGenerator:
    def __init__(self, llm, question):
        self.llm = llm
        self.question = question

    # RAG 결과 하나로 답변
    def answer_by_rag(self, result):
        chat_prompt = PromptTemplate(template="""
            Answer to the question using the information in RAG_result in Korean.
            RAG is Retrieval Augmented Generation.
            Today is {today}.
            <RAG_result>
            {result}
            </RAG_result>
            <question>
            {question}
            </question>
        """)
        chain = chat_prompt | self.llm | StrOutputParser()
        return chain.invoke({'today': datetime.now().strftime('%Y-%m-%d'), 'result': result, 'question': self.question})


    # RDB 결과 하나로 답변
    def answer_by_rdb(self, result):
        chat_prompt = PromptTemplate(template="""
            Answer to the question using the information in RDB_result in Korean.
            RDB is Relational Database.
            Today is {today}.
            <RDB_result>
            {result}
            </RDB_result>
            <question>
            {question}
            </question>
        """)
        chain = chat_prompt | self.llm | StrOutputParser()
        return chain.invoke({'today': datetime.now().strftime('%Y-%m-%d'), 'result': result, 'question': self.question})


    # rfc 결과 하나로 답변
    def answer_by_rfc(self, result, rfc_input, input_info, output_info):
        chat_prompt = PromptTemplate(template="""
            Answer to the question using the information in RFC_result in Korean.
            Use information about parameters in RFC_output_info to analyze the RFC_result.
            Today is {today}.
            <RFC_result>
            {result}
            </RFC_result>
            <RFC_input>
            {rfc_input}
            </RFC_input>
            <RFC_input_info>
            {input_info}
            </RFC_input_info>
            <RFC_output_info>
            {output_info}
            </RFC_output_info>
            <question>
            {question}
            </question>
            """,
            input_variables=['today', 'result', 'rfc_input', 'input_info', 'output_info', 'question'],
        )
        chain = chat_prompt | self.llm | StrOutputParser()
        return chain.invoke({'today': datetime.now().strftime('%Y-%m-%d'), 'result': result, 'rfc_input': rfc_input, 'input_info': input_info[['변수명', '설명']], 'output_info': output_info[['변수명', '설명', '비고']], 'question': self.question})

    # 검색 결과 평가
    def evaluate_search(self, response):
        chat_prompt = PromptTemplate(template="""
            Evaluate the response to the question below.
            If the response is not relavant to the question, return "No".
            If the response is relavant to the question, return "Yes".
            Provide the result as a JSON object with a single key 'result' and no additional explanation or text.
            <question>
            {question}
            </question>
            <response>
            {response}
            </response>
        """,
        input_variables=['question', 'response'],
        )
        chain = chat_prompt | self.llm | JsonOutputParser()
        return chain.invoke({'question': self.question, 'response': response})
    
    async def generate_answer(self, references):
        chat_prompt = PromptTemplate(template="""
            You are a helpful assistant of city gas company, "삼천리" specializing in information about city gas or town gas company.
            Answer the user's question JUST by using the references provided below. The answer should be nicely organized and the tone should be polite.
            If you can't find the answer from the reference, say you cannot answer to the question. The entire answer should be in Korean.
            Today is {today}.
            <references>
            {references}
            </references>
            <question>
            {question}
            </question>
        """)
        chain = chat_prompt | self.llm | StrOutputParser()
        async for event in chain.astream_events({
            'today': datetime.now().strftime('%Y-%m-%d'),
            'question': self.question,
            'references': '\n'.join([f"{i['source']}: {i['content']}" for i in references])
        }, version="v2"):
            yield event['data']['chunk'].content