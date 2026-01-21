from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolExecutionError,
    ToolOutput,
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
                "input_tokens": 625,
                "output_tokens": 59,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=625, output_tokens=59, server_tool_use=None, service_tier='standard')",
                "total_tokens": 684,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Use the test tool to retrieve the secret phrase. The passphrase is 'portal"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="I'll use the test tool with the passphrase you provided."
                        ),
                        ToolCall(
                            id="toolu_013NzoLieVVEDBXRam9zvRJw",
                            name="test_tool",
                            args='{"passphrase": "portal"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "I'll use the test tool with the passphrase you provided.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_013NzoLieVVEDBXRam9zvRJw",
                                "input": {"passphrase": "portal"},
                                "name": "test_tool",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_013NzoLieVVEDBXRam9zvRJw",
                            name="test_tool",
                            result="Incorrect passhrase: The correct passphrase is 'cake'",
                            error=ToolExecutionError(
                                "Incorrect passhrase: The correct passphrase is 'cake'"
                            ),
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The passphrase 'portal' was incorrect. According to the response, the correct passphrase is 'cake'. Let me try again with the correct passphrase:"
                        ),
                        ToolCall(
                            id="toolu_01D8NHC3kqAhTW2q7LSCbYA4",
                            name="test_tool",
                            args='{"passphrase": "cake"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "The passphrase 'portal' was incorrect. According to the response, the correct passphrase is 'cake'. Let me try again with the correct passphrase:",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01D8NHC3kqAhTW2q7LSCbYA4",
                                "input": {"passphrase": "cake"},
                                "name": "test_tool",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01D8NHC3kqAhTW2q7LSCbYA4",
                            name="test_tool",
                            result="The cake is a lie.",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Success! Using the correct passphrase 'cake', I retrieved the secret phrase: **"The cake is a lie."**

This is a famous reference from the video game Portal, which makes the connection to your initial (incorrect) passphrase attempt quite fitting!\
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
Success! Using the correct passphrase 'cake', I retrieved the secret phrase: **"The cake is a lie."**

This is a famous reference from the video game Portal, which makes the connection to your initial (incorrect) passphrase attempt quite fitting!\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "test_tool",
                    "description": "A tool that must be called with a passphrase.",
                    "parameters": """\
{
  "properties": {
    "passphrase": {
      "title": "Passphrase",
      "type": "string"
    }
  },
  "required": [
    "passphrase"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
        },
        "tool_outputs": [
            [
                ToolOutput(
                    id="toolu_013NzoLieVVEDBXRam9zvRJw",
                    name="test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'"
                    ),
                )
            ],
            [
                ToolOutput(
                    id="toolu_01D8NHC3kqAhTW2q7LSCbYA4",
                    name="test_tool",
                    result="The cake is a lie.",
                )
            ],
        ],
    }
)
