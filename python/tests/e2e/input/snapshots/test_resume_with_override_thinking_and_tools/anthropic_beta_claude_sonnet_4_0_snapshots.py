from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 477,
                "output_tokens": 26,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=477, output_tokens=26, server_tool_use=None, service_tier='standard')",
                "total_tokens": 503,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Fibonacci Calculation Strategy**

Okay, so the user wants the 100th Fibonacci number. Easy enough. I remember that `default_api.compute_fib` function is designed for this kind of calculation. That's precisely what it's for. So, I need to call that function. And, since they're looking for the 100th term, the input `n` should be set to 100. Should be straightforward.
"""
                        ),
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            args='{"n": 100}',
                        ),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Fibonacci Calculation Strategy**

Okay, so the user wants the 100th Fibonacci number. Easy enough. I remember that `default_api.compute_fib` function is designed for this kind of calculation. That's precisely what it's for. So, I need to call that function. And, since they're looking for the 100th term, the input `n` should be set to 100. Should be straightforward.
""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"n": 100},
                                    "name": "compute_fib",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xe2\x01\x01r\xc8\xda|\xbc{\x0eX\x06a\x08\x9c\xa9\xfeW"\xe8\xa9\rW\xff*\x0e\xe2J*\xff=X\xf4\xc7\xa6\xa4\x05\xf5\x8fS"Pmb\x97\xd3\xbfI+\xb2\xfe"\x0b\x04t\xf1T\xad\x1b\xca\xba\x1ew\x984\xfc(\xaaf>k\xee\x03\x08:\xd5f\xe5\x05\x03\xdcS\x1a~\xed\xe0\xd6\x1c\xb3t\n\x12\xbbJ\x14H\xe6:\xabw\x9cT\xb1X\xc4\x8d\xb5\t\xdf\xf4?\xb8<K\xdf\xe8\xcd\x85\x80\xed1q\xf2c=\xc1\x1a\xfc\xdcy\xaf\xf1\x9c\xdb\xe8\x0f`(\x10\x9aoT\xf8\xb5\x19\xdd\x1b\x00\xc8\x0fZ,\xc2\xc3dK\xab\x95\x00M#Um\x1f\x12\xc1\xf0DUX\x1eM3\x1fV\x00c\xa1\xba6b\xcf\xad\xee\xd3x\xe5r\xbb\xe6\nc\n\x8d\x1e\xad\xddC\x7f\x166\xa9p\xc9\xd8\x98\xaa=F\x83\xe8\xef\xab\xff\xa3\xa5q\xc5v\x85\xfen\xeb\xcbey\xac\x89',
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            value="218922995834555169026",
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
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
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
                    "strict": False,
                }
            ],
        }
    }
)
