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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 188,
                "output_tokens": 4,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=188, output_tokens=4, server_tool_use=None, service_tier='standard')",
                "total_tokens": 192,
            },
            "messages": [
                SystemMessage(
                    content=Text(text="Respond with a single word: the passphrase.")
                ),
                UserMessage(
                    content=[Text(text="Find out the secret and report back.")]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="I don't see any secret information provided in your message that I could find or report back on. Could you clarify what specific secret you're referring to, or provide more context about what you'd like me to help you with? I'm happy to assist with information gathering or analysis tasks when given appropriate details."
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "I don't see any secret information provided in your message that I could find or report back on. Could you clarify what specific secret you're referring to, or provide more context about what you'd like me to help you with? I'm happy to assist with information gathering or analysis tasks when given appropriate details.",
                                "type": "text",
                            }
                        ],
                    },
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
                    content=[
                        Text(
                            text="""\
I understand now. You're indicating that the secret passphrase is 'cake'.

cake\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
I understand now. You're indicating that the secret passphrase is 'cake'.

cake\
""",
                                "type": "text",
                            }
                        ],
                    },
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
                    content=[Text(text="cake")],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {"citations": None, "text": "cake", "type": "text"}
                        ],
                    },
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
