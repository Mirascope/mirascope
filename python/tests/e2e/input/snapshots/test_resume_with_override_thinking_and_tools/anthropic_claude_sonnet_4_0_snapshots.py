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
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 477,
                "output_tokens": 26,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=477, output_tokens=26, server_tool_use=None, service_tier='standard')",
                "total_tokens": 503,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Fibonacci Number Calculation**

Okay, so the user wants the 100th Fibonacci number.  No problem. I know the `default_api.compute_fib` function handles this perfectly.  It's designed for exactly this purpose.  My thought process is simple: I'll just call `compute_fib` with `n=100`. That should give me the answer they're looking for without any further manipulation needed. Easy peasy.
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
**Fibonacci Number Calculation**

Okay, so the user wants the 100th Fibonacci number.  No problem. I know the `default_api.compute_fib` function handles this perfectly.  It's designed for exactly this purpose.  My thought process is simple: I'll just call `compute_fib` with `n=100`. That should give me the answer they're looking for without any further manipulation needed. Easy peasy.
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
                                "thought_signature": b"\n\xe2\x01\x01r\xc8\xda|\x0c\x1a:\xa1\x92\x1b\xf1h\xf1{\x14OLT\xa8_\xd8B\xe2\xe4p\xf7\x99J\xdc\xb1hl,\x81\xa3\x1e\x16\xec\xaaV\xdb9\xbe\x8a\x87\x9a?L/^=F\xd4\x8e\x96\xa6\x8an6i\x1b\x14C\xa6\xa9\xc1\xa3\x9c\x98\x08W3\t\xf3\x85 %M\xea\xee/\x8c\xa3rwU\x8b\xae\xb70\x11``\xb9\xd4\xe6\x15_d*\xdf\xa9\xea\xa8\xef\xa6\xd2\xd2C\xe7\xe6\xa9\x07e\x07g\xd7\xed=\xa1\xb0\xcel\xaa(\xb8C5B\x1d6z\xac-T\x9d\n\x96]\x85\xa1\x998l\x9bS1Q\xcb\xd6O\xe4\x16&\xe6\x80\x9a\xcb]\xbf\xf9\x0f\x86\x97Y$\xc5\\\x7f\xb8\x1d\x89H\xdc\xd2\xda\x99[Y\xcf\xf7k>\xa5\xdf\xe5\xb0\xcbBS\xba!a\xad\xb8{3\xbd=\x13T6\xbb\x8d\xe5\xc9\x0b/.\xfeq\x1a\xee\xcc\xe4\xee\x95\x17\xd8\xaa(VK\xaag",
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
                    "strict": False,
                }
            ],
        }
    }
)
