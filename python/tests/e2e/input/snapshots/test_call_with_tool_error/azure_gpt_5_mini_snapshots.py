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
            "provider_id": "azure",
            "model_id": "azure/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 200,
                "output_tokens": 429,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 384,
                "raw": "CompletionUsage(completion_tokens=429, prompt_tokens=200, total_tokens=629, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=384, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 629,
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
                            id="call_A3OBMTenzkGrqWRSGtM3dEOW",
                            name="passphrase_test_tool",
                            args='{"passphrase":"\'portal"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_A3OBMTenzkGrqWRSGtM3dEOW",
                                "function": {
                                    "arguments": '{"passphrase":"\'portal"}',
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
                            id="call_A3OBMTenzkGrqWRSGtM3dEOW",
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
                            text="The tool reported your passphrase \"'portal\" was incorrect and returned the correct passphrase: 'cake'. Would you like me to run the test tool again using 'cake'?"
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": "The tool reported your passphrase \"'portal\" was incorrect and returned the correct passphrase: 'cake'. Would you like me to run the test tool again using 'cake'?",
                        "role": "assistant",
                        "annotations": [],
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
                    id="call_A3OBMTenzkGrqWRSGtM3dEOW",
                    name="passphrase_test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'. Try again.",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'. Try again."
                    ),
                )
            ]
        ],
    }
)
