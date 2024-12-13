from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QuestionAnalyzer:
    def __init__(self, llm):
        self.llm = llm

    def check_general_chat(self, question):
        word_list = ', '.join(['납부자 번호', '고객 번호', '공급규정', '요금문의', '전출입', 'AS', '납부방법', '경감관리', '명의변경', '고지방법', '안전점검', '공급중단', '검침관리', '계량기'])
        check_general_prompt = PromptTemplate(template=f"""
            Determine whether the user's question is related to gas company customer service or is a general chat question unrelated to the gas company.
            - Respond with "yes" if the question is general (not related to gas company services).
            - Respond with "no" if the question involves gas company-specific topics, such as billing, service requests, or any of the specific terms listed below.
            
            Provide the binary score as a JSON with a single key 'result' and no premable or explaination.

            <specific terms>
            {word_list}
            </specific terms>
            
            <question>
            {question}
            </question>
        """)
        check_general_chain = check_general_prompt | self.llm | JsonOutputParser()
        return check_general_chain.invoke({})

    async def response_general_chat(self, question):
        general_chat_prompt = PromptTemplate(template=f"""
            You are a helpful and polite assistant. Respond to the user's question in a concise and clear manner.
            - Be friendly and respectful in tone.
            - Keep your response short, yet informative.

            <question>
            {question}
            </question>
        """)
        general_chat_chain = general_chat_prompt | self.llm | StrOutputParser()
        
        async for event in general_chat_chain.astream_events({}, version="v2"):
            if event['event'] == 'on_chat_model_stream':
                yield event['data']['chunk'].content
    
    def check_new_question(self, question, history_list=[]):
        history = '\n'.join(history_list)
        check_new_prompt = PromptTemplate(template=f"""
            Analyze the chat history and determine if the user's question is related to any of the previous messages.
            - Respond with "yes" if the question introduces a new, unrelated topic (new question).
            - Respond with "no" if the question is connected to, builds upon, or continues the context of the chat history (related to history).

            Provide the result as a JSON object with a single key 'result' and no additional explanation or text.

            <chat history>
            {history}
            </chat history>

            <question>
            {question}
            </question>
        """)
        check_new_chain = check_new_prompt | self.llm | JsonOutputParser()
        return check_new_chain.invoke({})

    def classify_question(self, question, collection_dict):
        result = collection_dict['QC'].similarity_search(question, k=1)
        return result[0].metadata['group']