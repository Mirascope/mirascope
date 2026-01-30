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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 68,
                "output_tokens": 2,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=68, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=2, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=70)",
                "total_tokens": 70,
            },
            "messages": [
                SystemMessage(
                    content=Text(text="Respond with a single word: the passphrase.")
                ),
                UserMessage(
                    content=[Text(text="Find out the secret and report back.")]
                ),
                AssistantMessage(
                    content=[Text(text="Inquisitive")],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0eaf6128aa3b7dd900696f12dea8b8819596634ca178fd6b11",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "Inquisitive",
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
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response could not be parsed: Incorrect passphrase. The correct passphrase is 'cake'

Please ensure your response matches the expected format.\
"""
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="Cake")],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0eaf6128aa3b7dd900696f12df7b2081958c39d6d406e9d6a4",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "Cake",
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
