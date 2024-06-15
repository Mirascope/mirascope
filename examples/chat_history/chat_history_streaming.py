"""
The same chat_history_librarian example but with streaming instead of call.
"""

import os

from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall, OpenAIStream

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


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
    if librarian.question == "exit":
        break
    stream = OpenAIStream(librarian.stream())
    print("(Assistant): ", end="")
    for chunk, tool in stream:
        if chunk.user_message_param:
            print(chunk.content, end="", flush=True)
    print()
    if stream.user_message_param:
        librarian.history.append(stream.user_message_param)
    librarian.history.append(stream.message_param)

# > (User): What fantasy book should I read?
# > (Assistant): Have you read the Name of the Wind?
# > (User): I have! What do you like about it?
# > (Assistant): I love the intricate world-building...
