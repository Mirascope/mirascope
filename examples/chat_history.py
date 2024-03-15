"""
Our template parser makes inserting chat history beyond easy:
"""
from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall


class Librarian(OpenAICall):
    prompt_template = """
	SYSTEM: You are the world's greatest librarian.
	MESSAGES: {history}
	USER: {question}
	"""

    question: str
    history: list[ChatCompletionMessageParam] = []


librarian = Librarian(question="", history=[])
while True:
    librarian.question = input("(User): ")
    response = librarian.call()
    librarian.history.append({"role": "user", "content": librarian.question})
    librarian.history.append({"role": "assistant", "content": response.content})
    print(f"(Assistant): {response.content}")

# > (User): What fantasy book should I read?
# > (Assistant): Have you read the Name of the Wind?
# > (User): I have! What do you like about it?
# > (Assistant): I love the intricate world-building...
