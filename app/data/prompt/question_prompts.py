check_new_prompt = """
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
"""

general_chat_prompt = """
You are a helpful and polite assistant. Respond to the user's question in a concise and clear manner.
- Be friendly and respectful in tone.
- Keep your response short, yet informative.

<question>
{question}
</question>
"""

general_prompt = """
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
"""

