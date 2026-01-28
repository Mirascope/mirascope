from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolExecutionError,
    ToolNotFoundError,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 490,
                "output_tokens": 14,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=14, prompt_tokens=490, total_tokens=504, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 504,
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
                            text="<reasoning>The user says: \"Use the test tool to retrieve the secret phrase. The passphrase is 'portal\". They want us to call the function passphrase_test_tool with passphrase 'portal'. The instruction: \"The passphrase is 'portal\". So we call that function.</reasoning>"
                        ),
                        ToolCall(
                            id="chatcmpl-tool-ba93b1ccb76d93ba",
                            name="passphrase_test_tool",
                            args='{"passphrase":"portal"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": "<reasoning>The user says: \"Use the test tool to retrieve the secret phrase. The passphrase is 'portal\". They want us to call the function passphrase_test_tool with passphrase 'portal'. The instruction: \"The passphrase is 'portal\". So we call that function.</reasoning>",
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "chatcmpl-tool-ba93b1ccb76d93ba",
                                "function": {
                                    "arguments": '{"passphrase":"portal"}',
                                    "name": "passphrase_test_tool",
                                },
                                "type": "function",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="chatcmpl-tool-ba93b1ccb76d93ba",
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
                            text="""\
<reasoning>The tool returned an error saying the passphrase is indeed incorrect. The user provided 'portal', but tool says correct passphrase is 'cake'. So we should try again with passphrase 'cake'.

</reasoning>\
"""
                        ),
                        ToolCall(
                            id="chatcmpl-tool-aa9cb445bf5b7510",
                            name="passphrase_test_tool<|channel|>commentary",
                            args='{"passphrase":"cake"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": """\
<reasoning>The tool returned an error saying the passphrase is indeed incorrect. The user provided 'portal', but tool says correct passphrase is 'cake'. So we should try again with passphrase 'cake'.

</reasoning>\
""",
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "chatcmpl-tool-aa9cb445bf5b7510",
                                "function": {
                                    "arguments": '{"passphrase":"cake"}',
                                    "name": "passphrase_test_tool<|channel|>commentary",
                                },
                                "type": "function",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="chatcmpl-tool-aa9cb445bf5b7510",
                            name="passphrase_test_tool<|channel|>commentary",
                            result="Tool 'passphrase_test_tool<|channel|>commentary' not found in registered tools",
                            error=ToolNotFoundError(
                                "passphrase_test_tool<|channel|>commentary"
                            ),
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='<reasoning>Error: we used wrong method. The correct function call syntax is `functions.passphrase_test_tool`. The tool is defined under namespace functions. So call `functions.passphrase_test_tool({ passphrase: "cake" })`. Let\'s produce.</reasoning>'
                        ),
                        ToolCall(
                            id="chatcmpl-tool-81626816bf0b266e",
                            name="passphrase_test_tool",
                            args='{"passphrase":"cake"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": '<reasoning>Error: we used wrong method. The correct function call syntax is `functions.passphrase_test_tool`. The tool is defined under namespace functions. So call `functions.passphrase_test_tool({ passphrase: "cake" })`. Let\'s produce.</reasoning>',
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "chatcmpl-tool-81626816bf0b266e",
                                "function": {
                                    "arguments": '{"passphrase":"cake"}',
                                    "name": "passphrase_test_tool",
                                },
                                "type": "function",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="chatcmpl-tool-81626816bf0b266e",
                            name="passphrase_test_tool",
                            result="The cake is a lie.",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text='The secret phrase is: **"cake"**')],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": 'The secret phrase is: **"cake"**',
                        "role": "assistant",
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
                    id="chatcmpl-tool-ba93b1ccb76d93ba",
                    name="passphrase_test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'. Try again.",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'. Try again."
                    ),
                )
            ],
            [
                ToolOutput(
                    id="chatcmpl-tool-aa9cb445bf5b7510",
                    name="passphrase_test_tool<|channel|>commentary",
                    result="Tool 'passphrase_test_tool<|channel|>commentary' not found in registered tools",
                    error=ToolNotFoundError(
                        "passphrase_test_tool<|channel|>commentary"
                    ),
                )
            ],
            [
                ToolOutput(
                    id="chatcmpl-tool-81626816bf0b266e",
                    name="passphrase_test_tool",
                    result="The cake is a lie.",
                )
            ],
        ],
    }
)
