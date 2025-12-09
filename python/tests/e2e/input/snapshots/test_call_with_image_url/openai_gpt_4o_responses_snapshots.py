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
            "provider": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_id": "gpt-4o:responses",
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
                    provider="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_id="gpt-4o:responses",
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
                        }
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
