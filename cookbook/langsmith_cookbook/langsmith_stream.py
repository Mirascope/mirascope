"""LangSmith + Mirascope example of streaming OpenAI chat with history."""
import os

from langsmith import wrappers
from langsmith_config import Settings

from mirascope import OpenAICallParams, OpenAIChat, Prompt
from mirascope.prompts.messages import Message

settings = Settings()

os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class ChatPrompt(Prompt):
    """A chat with history"""

    message: str
    history: list[Message] = []

    call_params = OpenAICallParams(model="gpt-3.5-turbo")

    @property
    def messages(self) -> list[Message]:
        return [
            {"role": "system", "content": "You are a helpful AI."},
            *self.history,
            {"role": "user", "content": f"{self.message}"},
        ]


class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str
    _call_params: OpenAICallParams = OpenAICallParams(model="gpt-3.5-turbo")


conversation_id = "101e8e66-9c68-4858-a1b4-3b0e3c51a934"
chat = OpenAIChat(client_wrapper=wrappers.wrap_openai)
first_message = "Hi there"
stream = chat.stream(
    ChatPrompt(message=first_message),
    langsmith_extra={"metadata": {"conversation_id": conversation_id}},
)
response = ""
for chunk in stream:
    print(chunk, end="")
    response += str(chunk)

chat_history: list[Message] = []
print()
chat_history.extend(
    [
        {"role": "user", "content": first_message},
        {"role": "assistant", "content": response},
    ]
)

# ... Next message comes in
second_message = "I don't need much assistance, actually."
stream2 = chat.stream(
    ChatPrompt(message=second_message, history=chat_history),
    langsmith_extra={"metadata": {"conversation_id": conversation_id}},
)
for chunk in stream2:
    print(chunk, end="")
    response += str(chunk)
