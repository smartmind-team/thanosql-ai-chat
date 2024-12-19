import json
from datetime import datetime

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from models import schema
from modules.chatbot.answer import AnswerGenerator
from modules.chatbot.question import QuestionAnalyzer
from modules.chatbot.search import DataSearcher
from modules.database import pg
from utils import logger, settings

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
table_info = json.load(open(FILE_PATH + "chatbot/table_dict.json"))

# 유형그룹(GROUP) 11개
class_group_list = settings.app.system_tags

# 컬렉션 사전
collection_dict = dict()
embeddings = OpenAIEmbeddings(model=settings.openai.embedding_model)
for name in class_group_list:
    collection_dict[name] = pg.load_vector(embeddings, name)
collection_dict["공급규정"] = pg.load_vector(embeddings, "공급규정")
collection_dict["이지원"] = pg.load_vector(embeddings, "이지원")
collection_dict["QC"] = pg.load_vector(embeddings, "QC")


async def chatbot(request: schema.chat.ChatRequest):
    log_msg = "Collection Dict keys:"
    for key in collection_dict.keys():
        log_msg += f"\n   - {key}"
    logger.debug(log_msg)
    try:
        logger.debug("Start chatbot process")
        question = request.messages[-1]["content"]
        tags = request.tag
        log_object = schema.chat.ChatLogSchema(
            session_id=request.session_id,
            message_id=request.messages[-1]["id"],
            question=question,
            validate_tag="user" if request.tag else "agent",
        )
        logger.debug(
            "Received Chat Request:"
            + f"\n   - question: {question}"
            + f"\n   - tags: {tags}"
        )

        question_analyzer = QuestionAnalyzer(llm=llm)
        data_searcher = DataSearcher(
            llm=llm,
            collection_dict=collection_dict,
            connection=pg.vector_conn,
            table_info=table_info,
            file_path=FILE_PATH,
            question=question,
        )
        answer_generator = AnswerGenerator(llm=llm, question=question)
        logger.debug("Prepared agents")

        if tags == ["이지원"]:
            result = collection_dict["이지원"].similarity_search(question, k=1)
            image_path = result[0].metadata["image_path"]
            easyone_result = f'{result[0].page_content} <img src="{image_path}" alt="이지원 설명입니다"/>'
            logger.debug(f"easyone_result: {easyone_result}")
            yield f"0:{json.dumps(easyone_result)}\n"
            yield f"8:[{json.dumps(json.loads(log_object.model_dump_json()))}]\n"
        else:
            log_object.history = [
                request.messages[i * (-2) - 1]["content"]
                for i in range(1, settings.app.max_memory)
                if len(request.messages) > i * 2
            ]

            if tags:
                group = tags
            else:
                group = question_analyzer.classify_question(question, collection_dict)
            logger.debug(f"Group: {group}")

            # 참고 자료 조회
            references = []
            if group == "요금문의":
                response = data_searcher.ask_need_gasrate(question)
                logger.debug(f"Need gas rate Response: {response}")
                if response != "No":  # response == "Yes"
                    gasrate_info = pg.execute(response[response.find("s") : -3])
                    references.append(
                        {
                            "source": "RDB",
                            "raw_content": gasrate_info,
                            "content": gasrate_info,
                        }
                    )
                    log_object.validate_rdb = True
                    log_object.query = response
                    log_object.rdb = str(gasrate_info)

            rfc_info = data_searcher.extract_rfc_info(group)
            for dfs in rfc_info:
                rfc_param = data_searcher.ask_need_rfc(rfc_info=dfs, question=question)
                yield f'0:{json.dumps("RFC 정보 추출 중입니다.")}\n'
                logger.info(f"RFC Param: {rfc_param}")
                if rfc_param != "No":
                    rfc_param = json.loads(
                        rfc_param[rfc_param.find("{") : rfc_param.rfind("}") + 1]
                    )
                    rfc_num = dfs[0]["Function Call No"].values[0][-2:]
                    rfc_name = dfs[0]["RFC Function 명"].values[0]
                    logger.info(f"RFC Num: {rfc_num}, RFC Name: {rfc_name}")
                    logger.info(f"RFC Param: {rfc_param}")

                    rfc_result = await data_searcher.search_rfc_result(
                        rfc_num, rfc_name, rfc_param
                    )
                    logger.info(f"RFC Result: {rfc_result}")

                    rfc_summary = data_searcher.summarize_rfc(
                        rfc_result, rfc_param, dfs[1], dfs[2], question
                    )
                    logger.info(f"RFC Summary: {rfc_summary}")
                    log_object.validate_rfc = True
                    log_object.rfc = str(rfc_result)

                    yield f"0:{json.dumps(rfc_summary)}\n"
                    yield f"8:[{json.dumps(json.loads(log_object.model_dump_json()))}]\n"
                    raise StopAsyncIteration

            yield f'0:{json.dumps("RAG 정보 추출 중입니다.")}\n'
            retrieval_result = data_searcher.search_collection(
                question, collection_name=group
            )
            logger.info(f"Retrieval Result: {retrieval_result}")
            rag_answer = answer_generator.answer_by_rag(retrieval_result)
            references.append(
                {
                    "source": "RAG",
                    "raw_content": retrieval_result,
                    "content": rag_answer,
                    "valid": True,
                }
            )
            log_object.validate_rag = True
            log_object.rag = retrieval_result

            answer_references = [f"{i['source']}: {i['content']}" for i in references]
            logger.info(f"answer_references: {answer_references}")
            answer_chain = answer_generator.get_answer_chain(references)
            answer = ""

            async for event in answer_chain.astream_events(
                {
                    "today": datetime.now().strftime("%Y-%m-%d"),
                    "references": references,
                    "question": question,
                },
                version="v2",
            ):
                if event["event"] == "on_chat_model_stream":
                    answer += event["data"]["chunk"].content
                    yield f"0:{json.dumps(event['data']['chunk'].content)}\n"
            log_object.tag = group
            log_object.response = answer
            yield f"8:[{json.dumps(json.loads(log_object.model_dump_json()))}]\n"
    except Exception as e:
        logger.error(f"chatbot error: {e}")
        yield "0:Something went wrong in chatbot\n"
        yield "8:[]"

    #         dict_front = {"context_easyone": result[0].metadata["image_path"]}
    #         logger.debug(f"dict_front: {dict_front}")
    #         # yield {
    #         #     "annotations": [dict_front],
    #         #     "content": "이지원 설명입니다"
    #         #     + '<img src="'
    #         #     + dict_front["context_easyone"]
    #         #     + '" alt="이지원 설명입니다">',
    #         # }

    #     # 일상대화 체크
    #     general_chat = question_analyzer.check_general_chat(question)
    #     if general_chat.get("result") == "yes":
    #         logger.info(f"Received General Chat Request: {question}")
    #         response = await question_analyzer.response_general_chat(question)
    #         logger.debug(f"Generated Response: {response}")
    #         yield {"response": response, "annotations": []}
    #     logger.info(f"Received Chat Request: {question}")

    #     # 이전 대화 히스토리 확인
    #     history_list = [
    #         request.messages[i * (-2) - 1]["content"]
    #         for i in range(1, settings.app.max_memory)
    #         if len(request.messages) > i * 2
    #     ]

    #     dict_front = None
    #     if not tags:
    #         groups = [question_analyzer.classify_question(question, collection_dict)]
    #     elif tags == ["이지원"]:
    #         result = collection_dict["이지원"].similarity_search(question, k=1)
    #         dict_front = {"context_easyone": result[0].metadata["image_path"]}
    #         logger.debug(f"dict_front: {dict_front}")
    #         yield {
    #             "annotations": [dict_front],
    #             "content": "이지원 설명입니다"
    #             + '<img src="'
    #             + dict_front["context_easyone"]
    #             + '" alt="이지원 설명입니다">',
    #         }
    #     else:
    #         groups = tags
    #         # 참고 자료 조회
    #         raw_references = []
    #         for group in groups:
    #             if group == "요금문의":
    #                 gasrate_ref = await data_searcher.search_gasrate(question)
    #                 if gasrate_ref == "Yes":
    #                     raw_references.append({"source": "RDB", "content": gasrate_ref})
    #                 else:
    #                     raw_references.append({"source": "RDB", "content": ""})

    #             rag_ref = await data_searcher.search_collection(question, group)
    #             raw_references.append({"source": "RAG", "content": rag_ref})

    #             rfc_ref = await data_searcher.search_rfc(question, group)
    #             if rfc_ref:
    #                 raw_references.append({"source": "RFC", "content": rfc_ref})

    #         # 답변 생성
    #         answer = await answer_generator.generate_answer(question, raw_references)
    #         logger.info(f"Generated Answer: {answer}")

    #         # insert_log()
    #         result = {
    #             "annotations": [dict_front] if dict_front else [],
    #             "content": answer,
    #         }
    #         logger.debug(f"Generated Result: {result}")

    #         yield result

    # except Exception as e:
    #     logger.error(f"chatbot error: {e}")
    #     return {"content": "Something went wrong in chatbot\n", "annotations": []}
