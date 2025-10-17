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
                "provider": "openai:responses",
                "model_id": "gpt-4o",
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
                        provider="openai:responses",
                        model_id="gpt-4o",
                        raw_message=[
                            {
                                "id": "msg_0d6a9ea95ee935160068f292323dc48190a48314e7ab483b97",
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
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:responses)",
            "Skipping unsupported parameter: seed=42 (provider: openai:responses)",
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: openai:responses)",
            "Skipping unsupported parameter: thinking=False (provider: openai:responses with model_id: gpt-4o)",
        ],
    }
)
