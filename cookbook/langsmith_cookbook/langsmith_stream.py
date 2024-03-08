"""LangSmith + Mirascope example of streaming OpenAI chat with history."""
import os

from langsmith import wrappers
from langsmith_config import Settings
from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICallParams, OpenAIPrompt

settings = Settings()

os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class Chat(OpenAIPrompt):
    """A chat with history"""

    message: str
    history: list[ChatCompletionMessageParam] = []

    call_params = OpenAICallParams(model="gpt-3.5-turbo", wrapper=wrappers.wrap_openai)

    @property
    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            {"role": "system", "content": "You are a helpful AI."},
            *self.history,
            {"role": "user", "content": f"{self.message}"},
        ]


first_message = "Hi there"
chat = Chat(message=first_message)
conversation_id = "101e8e66-9c68-4858-a1b4-3b0e3c51a934"
stream = chat.stream(
    langsmith_extra={"metadata": {"conversation_id": conversation_id}},
)
response = ""
for chunk in stream:
    print(chunk, end="")
    response += str(chunk)

chat_history: list[ChatCompletionMessageParam] = []
print()
chat_history.extend(
    [
        {"role": "user", "content": first_message},
        {"role": "assistant", "content": response},
    ]
)

# ... Next message comes in
second_message = "I don't need much assistance, actually."

chat.message = second_message
chat.history = chat_history

stream2 = chat.stream(
    langsmith_extra={"metadata": {"conversation_id": conversation_id}},
)
for chunk in stream2:
    print(chunk, end="")
    response += str(chunk)
