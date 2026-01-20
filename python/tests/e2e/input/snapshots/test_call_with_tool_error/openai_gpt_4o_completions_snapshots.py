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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 104,
                "output_tokens": 31,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=31, prompt_tokens=104, total_tokens=135, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 135,
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
                            id="call_pqZYlGgEIyaGG3rI86Ii3F1V",
                            name="test_tool",
                            args='{"passphrase":"portal"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_pqZYlGgEIyaGG3rI86Ii3F1V",
                                "function": {
                                    "arguments": '{"passphrase":"portal"}',
                                    "name": "test_tool",
                                },
                                "type": "function",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_pqZYlGgEIyaGG3rI86Ii3F1V",
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
                            text="It seems that the passphrase provided was incorrect. The correct passphrase is 'cake'. Would you like me to try using that passphrase instead?"
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": "It seems that the passphrase provided was incorrect. The correct passphrase is 'cake'. Would you like me to try using that passphrase instead?",
                        "role": "assistant",
                        "annotations": [],
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
                    id="call_pqZYlGgEIyaGG3rI86Ii3F1V",
                    name="test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'"
                    ),
                )
            ]
        ],
    }
)
