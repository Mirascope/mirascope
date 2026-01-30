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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 477,
                "output_tokens": 26,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=477, output_tokens=26, server_tool_use=None, service_tier='standard')",
                "total_tokens": 503,
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
                                "thought_signature": b"\n\xbc\x02\x01r\xc8\xda|\xee;\xf5\xce\x17j\x1d\xd5T\x0e\xf9\xd6\xb5\xd2;\x7f\xca\x92\xf2\xc9\xdb\x0eJ\x94Rq/AVr\xa0\x95\x02\xd9q\x19\xdc^\xe4\xfb`\xfa\xd3\xefm\\\xbd'\x90\xb2\x9b\x82\\\xfcI\xb4\x9az,\x86,\xdd\x18b\x92vN3%\xce\xae%3\xca5\x96}\xda\xa2\xc3\x1cx%\xa2\xbf\xbb#\x07\x0f\x05\xdcZ\x98?o\xb5\xb3\xae\x7f\xde\xfd\xc4\x89\x007\xe6t'\xd5\x15^k\x1f\x1c,\x0e&\xa7\xed\x9d\x86\xee0\xe3\xfa\x0c\xa4\x8e\r\x0f\xbf\xfa\xb09q\xe4\xbb\x1d\x16\xaf|\x16\x0f\x9dzZ\x16j\x80q\x9a\x7f\xb0W\xb09u\\\x03\x05\xe8z\x15\xebH\xa6z\xfd\xdc2P\x89\x98hm\xee\xa6Y\x0bHy\xbf;\xcb[;\xaa\xdc\x8c\x15\x94\xaf\xb7(\xe5\xd5\xfa\xe9\x0eP\xae\x8a\xdeXJg\x01\x1e\xa6\x14\xa9\xaf\x80rg\xfa\xae\xadEV4K\xa9w\xfdks\x80\x9b\xbd\xb3\xf1C\x12\xcc\x86w\xec\x9df9\xb3\xdd\xdc_\x984/\xcf\x11\xb0\xc9\xad\x1d\x0b\xcer\xccn\x1eK\x9e\xb3\x08\x8fO\xad!\x00\xff\xf7|=\x9b\xdf\xed\xcf\x94\xc3\xe8\x13\xeel\x94;\x81P\xff\xc3\xe3\xf6C\xacA\xe6\xce\x80ew[X\x06\xd8\xcd\xfd\x12\"c\x92pW",
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
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
                                "type": "text",
                            }
                        ],
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
