rag_prompt = """
Answer to the question using the information in RAG_result in Korean.
RAG is Retrieval Augmented Generation.
Today is {today}.
<RAG_result>
{result}
</RAG_result>
<question>
{question}
</question>
"""

rdb_prompt = """
Answer to the question using the information in RDB_result in Korean.
RDB is Relational Database.
Today is {today}.
<RDB_result>
{result}
</RDB_result>
<question>
{question}
</question>
"""

rfc_prompt = """
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
"""

eval_search_prompt = """
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
"""

answer_prompt = """
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
"""