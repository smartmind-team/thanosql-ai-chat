gasrate_prompt = """
가스요금 단가표의 컬럼 관련 정보는 다음과 같습니다.
<단가표 컬럼 정보>
{table_info}
</단가표 컬럼 정보>
아래의 질문에 대한 답변을 할 때 가스요금 단가표가 필요할까요?
Yes or No 로 답해주세요.
<질문>
{question}
</질문>
"""

need_rfc_prompt = """
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
{rfc_info[2]}
</output_info>
</RFC info>
<question>
{question}
</question>
        """