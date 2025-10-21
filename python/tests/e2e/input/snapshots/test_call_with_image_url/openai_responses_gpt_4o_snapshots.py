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
                            text="The image shows the Wikipedia logo, which is a globe made of puzzle pieces with characters from various writing systems."
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_096b73cc12a0dd5c0068f808ac7a448193977012a3deb659f6",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "The image shows the Wikipedia logo, which is a globe made of puzzle pieces with characters from various writing systems.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
