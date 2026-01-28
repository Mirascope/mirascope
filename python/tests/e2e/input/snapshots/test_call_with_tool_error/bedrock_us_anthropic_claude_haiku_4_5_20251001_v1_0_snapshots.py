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
            "provider_id": "bedrock",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 811,
                "output_tokens": 36,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=811, output_tokens=36, server_tool_use=None, service_tier=None)",
                "total_tokens": 847,
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
                        ToolCall(
                            id="toolu_bdrk_01NgSz4C8efo97UfdxtHf7Ph",
                            name="passphrase_test_tool",
                            args='{"passphrase": "portal"}',
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01NgSz4C8efo97UfdxtHf7Ph",
                                "input": {"passphrase": "portal"},
                                "name": "passphrase_test_tool",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_01NgSz4C8efo97UfdxtHf7Ph",
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
                            text="The passphrase \"portal\" was incorrect. According to the tool's response, the correct passphrase is **'cake'**. Let me try again with the correct passphrase:"
                        ),
                        ToolCall(
                            id="toolu_bdrk_01A6rJ7ZkYoY9d66F7YVxds5",
                            name="passphrase_test_tool",
                            args='{"passphrase": "cake"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "The passphrase \"portal\" was incorrect. According to the tool's response, the correct passphrase is **'cake'**. Let me try again with the correct passphrase:",
                                "type": "text",
                            },
                            {
                                "id": "toolu_bdrk_01A6rJ7ZkYoY9d66F7YVxds5",
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
                            id="toolu_bdrk_01A6rJ7ZkYoY9d66F7YVxds5",
                            name="passphrase_test_tool",
                            result="The cake is a lie.",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='Great! I\'ve successfully used the test tool with the correct passphrase "cake". The secret phrase retrieved is: **"The cake is a lie."**'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": 'Great! I\'ve successfully used the test tool with the correct passphrase "cake". The secret phrase retrieved is: **"The cake is a lie."**',
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
                    id="toolu_bdrk_01NgSz4C8efo97UfdxtHf7Ph",
                    name="passphrase_test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'. Try again.",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'. Try again."
                    ),
                )
            ],
            [
                ToolOutput(
                    id="toolu_bdrk_01A6rJ7ZkYoY9d66F7YVxds5",
                    name="passphrase_test_tool",
                    result="The cake is a lie.",
                )
            ],
        ],
    }
)
