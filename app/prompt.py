user_prompt_generate_message_title = """
Following the guidelines below, summarize the following this sentence `{question}` into 5 words or less.

#### Guidelines
1. Start with a gerund (verb ending in -ing) when possible.
2. Capitalize each word.
3. Use formal, descriptive language.
4. Utilize words from the original question as much as possible.
5. If the sentence is already 5 words or fewer, simply adjust it to ensure grammatical correctness without changing its meaning.
"""

system_prompt_generate_sql = """
### Task
Provide only PostgreSQL syntax to answer the given message or content.
SQL MUST NOT include columns that are not requested in questions.
Use user defined functions when necessary.
Provide only PostgreSQL syntax. Include explanatory comments within the SQL code if needed for clarity.
DO NOT use markdown format, just return SQL syntax with comments only.

IMPORTANT NOTE: you can use specialized pgvector syntax (`<->`) to do nearest \
neighbors/semantic search to a given vector from an embeddings column in the table. \
The embeddings value for a given row typically represents the semantic meaning of that row. \
The vector represents an embedding representation \
of the question, given below. Do NOT fill in the vector values directly, but rather specify a \
`[query_vector]` placeholder. For instance, some select statement examples below \
(the name of the embeddings column is `embedding`):
SELECT * FROM items ORDER BY embedding <-> '[query_vector]' LIMIT 5;
SELECT * FROM items WHERE id != 1 ORDER BY embedding <-> (SELECT embedding FROM items WHERE id = 1) LIMIT 5;
SELECT * FROM items WHERE embedding <-> '[query_vector]' < 5;

### Database Schema
The query will run on a database with the following schema:
{create_table_statement}

### Available User Defined Functions
{udf_list}

### Answer
"""

system_prompt_generate_query_result_summary = """
{system_prompt}

### Task
Analyze and explain the provided Query Log, which represents a database operation log. Include details about:

1. query_id: A unique identifier for the query
2. statement_type: The type of SQL statement executed
3. start_time and end_time: Timestamps for query execution
4. query: The actual SQL query executed
5. referer: The source of the query request
6. state: The status of the query execution
7. destination_table_name and destination_schema: Information about where results are stored
8. error_result: Any error messages (if applicable)
9. created_at: Timestamp of when the query was created
10. records: Contains the actual data returned by the query.
    - data: An array of objects, each containing a 'title' field
    - total: The total number of records returned

Your task is to analyze this log and provide a friendly, conversational summary of the 'records' section within 500 characters.

The 'records' section is a preview of up to 10 rows the raw data, so do not imply or state that you have a specific number of data available. Simply present the data you see without referring to the how many there are.
Your response should directly address the user's question.
DO NOT mention that you are referencing any log or database in your response.
Organize results using bullet points or numbering when applicable.

IMPORTANT: If there is an error_result in the log, you should provide a general response indicating that there was an issue retrieving the information, without going into technical details.
Also explain that it shows a summarized view of the data rather than the full dataset. Emphasize that this summary provides an overview of key information and trends without displaying every individual record.

### Query Log
{query_log}

### Answer
"""
