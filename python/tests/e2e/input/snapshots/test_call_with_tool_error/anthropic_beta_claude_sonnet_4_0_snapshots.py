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
                "input_tokens": 627,
                "output_tokens": 30,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=627, output_tokens=30, server_tool_use=None, service_tier='standard')",
                "total_tokens": 657,
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
                            id="toolu_01CdpCuiVXrd7B3T2TqPbFQn",
                            name="test_tool",
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
                                "id": "toolu_01CdpCuiVXrd7B3T2TqPbFQn",
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
                            id="toolu_01CdpCuiVXrd7B3T2TqPbFQn",
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
                            text="It looks like the passphrase 'portal' was incorrect. The tool returned that the correct passphrase is 'cake'. Let me try again with the correct passphrase:"
                        ),
                        ToolCall(
                            id="toolu_01XMyM5m1tpf1zGA9FHqLm8Z",
                            name="test_tool",
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
                                "text": "It looks like the passphrase 'portal' was incorrect. The tool returned that the correct passphrase is 'cake'. Let me try again with the correct passphrase:",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01XMyM5m1tpf1zGA9FHqLm8Z",
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
                            id="toolu_01XMyM5m1tpf1zGA9FHqLm8Z",
                            name="test_tool",
                            result="The cake is a lie.",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="Success! Using the correct passphrase 'cake', the test tool returned the secret phrase: \"The cake is a lie.\""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": "Success! Using the correct passphrase 'cake', the test tool returned the secret phrase: \"The cake is a lie.\"",
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
                    id="toolu_01CdpCuiVXrd7B3T2TqPbFQn",
                    name="test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'"
                    ),
                )
            ],
            [
                ToolOutput(
                    id="toolu_01XMyM5m1tpf1zGA9FHqLm8Z",
                    name="test_tool",
                    result="The cake is a lie.",
                )
            ],
        ],
    }
)
