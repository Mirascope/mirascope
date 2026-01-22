from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 17,
                "output_tokens": 2,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 19,
            },
            "messages": [
                SystemMessage(
                    content=Text(text="Respond with a single word: the passphrase.")
                ),
                UserMessage(
                    content=[Text(text="Find out the secret and report back.")]
                ),
                AssistantMessage(
                    content=[Text(text="cake")],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": {
                "name": "extract_passphrase",
                "description": "Extract a passphrase from the response.",
                "schema": {},
                "mode": "parser",
                "formatting_instructions": "Respond with a single word: the passphrase.",
            },
            "tools": [],
        }
    }
)
