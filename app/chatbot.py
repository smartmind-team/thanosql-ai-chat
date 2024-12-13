from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from pyrfc import Connection
import os
import json
import pandas as pd
import logging
from datetime import datetime
from chat_schema import log_schema
from log import insert_log
from dataclasses import dataclass
import psycopg2

logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = "sk-7hXELHYh5gZHtW7rA5A-h-RK6VbYykHtGbg87rFtKWT3BlbkFJ5bRF-BGffBWYjerh-IfMpSFp_htRmcaFYPPgzPw08A"
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# client = ThanoSQL(
#     api_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3b3Jrc3BhY2VfaWQiOjEsImV4cCI6OTIyMzM3MTk3NDcxOTE3OTAwMCwidG9rZW5faWQiOiI3MmI3Yjk1YXNmZTMzOTQyODlhMyJ9.QI_8riETPk7b3a8zGaiLckU4a9pSRzCcKxHI-pSvTUY",
#     engine_url="http://gateway:8000"
# )
connection = "postgresql+psycopg://thanosql_user:thanosql@18.119.33.153:8821/default_database"
api_url = "http://192.168.10.1:8827/v1"
llm = ChatOpenAI(
    # model="/vllm-workspace/model/Linkbricks-Horizon-AI-Korean-llama-3.1-sft-dpo-8B",
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # api_key='EMPTY',
    # openai_api_base = api_url,
    # streaming=True,
    api_key='sk-7hXELHYh5gZHtW7rA5A-h-RK6VbYykHtGbg87rFtKWT3BlbkFJ5bRF-BGffBWYjerh-IfMpSFp_htRmcaFYPPgzPw08A'
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

# 일상대화인지 확인
def check_general_chat(question):
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
    check_general_chain = check_general_prompt | llm | JsonOutputParser()
    return check_general_chain.invoke({})

def response_general_chat(question):
    general_chat_prompt = PromptTemplate(template=f"""
        You are a helpful and polite assistant. Respond to the user's question in a concise and clear manner.
        - Be friendly and respectful in tone.
        - Keep your response short, yet informative.

        <question>
        {question}
        </question>
    """)
    chain = general_chat_prompt | llm | StrOutputParser()
    
    return chain.invoke({'question': question})

# 새 질문인지 전 질문에 추가질문인지 확인
def check_new_question(question,history_list=[]):
    history = '\n'.join(history_list)
    chat_prompt = PromptTemplate(template=f"""
                Chat history is as follows. Return Yes or No about if the question is new question or not(Yes: new question, No: relevant to history).
                <history>
                {history}
                </history>
                <question>
                {question}
                </question>
            """,
    )
    chain = chat_prompt | llm | StrOutputParser()
    return chain.invoke({})

# QC
def classify_question(question):
    result = collection_dict['QC'].similarity_search(question, k=1)
    group = result[0].metadata['group']
    return group

# RAG 결과 하나로 답변
def answer_by_rag(result, question):
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
    chain = chat_prompt | llm | StrOutputParser()
    return chain.invoke({'today': datetime.now().strftime('%Y-%m-%d'), 'result': result, 'question': question})


# 조회 결과 평가
def evaluate_search(result, question):
    chat_prompt = PromptTemplate(template="""
            Evaluate the result below.
            If the result is not relavant to the question, return only "No".
            If the result is relavant to the question, return only "Yes".
            <question>
            {question}
            </question>
            <result>
            {result}
            </result>
        """,
        input_variables=['question', 'result'],
        )
    chain = chat_prompt | llm | StrOutputParser()
    return chain.invoke({'question': question, 'result': result})

def ask_gasrate(question):
    # 이번 달 사용량에 대한 요금이 궁금합니다. Yes
    # 이번 달 요금이 많이 나온 거 같은데 그 이유가 뭘까요? No
    # 이번 달 사용량이 800m3 이네요. 이번 달 요금이 많이 나온 거 같은데 그 이유가 뭘까요? Yes
    chat_prompt = PromptTemplate(template="""
            가스요금 단가표의 컬럼 관련 정보는 다음과 같습니다.
            아래의 질문에 대한 답변을 할 때 가스요금 단가표가 필요할까요?
            - 필요하다면 단가표 컬럼 정보를 활용해서 아래의 질문에 대한 답변을 할 때 필요한 POSTGRESQL 쿼리만을 출력해주세요. 반드시 쿼리만 출력해주세요.
            - 필요하지 않다면 No 만 출력해주세요.
            <단가표 컬럼 정보>
            {table_info}
            </단가표 컬럼 정보> 
            <질문>
            {question}
            </질문>
        """,
        input_variables=['table_info', 'question'],
    )
    logger.info(f'gasrate_table_info: {table_info}')
    chain = chat_prompt | llm | StrOutputParser()
    return chain.invoke({'table_info': table_info, 'question': question})

# def ask_query(question):
#     chat_prompt = PromptTemplate(template="""
#         가스요금 단가표의 컬럼 관련 정보는 다음과 같습니다.
#         단가표 컬럼 정보를 활용해서 아래의 질문에 대한 답변을 할 때 필요한 POSTGRESQL 쿼리를 생성해주세요.(오직 쿼리만 출력)
#         <단가표 컬럼 정보>
#         {table_info}
#         </단가표 컬럼 정보>
#         <질문>
#         {question}
#         </질문>
#     """,
#     input_variables=["table_info", "question"],
#     )
#     chain = chat_prompt | llm | StrOutputParser()
#     return chain.invoke({"table_info": table_info, "question": question})

def search_collection(question, collection_name):
    responses = collection_dict[collection_name].similarity_search(question, k=3)
    to_add = []
    for idx, response in enumerate(responses):
        to_add.append(response.page_content)
    return to_add


## RFC
# RFC 정보 추출
def extract_rfc_info(group):
    df_rfc_info = pd.read_excel(file_path+'RFC/Function Call 명세서_v1.5.xlsx')
    dfs = []
    for i in df_rfc_info.loc[df_rfc_info['문의유형(적용대상)_1'] == group]['Function Call  NO']:
        df_rfc_function_info = pd.read_excel(file_path+'RFC/rfc_function_info.xlsx', sheet_name=i[-2:])
        df_rfc_input = pd.read_excel(file_path+'RFC/rfc_input.xlsx', sheet_name=i[-2:])
        df_rfc_output = pd.read_excel(file_path+'RFC/rfc_output.xlsx', sheet_name=i[-2:])
        dfs.append([df_rfc_function_info, df_rfc_input, df_rfc_output])
    return dfs

# RFC 필요 확인
def ask_need_rfc(rfc_info, question):
    chat_prompt = PromptTemplate(template=f"""
        Information about RFC and question are as follows.
        Check if the question needs to call RFC and you can find appropiate input parameters from the question.
        'I_VKONT''s type is string but NEVER contains any characters except numbers.
        If it needs and you can find appropiate input parameters from question, return only input parameters in JSON format without explanation.
        If it doesn't need or you can't find appropiate input parameters, return "No".
        <RFC info>
            <function_info>
            {rfc_info[0]}
            </function_info>
            <input_info>
            {rfc_info[1]}
            </input_info>
            <output_info>
            {rfc_info[2][['변수명', '설명']]}
            </output_info>
        </RFC info>
        <question>
        {question}
        </question>
    """,
    )

    chain = chat_prompt | llm | StrOutputParser()
    return chain.invoke({})

# RFC 호출
def rfc_call(name, input_parameters):
    # Establish the connection
    rfc_user="IF_RFC01"
    rfc_passwd="3002RFC01"
    rfc_conn = Connection(
        user=rfc_user,
        passwd=rfc_passwd,
        ashost="172.17.0.150",  # Application server host
        sysnr="00",  # System number
        client="100",  # Client number
        lang="KO"  # Language
    )

    # Call the RFC function
    try:
        result = rfc_conn.call(name, **input_parameters)
        logger.info(f'rfc_call result: {result}')
        return result
    except Exception as e:
        print(f"rfc_call error: {e}")

# RFC 결과 요약
def summarize_rfc(result, rfc_input, input_info, output_info, question):
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
    chain = chat_prompt | llm | StrOutputParser()
    return chain.invoke({'today': datetime.now().strftime('%Y-%m-%d'), 'result': result, 'rfc_input': rfc_input, 'input_info': input_info[['변수명', '설명']], 'output_info': output_info[['변수명', '설명', '비고']], 'question': question})

# 참고자료 바탕으로 LLM 질의
def chat_LLM(question, references):
    chat_prompt = PromptTemplate(template="""
        You are a helpful assistant for the city gas company, "삼천리," specializing in information about city gas or town gas services.
        Respond to the user's question using only the relevant and necessary information from the references provided below.
        - Do not include irrelevant details from the references.
        - If the answer to the question cannot be found in the references, politely state that you cannot answer the question.
        - Your response must be polite, concise, and entirely in Korean.

        Today is {today}.

        <references>
        {references}
        </references>

        <question>
        {question}
        </question>
    """,
    
    input_variables=['today', 'question', 'references'],
    )
    chain = chat_prompt | llm | StrOutputParser()
    return chain.invoke({'today': datetime.now().strftime('%Y-%m-%d'), 'references': references, 'question': question})


def chatbot(request):
    try:
        logger.info(f'request: {request}')
        question = request.messages[-1]['content']
        log_object = log_schema(
            session_id = request.session_id,
            message_id = request.messages[-1]['id'],
            question = question,
            tag = '',
            query = '',
            rdb = '',
            rag = [''],
            rfc = '',
            response = '',
            history = [''],
            validate_intention = 'new',
            validate_additional = 'no',
            validate_tag = 'user' if request.tag else 'agent',
            validate_rdb = False,
            validate_rag = False,
            validate_rfc = False,
        )
        tag = request.tag

        # async for event in chain.astream_events({"question": question}, version="v2"):
        #     if event['event'] == 'on_chat_model_stream':
        #         yield event['data']['chunk'].content

         # 이지원 전용 처리
        if tag == '이지원':
            result = collection_dict['이지원'].similarity_search(question, k=1)
            return {'annotations': [json.loads(log_object.model_dump_json())], 'content': result[0].page_content+'<img src="'+result[0].metadata['image_path']+'" alt="이지원 설명입니다">'}
        
        # No tag일 때,
        else:
            # 일상대화인지 확인
            is_general_chat = check_general_chat(question)
            logger.info(f'is_general_chat: {is_general_chat}')
            if is_general_chat.get("result") == 'yes':
                response = response_general_chat(question)
                logger.info(f'response: {response}')
                log_object.validate_intention = 'general'
                log_object.validate_additional = 'no'
                return {'content': response, 'annotations': [json.loads(log_object.model_dump_json())]}
            
            history_list = ['']
            # 새 질문인지 전 질문에 추가질문인지 확인
            if len(request.messages) != 1:
                for i in range(1,4):
                    try:
                        history_list.append(request.messages[i*(-2)-1]['id'])
                    except:
                        pass
            log_object.history = history_list
            # if len(history_list) > 0:
            #     is_new_question = check_new_question(question, history_list)
            
            if tag:
                group = tag
            else:
                group = classify_question(question)
            logger.info(f'group: {group}')

            # 참고 문서(VDB, RDB, RFC) 조회
            references = []
            # 요금문의일 때, 단가표 조회 여부 확인
            if group == '요금문의':
                response = ask_gasrate(question)
                logger.info(f'need_gasrate: {response}')
                if response != 'No':
                    # 단가표 조회하는 쿼리 생성하고 조회
                    rdb_connection = psycopg2.connect(host='18.119.33.153', dbname='default_database', user='thanosql_user', password='thanosql', port=8821)
                    cursor = rdb_connection.cursor()
                    cursor.execute(response[response.find('s'):-3])
                    gasrate_info = cursor.fetchall()
                    references.append({'source': 'RDB', 'raw_content': gasrate_info, 'content': gasrate_info})
                    logger.info(f'query: {response}')
                    cursor.close()
                    log_object.validate_rdb = True
                    log_object.query = response
                    log_object.rdb = str(gasrate_info)
                    # rdb_valid = evaluate_search(gasrate_info, question)
                    # if rdb_valid == 'Yes':
                    #     log_object.validate_rdb = True
                    #     log_object.query = response
                    #     log_object.rdb = gasrate_info
                    # else:
                    #     log_object.validate_rdb = False
                    #     log_object.query = ''
                    #     log_object.rdb = ''

            try:
                # RFC 호출
                rfc_info = extract_rfc_info(group)

                # dfs = [rfc_function_info, rfc_input_info, rfc_output_info]
                for dfs in rfc_info:
                    rfc_param = ask_need_rfc(dfs, question)
                    
                    if rfc_param != 'No':
                        rfc_param = json.loads(rfc_param[rfc_param.find('{'):rfc_param.rfind('}')+1])                    
                        rfc_num = dfs[0]['Function Call No'].values[0][-2:]
                        rfc_name = dfs[0]['RFC Function 명'].values[0]
                        logger.info(f'rfc_num: {rfc_num}, rfc_name: {rfc_name}')
                        logger.info(f'rfc_param: {rfc_param}')
                        rfc_result = rfc_call(rfc_name, rfc_param)
                        logger.info(f'rfc_output_info: {dfs[2]}')
                        rfc_summary = summarize_rfc(rfc_result, rfc_param, dfs[1], dfs[2], question)
                        logger.info(f'rfc_summary: {rfc_summary}')
                        # evaluation = evaluate_search(rfc_summary, question)
                        references.append({'source': 'RFC', 'raw_content': rfc_result, 'content': rfc_summary, 'valid': True})
                        log_object.validate_rfc = True
                        log_object.rfc = str(rfc_result)
                        try:
                            insert_log(log_object)
                        except Exception as e:
                            logger.error(f'insert_log error: {e}')
                        return {'content': rfc_summary, 'annotations': [json.loads(log_object.model_dump_json())]}
                        
                        
            except Exception:
                logger.error('RFC : RFC data is not provided')

            # Vector DB에서 조회
            retrieval_result = search_collection(question, group)
            logger.info(f'retrieval_result: {retrieval_result}')
            rag_answer = answer_by_rag(retrieval_result, question)
            # rag_valid = evaluate_search(rag_answer, question)
            references.append({'source': 'RAG', 'raw_content': retrieval_result, 'content': rag_answer, 'valid': True})
            log_object.validate_rag = True
            log_object.rag = retrieval_result
            # else:
            # if rag_valid == 'Yes':
            #     log_object.validate_rag = True
            #     log_object.rag = retrieval_result
            # else:
            #     log_object.validate_rag = False
            #     log_object.rag = ''

            answer_references = [f"{i['source']}: {i['content']}" for i in references]
            logger.info(f'answer_references: {answer_references}')            
            answer = chat_LLM(question, answer_references)
            log_object.tag = group
            log_object.response = answer
            # logger.info(f'answer: {answer}')
            logger.info(f'answer: {answer}')
            try:
                insert_log(log_object)
            except Exception as e:
                logger.error(f'insert_log error: {e}')
            return {'content': answer, 'annotations': [json.loads(log_object.model_dump_json())]}
                
    except Exception as e:
        logger.error(f'chatbot error: {e}')
        return {'content': 'Something went wrong in chatbot\n', 'annotations': []}
