"""A basic example showcasing how to manually manage chat history."""
import os

from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICallParams, OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class ChatPrompt(OpenAIPrompt):
    """A chat with history"""

    message: str
    history: list[ChatCompletionMessageParam] = []

    call_params = OpenAICallParams(model="gpt-3.5-turbo")

    @property
    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            {"role": "system", "content": "You are a helpful AI."},
            *self.history,
            {"role": "user", "content": f"{self.message}"},
        ]


chat_history: list[ChatCompletionMessageParam] = []

first_message = "Hello, my favorite ice cream flavor is chocolate. What's yours?"

chat_history.extend(
    [
        {"role": "user", "content": first_message},
        {
            "role": "assistant",
            "content": str(ChatPrompt(message=first_message).create()),
        },
    ]
)

second_message = (
    "I am forgetful and I don't remember my favorite ice cream flavor. "
    "Can you remind me?"
)

completion = ChatPrompt(message=second_message, history=chat_history).create()
print(completion)
