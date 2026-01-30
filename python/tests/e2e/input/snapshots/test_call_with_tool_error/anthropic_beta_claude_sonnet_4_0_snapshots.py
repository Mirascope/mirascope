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
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 638,
                "output_tokens": 22,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=638, output_tokens=22, server_tool_use=None, service_tier='standard')",
                "total_tokens": 660,
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
                            id="toolu_018r3ahM7MaKzR4Gq86zyKZM",
                            name="passphrase_test_tool",
                            args='{"passphrase": "portal"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": "I'll use the test tool with the passphrase you provided.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_018r3ahM7MaKzR4Gq86zyKZM",
                                "input": {"passphrase": "portal"},
                                "name": "passphrase_test_tool",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_018r3ahM7MaKzR4Gq86zyKZM",
                            name="passphrase_test_tool",
                            result="Incorrect passhrase: The correct passphrase is 'cake'. Try again.",
                            error=ToolExecutionError(
                                "Incorrect passhrase: The correct passphrase is 'cake'. Try again."
                            ),
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The passphrase 'portal' was incorrect. The tool indicated that the correct passphrase is 'cake'. Let me try again with the correct passphrase:"
                        ),
                        ToolCall(
                            id="toolu_01Po7AAqi9YKrgB4L9qMWFGw",
                            name="passphrase_test_tool",
                            args='{"passphrase": "cake"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": "The passphrase 'portal' was incorrect. The tool indicated that the correct passphrase is 'cake'. Let me try again with the correct passphrase:",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01Po7AAqi9YKrgB4L9qMWFGw",
                                "input": {"passphrase": "cake"},
                                "name": "passphrase_test_tool",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01Po7AAqi9YKrgB4L9qMWFGw",
                            name="passphrase_test_tool",
                            result="The cake is a lie.",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='The secret phrase has been retrieved! The secret phrase is: "The cake is a lie."'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": 'The secret phrase has been retrieved! The secret phrase is: "The cake is a lie."',
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "passphrase_test_tool",
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
                    id="toolu_018r3ahM7MaKzR4Gq86zyKZM",
                    name="passphrase_test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'. Try again.",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'. Try again."
                    ),
                )
            ],
            [
                ToolOutput(
                    id="toolu_01Po7AAqi9YKrgB4L9qMWFGw",
                    name="passphrase_test_tool",
                    result="The cake is a lie.",
                )
            ],
        ],
    }
)
