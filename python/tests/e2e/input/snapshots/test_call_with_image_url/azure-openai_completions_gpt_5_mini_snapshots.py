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
            "provider": "azure-openai:completions",
            "model_id": "gpt-5-mini",
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
                            text="A gray spherical jigsaw globe composed of interlocking puzzle pieces, each marked with a different letter or character from various writing systems, representing the Wikipedia logo."
                        )
                    ],
                    provider="azure-openai:completions",
                    model_id="gpt-5-mini",
                    raw_message={
                        "content": "A gray spherical jigsaw globe composed of interlocking puzzle pieces, each marked with a different letter or character from various writing systems, representing the Wikipedia logo.",
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
