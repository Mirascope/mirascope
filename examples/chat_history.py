"""A basic example showcasing how to manually manage chat history.
NOTE: This example is now deprecated since chat completions are now done from the 
prompt itself. Will update."""

import os

from mirascope import BasePrompt, OpenAICallParams, OpenAIChat
from mirascope.base import Message

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class ChatPrompt(BasePrompt):
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


chat_history: list[Message] = []

chat = OpenAIChat()

first_message = "Hello, my favorite ice cream flavor is chocolate. What's yours?"

chat_history.extend(
    [
        {"role": "user", "content": first_message},
        {
            "role": "assistant",
            "content": str(chat.create(ChatPrompt(message=first_message))),
        },
    ]
)

second_message = (
    "I am forgetful and I don't remember my favorite ice cream flavor. "
    "Can you remind me?"
)

completion = chat.create(ChatPrompt(message=second_message, history=chat_history))
print(completion)
