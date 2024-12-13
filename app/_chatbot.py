from question import QuestionAnalyzer
from search import DataSearcher
from answer import AnswerGenerator
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_postgres.vectorstores import PGVector
from pyrfc import Connection
import os
import json
import pandas as pd
import logging
from datetime import datetime
from question import QuestionAnalyzer
from search import DataSearcher
from answer import AnswerGenerator
from log import insert_log
from chat_schema import log_schema, chat_schema


logger = logging.getLogger(__name__)
os.environ["OPENAI_API_KEY"] = "sk-7hXELHYh5gZHtW7rA5A-h-RK6VbYykHtGbg87rFtKWT3BlbkFJ5bRF-BGffBWYjerh-IfMpSFp_htRmcaFYPPgzPw08A"
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
connection = "postgresql+psycopg://thanosql_user:thanosql@18.119.33.153:8821/default_database"
api_url = "http://192.168.10.1:8827/v1"

llm = ChatOpenAI(
    model="/vllm-workspace/model/Linkbricks-Horizon-AI-Korean-llama-3.1-sft-dpo-8B",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key='EMPTY',
    streaming=True,
    openai_api_base = api_url,
)
# 단가표 설명 정보
file_path = "data/"
table_info = json.load(open(file_path+'chatbot/table_dict.json', 'r'))

# 유형그룹(GROUP) 11개
class_group_list = ['요금문의', '전출입, AS', '납부방법문의', '경감관리', '명의변경', '고지방법문의', '안전점검', '공급중단', '검침관리', '계량기', '기타문의']

# 컬렉션 사전
collection_dict = dict()
for name in class_group_list:
    collection_dict[name] = PGVector.from_existing_index(embedding=embeddings, collection_name=name, connection=connection)
collection_dict['공급규정'] = PGVector.from_existing_index(embedding=embeddings, collection_name='공급규정', connection=connection)
collection_dict['이지원'] = PGVector.from_existing_index(embedding=embeddings, collection_name='이지원', connection=connection)
collection_dict['QC'] = PGVector.from_existing_index(embedding=embeddings, collection_name='QC', connection=connection)


def chatbot(request):
    try:
        question = request.messages[-1]['content']
        tags = request.tag_list
        
        question_analyzer = QuestionAnalyzer(llm)
        data_searcher = DataSearcher(llm, collection_dict, connection, table_info, file_path)
        answer_generator = AnswerGenerator(llm)

        # 일상대화 체크
        general_chat = question_analyzer.check_general_chat(question)
        if general_chat.get('result') == 'yes':
            response = question_analyzer.response_general_chat(question)
            return {'response': response, 'annotations': []}

        # 이전 대화 히스토리 확인
        history_list = [request.messages[i*(-2)-1]['content'] for i in range(1,4) if len(request.messages) > i*2]
        
        if not tags:
            groups = [question_analyzer.classify_question(question, collection_dict)]
        # 이지원 태그일 때
        elif tags == ['이지원']:
            result = collection_dict['이지원'].similarity_search(question, k=1)
            dict_front = {'context_easyone': result[0].metadata['image_path']}
            logger.info(f'dict_front: {dict_front}')
            yield {'annotations': [dict_front], 'content': '이지원 설명입니다'+'<img src="'+dict_front['context_easyone']+'" alt="이지원 설명입니다">'}

        else:
            groups = tags
            # 참고 자료 조회
            raw_references = []
            for group in groups:
                if group == '요금문의':
                    gasrate_ref = data_searcher.search_gasrate(question)
                    if gasrate_ref=='Yes':
                        raw_references.append({'source': 'RDB', 'content': gasrate_ref})
                    else:
                        raw_references.append({'source': 'RDB', 'content': ''})
                
                rag_ref = data_searcher.search_collection(question, group)
                raw_references.append({'source': 'RAG', 'content': rag_ref})
                
                rfc_ref = data_searcher.search_rfc(question, group)
                if rfc_ref:
                    raw_references.append({'source': 'RFC', 'content': rfc_ref})
                
            # 답변 생성
            answer = answer_generator.generate_answer(question, raw_references)
            
            insert_log()
            
            return {'annotations': [dict_front], 'content': answer}

    except Exception as e:
        logger.error(f'chatbot error: {e}')
        return {'content': 'Something went wrong in chatbot\n', 'annotations': []}