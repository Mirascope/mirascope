from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "provider_model_name": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text=""), Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="It seems like you haven't asked a question yet. Please go ahead and ask your question, and I'll be happy to help!"
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message={
                        "role": "assistant",
                        "content": "It seems like you haven't asked a question yet. Please go ahead and ask your question, and I'll be happy to help!",
                        "tool_calls": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
