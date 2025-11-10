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
                "provider": "azure-openai:responses",
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
                        content=[Text(text="4200 + 42 equals 4242.")],
                        provider="azure-openai:responses",
                        model_id="gpt-4o-mini",
                        raw_message=[
                            {
                                "id": "msg_0bfe44b1728d9a6100690c214d7a20819588671f9c4b727659",
                                "content": [
                                    {
                                        "annotations": [],
                                        "text": "4200 + 42 equals 4242.",
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
            },
        ),
        "logs": [
            "Skipping unsupported parameter: top_k=50 (provider: azure-openai:responses)",
            "Skipping unsupported parameter: seed=42 (provider: azure-openai:responses)",
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: azure-openai:responses)",
            "Skipping unsupported parameter: thinking=False (provider: azure-openai:responses with model_id: gpt-4o-mini)",
        ],
    }
)
