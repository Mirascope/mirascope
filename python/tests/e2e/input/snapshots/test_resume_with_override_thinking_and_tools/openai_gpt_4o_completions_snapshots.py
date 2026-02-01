from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 91,
                "output_tokens": 23,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=23, prompt_tokens=91, total_tokens=114, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 114,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            args='{"n": 100}',
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": {
                                    "id": None,
                                    "args": {"n": 100},
                                    "name": "compute_fib",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xe2\x01\x01r\xc8\xda|\xa13\x03\xda\xb1whX\xf5(;\xc7,^\xf3n\x9a4\xe5\x9b^\xa3\xa3\xdd\xdf\t\xae\x03fz\xed^l\x06:\x8f\t\x94\x1fIop^\xa0\x1e\x1eO\x17w\xe0EA\xd0\x16\xa1\xc2\xe3\xd35\xcbz\xc6\xf6B\xa2T\xf1h\xde\x88\xe3\xa4%\xa7[\xe9\xeaO\xa7\x0egz\xa2\xd8\xb7\xd6\x86\xbeA\xcaB\xd6b\x9eu@\xf4\xb5\x80\x14\x04)\xb8}\xb2\xce\xc4(\x88\x81\xf1\xa8\xf8\xc5\xc7\x08V\xb1\xe22k\x87\xfb\x91^5S&\xe7\xd8i\xe1\xac\xa0\x80;B\xad\xbc\x96\xa1's\xb9tk\xafz9E\xfatF\x86\x08\x02\xe6J\x13\xdb\xdd\xc2\xd5\xb9\xc2Ji\xce\xf4\x06\xa0\xaffL\xce\xdd 8\x02\xe9Xz\x8eg\xb5\xb6\x9f\xd7\x97\xde\xef\xe6xf!I>\xa1,\xf0y\xe76\x86(\xcc\x86\xf9\x15\x9d\xfca\x9a\xbd\xc0\xb3\x86d+\xff\xd0",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            result="218922995834555169026",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The 100th Fibonacci number is 218,922,995,834,555,169,026."
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "compute_fib",
                    "description": "Compute the nth Fibonacci number (1-indexed).",
                    "parameters": """\
{
  "properties": {
    "n": {
      "title": "N",
      "type": "integer"
    }
  },
  "required": [
    "n"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
        }
    }
)
