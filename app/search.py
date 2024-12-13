from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from pyrfc import Connection
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataSearcher:
    def __init__(self, llm, collection_dict, connection, table_info, file_path, question):
        self.llm = llm
        self.collection_dict = collection_dict
        self.connection = connection
        self.table_info = table_info
        self.file_path = file_path
        self.question =question
    
    ## RDB
    def ask_need_gasrate(self, question):
        chat_prompt = PromptTemplate(template="""
            가스요금 단가표의 컬럼 관련 정보는 다음과 같습니다.
            <단가표 컬럼 정보>
            {table_info}
            </단가표 컬럼 정보>
            아래의 질문에 대한 답변을 할 때 가스요금 단가표가 필요할까요?
            Yes or No 로 답해주세요.
            <질문>
            {question}
            </질문>
        """,
        input_variables=['table_info', 'question'],
        )
        chain = chat_prompt | self.llm | StrOutputParser()
        return chain.invoke({'table_info': self.table_info, 'question': question})
    
    # 단가표 조회
    def search_gasrate(self, question):
        need_gasrate = self.ask_need_gasrate(question)
        if need_gasrate == 'Yes':
            query = self.ask_query(question)
            cursor = self.connection.cursor()
            cursor.execute(query)
            gasrate_info = cursor.fetchall()
            cursor.close()
            return {'source': 'RDB', 'content': gasrate_info}
        return None


    ## RAG
    def search_collection(self, question, collection_name):
        responses = self.collection_dict[collection_name].similarity_search(question, k=3)
        to_add = [f'<RAG {idx+1}>\n{response.page_content}' for idx, response in enumerate(responses)]
        return {'source': 'RAG', 'content': '\n'.join(to_add)}


    ## RFC
    # RFC 정보 추출
    def extract_rfc_info(self, group):
        df_rfc_info = pd.read_excel(self.file_path+'RFC/Function Call 명세서_v1.5.xlsx')
        dfs = []
        for i in df_rfc_info.loc[df_rfc_info['문의유형(적용대상)_1'] == group]['Function Call  NO']:
            df_rfc_function_info = pd.read_excel(self.file_path+'RFC/rfc_function_info.xlsx', sheet_name=i[-2:])
            df_rfc_input = pd.read_excel(self.file_path+'RFC/rfc_input.xlsx', sheet_name=i[-2:])
            df_rfc_output = pd.read_excel(self.file_path+'RFC/rfc_output.xlsx', sheet_name=i[-2:])
            dfs.append([df_rfc_function_info, df_rfc_input, df_rfc_output])
        return dfs

    # RFC 필요 확인
    def ask_need_rfc(self, rfc_info, question):
        chat_prompt = PromptTemplate(template=f"""
            Information about RFC and question are as follows.
            Check if the question needs to call RFC and you can find appropiate input parameters from the question.
            'I_VKONT''s type is string but NEVER contain any characters except numbers.
            If it needs and you can find appropiate input parameters) from question, return only input parameters in JSON format without explanation.
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

        chain = chat_prompt | self.llm | StrOutputParser()
        return chain.invoke({})

    # RFC 호출
    def rfc_call(self, name, input_parameters):
        # Establish the connection
        rfc_user="IF_RFC01"
        rfc_passwd="3002RFC01"
        rfc_conn = Connection(
            user=rfc_user,
            passwd=rfc_passwd,
            ashost="vhsmyepqci.tyo2.hec.samchully.co.kr",  # Application server host
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

   
    def search_rfc(self, question, group):
        try:
            rfc_info = self.extract_rfc_info(group)
            for dfs in rfc_info:
                rfc_param = self.ask_need_rfc(dfs, question)
                if rfc_param != 'No':
                    rfc_param = json.loads(rfc_param[rfc_param.find('{'):rfc_param.rfind('}')+1])
                    rfc_name = dfs[0]['RFC Function 명'].values[0]
                    rfc_result = self.rfc_call(rfc_name, rfc_param)
                    rfc_summary = self.answer_by_rfc(rfc_result, rfc_param, dfs[1], dfs[2], question)
                    return {'source': 'RFC', 'content': rfc_summary}
        except Exception as e:
            logger.error(f'RFC error: {e}')
        return None