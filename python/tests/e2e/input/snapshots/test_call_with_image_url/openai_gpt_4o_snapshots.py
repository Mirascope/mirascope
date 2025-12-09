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
            "model_id": "openai/gpt-4o",
            "provider_model_id": "gpt-4o:completions",
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
                            text="The image shows the Wikipedia logo, which is a globe constructed from puzzle pieces featuring various characters from different writing systems."
                        )
                    ],
                    provider="openai",
                    model_id="openai/gpt-4o",
                    provider_model_id="gpt-4o:completions",
                    raw_message={
                        "content": "The image shows the Wikipedia logo, which is a globe constructed from puzzle pieces featuring various characters from different writing systems.",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
