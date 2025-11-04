from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Image,
    Text,
    URLImageSource,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(text="Describe the following image in one sentence"),
                        Image(
                            source=URLImageSource(
                                type="url_image_source",
                                url="https://en.wikipedia.org/static/images/icons/wikipedia.png",
                            )
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The image is the Wikipedia logo, featuring a globe made of puzzle pieces with various characters on them."
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0371d245ba0faaf90068f9668756808195a999162b17b05af1",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "The image is the Wikipedia logo, featuring a globe made of puzzle pieces with various characters on them.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                            "response_id": "resp_0371d245ba0faaf90068f96684b6e48195a8a8b759e2f363de",
                        }
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
