import boto3
from pydantic import BaseModel

bedrock_client = boto3.client(service_name="bedrock-runtime")


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    messages = [{"role": "user", "content": [{"text": f"Extract {text}"}]}]
    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "Book",
                    "description": "An extracted book.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "author": {"type": "string"},
                            },
                            "required": ["title", "author"],
                        }
                    },
                }
            }
        ],
        "toolChoice": {"type": "tool", "name": "Book"},
    }
    response = bedrock_client.converse(
        modelId="amazon.nova-lite-v1:0",
        messages=messages,
        toolConfig=tool_config,
    )
    output_message = response["output"]["message"]
    messages.append(output_message)
    for content_piece in output_message["content"]:
        if "toolUse" in content_piece and content_piece["toolUse"].get("input"):
            tool_input = content_piece["toolUse"]["input"]
            return Book.model_validate(tool_input)
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
