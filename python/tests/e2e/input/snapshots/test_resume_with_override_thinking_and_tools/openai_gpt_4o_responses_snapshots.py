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
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 84,
                "output_tokens": 18,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=84, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=18, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=102)",
                "total_tokens": 102,
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
                                "thought_signature": b'\n\xe2\x01\x01r\xc8\xda|\xb3\xc4\xd3\xe0\xa7\xc0{I\x80\xd2\r\x8e|4\xfa1W\\\xd7\xd4\xcd\xfa|0]T\x8e\x9bq\xc3\xd4\xdc\n\x8c\x94\xc6t&\xf6\xf8a\x19\xe6R\xab\x99\xab\x9c\xf6\x17\x1b\xc7\xc3bL\x83\x80\x9bKQF\x19\x93\xef\xe1&\x94\xa7\x8c\x15\x827~\xc0\x17j\xc4zz\xca?\x08\x17\x8c\xa6\x08F>\xfa\x1e\x14iO\x0ee\x86\xbfv\xab\\\xcaj\x88\xc3\x9d9k\xe0\xad!Z5!\xac{e\xbe\x16\x1d\xf8+V\r\xa7B\xd5\xf6\x1e\xd5\xed\xad\xc8,\xc9X\xe8t\xb0F\x95\n\x15\x89/j7UU.\x07\xa1\x8b"u\xa47\xc9\xc6r:\xb0\x17\xda\x1cD\xa2\xc2\xbe\x0e \xa1\xbc]\x19o\x00\x90\x00\x0f\x10\x08\xe7"\x81\xde\xd6\x92\x16R\x81$\xd2t\xbf\xef\x074\xe9\x17\x03!\xed\xce\xa1)\xb8&2\xd1\xe8K\x18%\xe0]\x06\xc3O\xadz\x1c',
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
                            text="The 100th Fibonacci number is 218922995834555169026."
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_06239e8744215ddf0069689ad7c6f88193853e05a8db2a352c",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "The 100th Fibonacci number is 218922995834555169026.",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
