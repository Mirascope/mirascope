from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    ChatCompletionsToolDefinition,
    ChatRequestMessage,
    FunctionDefinition,
)
from azure.core.credentials import AzureKeyCredential
from pydantic import BaseModel

client = ChatCompletionsClient(
    endpoint="YOUR_ENDPOINT", credential=AzureKeyCredential("YOUR_KEY")
)


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    completion = client.complete(
        model="gpt-4o-mini",
        messages=[ChatRequestMessage({"role": "user", "content": f"Extract {text}"})],
        tools=[
            ChatCompletionsToolDefinition(
                function=FunctionDefinition(
                    name="Book",
                    description="An extracted book.",
                    parameters={
                        "properties": {
                            "title": {"type": "string"},
                            "author": {"type": "string"},
                        },
                        "required": ["title", "author"],
                        "type": "object",
                    },
                )
            )
        ],
        tool_choices="required",
    )
    if tool_calls := completion.choices[0].message.tool_calls:
        return Book.model_validate_json(tool_calls[0].function.arguments)
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
