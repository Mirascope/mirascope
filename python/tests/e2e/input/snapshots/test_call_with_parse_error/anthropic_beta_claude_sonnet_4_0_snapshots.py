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
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 169,
                "output_tokens": 4,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=169, output_tokens=4, server_tool_use=None, service_tier='standard')",
                "total_tokens": 173,
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
                            text="""\
I don't see any secret information or puzzle to solve in your message. Could you provide more context about what secret you'd like me to find? For example:

- Is there a coded message, cipher, or puzzle you'd like me to analyze?
- Are you referring to a riddle or brain teaser?
- Is there additional information or context I should be working with?

Please share the details of what you'd like me to investigate, and I'll do my best to help!\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": """\
I don't see any secret information or puzzle to solve in your message. Could you provide more context about what secret you'd like me to find? For example:

- Is there a coded message, cipher, or puzzle you'd like me to analyze?
- Are you referring to a riddle or brain teaser?
- Is there additional information or context I should be working with?

Please share the details of what you'd like me to investigate, and I'll do my best to help!\
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
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [{"text": "cake", "type": "text"}],
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
