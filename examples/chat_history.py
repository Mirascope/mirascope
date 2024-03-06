"""A basic example showcasing how to manually manage chat history."""
import os

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from mirascope import OpenAICallParams
from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class ChatPrompt(OpenAIPrompt):
    """A chat with history"""

    message: str
    history: list[ChatCompletionMessageParam] = []

    call_params = OpenAICallParams(model="gpt-3.5-turbo")

    @property
    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            ChatCompletionSystemMessageParam(
                role="system", content="You are a helpful AI."
            ),
            *self.history,
            ChatCompletionUserMessageParam(role="user", content=self.message),
        ]


prompt = ChatPrompt(message="")


def create_and_extend_history(prompt: ChatPrompt, message=str) -> str:
    """Create a message and extend the chat history."""
    prompt.message = message
    completion = prompt.create()
    prompt.history.extend(
        [
            ChatCompletionUserMessageParam(role="user", content=message),
            ChatCompletionAssistantMessageParam(
                role="assistant",
                content=str(completion),
            ),
        ]
    )
    return str(completion)


print(
    create_and_extend_history(
        prompt, "Hello, my favorite ice cream flavor is chocolate. What's yours?"
    )
)
print(
    create_and_extend_history(
        prompt,
        "I am forgetful and don't remember my favorite ice cream flavor."
        " Can you remind me?",
    )
)
print(
    create_and_extend_history(
        prompt,
        "What did I ask you about in my last question?",
    )
)

print(prompt.messages)
"""
output = [
    {"role": "system", "content": "You are a helpful AI."},
    {
        "role": "user",
        "content": "Hello, my favorite ice cream flavor is chocolate. What's yours?",
    },
    {
        "role": "assistant",
        "content": "As an AI, I don't have the ability to taste or enjoy food. However,
            many people enjoy chocolate ice cream just like you do! It's a classic
            favorite for many ice cream enthusiasts.",
    },
    {
        "role": "user",
        "content": "I am forgetful and don't remember my favorite ice cream flavor.
            Can you remind me?",
    },
    {
        "role": "assistant",
        "content": "Based on our previous conversation, your favorite ice cream flavor
            is chocolate! It's a popular choice, so you have great taste.",
    },
    {"role": "user", "content": "What did I ask you about in my last question?"},
    {
        "role": "assistant",
        "content": "In your last question, you mentioned that you are forgetful and
            asked me to remind you of your favorite ice cream flavor.",
    },
    {"role": "user", "content": "What did I ask you about in my last question?"},
]
"""
