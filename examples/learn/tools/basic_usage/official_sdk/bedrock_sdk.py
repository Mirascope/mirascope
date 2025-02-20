import boto3

bedrock_client = boto3.client(service_name="bedrock-runtime")


def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


def identify_author(book: str) -> str:
    messages = [{"role": "user", "content": [{"text": f"Who wrote {book}?"}]}]
    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "get_book_author",
                    "description": "Returns the author of the book with the given title.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "The title of the book.",
                                }
                            },
                            "required": ["title"],
                        }
                    },
                }
            }
        ]
    }
    response = bedrock_client.converse(
        modelId="amazon.nova-lite-v1:0",
        messages=messages,
        toolConfig=tool_config,
    )
    content = ""
    output_message = response["output"]["message"]
    messages.append(output_message)
    stop_reason = response["stopReason"]

    if stop_reason == "tool_use":
        tool_requests = output_message["content"]
        for tool_request in tool_requests:
            if "toolUse" in tool_request:
                tool = tool_request["toolUse"]
                if tool["name"] == "get_book_author":
                    return get_book_author(**tool["input"])
    for content_piece in output_message["content"]:
        if "text" in content_piece:
            content += content_piece["text"]
    return content


author = identify_author("The Name of the Wind")
print(author)
