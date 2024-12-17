import sys
import json
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

sys.path.append(Path(__file__).parents[3])
from utils import settings
from utils.logger import logger
from modules.database import pg
from modules.chatbot.question import QuestionAnalyzer
from modules.chatbot.answer import AnswerGenerator
from modules.chatbot.search import DataSearcher

from log import insert_log


llm = ChatOpenAI(
    model=settings.openai.model,
    # temperature=settings.app.default_temperature,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=settings.app.max_retries,
    api_key=settings.openai.api_key,
    streaming=True,
    openai_api_base=settings.openai.base_url,
)
# 단가표 설명 정보
FILE_PATH = "data/"
table_info = json.load(open(FILE_PATH + "chatbot/table_dict.json", "r"))

# 유형그룹(GROUP) 11개
class_group_list = settings.AppSetting.system_tags

# 컬렉션 사전
collection_dict = dict()
embeddings = OpenAIEmbeddings(model=settings.openai.embedding_model)
for name in class_group_list:
    collection_dict[name] = pg.load_vector(embeddings, name)
collection_dict["공급규정"] = pg.load_vector(embeddings, "공급규정")
collection_dict["이지원"] = pg.load_vector(embeddings, "이지원")
collection_dict["QC"] = pg.load_vector(embeddings, "QC")


def chatbot(request):
    try:
        question = request.messages[-1]["content"]
        tags = request.tag_list

        question_analyzer = QuestionAnalyzer(llm)
        data_searcher = DataSearcher(
            llm, collection_dict, connection, table_info, file_path
        )
        answer_generator = AnswerGenerator(llm)

        # 일상대화 체크
        general_chat = question_analyzer.check_general_chat(question)
        if general_chat.get("result") == "yes":
            response = question_analyzer.response_general_chat(question)
            return {"response": response, "annotations": []}

        # 이전 대화 히스토리 확인
        history_list = [
            request.messages[i * (-2) - 1]["content"]
            for i in range(1, settings.app.max_memory)
            if len(request.messages) > i * 2
        ]

        if not tags:
            groups = [question_analyzer.classify_question(question, collection_dict)]
        # 이지원 태그일 때
        elif tags == ["이지원"]:
            result = collection_dict["이지원"].similarity_search(question, k=1)
            dict_front = {"context_easyone": result[0].metadata["image_path"]}
            logger.info(f"dict_front: {dict_front}")
            yield {
                "annotations": [dict_front],
                "content": "이지원 설명입니다"
                + '<img src="'
                + dict_front["context_easyone"]
                + '" alt="이지원 설명입니다">',
            }

        else:
            groups = tags
            # 참고 자료 조회
            raw_references = []
            for group in groups:
                if group == "요금문의":
                    gasrate_ref = data_searcher.search_gasrate(question)
                    if gasrate_ref == "Yes":
                        raw_references.append({"source": "RDB", "content": gasrate_ref})
                    else:
                        raw_references.append({"source": "RDB", "content": ""})

                rag_ref = data_searcher.search_collection(question, group)
                raw_references.append({"source": "RAG", "content": rag_ref})

                rfc_ref = data_searcher.search_rfc(question, group)
                if rfc_ref:
                    raw_references.append({"source": "RFC", "content": rfc_ref})

            # 답변 생성
            answer = answer_generator.generate_answer(question, raw_references)

            insert_log()

            return {"annotations": [dict_front], "content": answer}

    except Exception as e:
        logger.error(f"chatbot error: {e}")
        return {"content": "Something went wrong in chatbot\n", "annotations": []}
