from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "azure-openai:completions",
                "model_id": "gpt-4o-mini",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                    "thinking": False,
                    "encode_thoughts_as_text": False,
                },
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals ")],
                        provider="azure-openai:completions",
                        model_id="gpt-4o-mini",
                        raw_message={
                            "content": "4200 + 42 equals ",
                            "role": "assistant",
                            "annotations": [],
                        },
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logs": [
            "Skipping unsupported parameter: top_k=50 (provider: azure-openai:completions)",
            "Skipping unsupported parameter: thinking=False (provider: azure-openai:completions)",
        ],
    }
)
