import json

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    ChatCompletionsToolDefinition,
    ChatRequestMessage,
    FunctionDefinition,
)
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint="YOUR_ENDPOINT", credential=AzureKeyCredential("YOUR_KEY")
)


def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


def identify_author(book: str) -> str:
    completion = client.complete(
        model="gpt-4o-mini",
        messages=[
            ChatRequestMessage({"role": "user", "content": f"Who wrote {book}?"})
        ],
        tools=[
            ChatCompletionsToolDefinition(
                function=FunctionDefinition(
                    name="get_book_author",
                    description="Returns the author of the book with the given title.",
                    parameters={
                        "properties": {"title": {"type": "string"}},
                        "required": ["title"],
                        "type": "object",
                    },
                )
            )
        ],
    )
    if tool_calls := completion.choices[0].message.tool_calls:
        if tool_calls[0].function.name == "get_book_author":
            return get_book_author(**json.loads(tool_calls[0].function.arguments))
    return str(completion.choices[0].message.content)


author = identify_author("The Name of the Wind")
print(author)
