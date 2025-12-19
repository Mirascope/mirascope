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
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 95,
                "output_tokens": 24,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=95, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=24, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=119)",
                "total_tokens": 119,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**The Fibonacci Challenge**

Okay, so the user wants the 100th Fibonacci number.  No problem. I immediately recall the `default_api.compute_fib` function – that's *exactly* what that's for.  The parameter I need to pass is the `n` value, in this case, 100.  So, I just need to call `default_api.compute_fib(n=100)`.  Simple as that.
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
**The Fibonacci Challenge**

Okay, so the user wants the 100th Fibonacci number.  No problem. I immediately recall the `default_api.compute_fib` function – that's *exactly* what that's for.  The parameter I need to pass is the `n` value, in this case, 100.  So, I just need to call `default_api.compute_fib(n=100)`.  Simple as that.
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
                                "thought_signature": b"\n\xe0\x01\x01r\xc8\xda|}\xb3g\xe4\xe3\x9c\x87\x188\xef8\xea_\x1ak?4\xf4\xf5\xd4\xa5\xbdm\x01\xffP\xc6\x9c\x0c\x88\xe2\x92\xe3\xa3G\x9a\xacH\x94\x16\xe8\xf6\xd6E:\xaf\xae:4\xdeL\xeei\x01\xba\xd4\x06\xa2\x14d\x08\xf0q\xb7\x03\x1f\x0b\xf7\xd2\xce\xfcN\xedE\xf7_>jGO\xcf1\x1f\xcfr\x8a\xc9\xbf\xeb\x17\xc9\xd1M\x08\x91uB\xdeW\x14\xd7\xa2\x90/\x88\xd8A\xf2<}\xe2\xc9l\xb1\xcc\xf5\xd5\xe5'\x0b\xfb}vx\xe5\xe0,:\x1a\xccq\xb1+\x15G&\xf6\xa9$^f\xea\x81#6f\x03\x10u\xa4C\xe7\x91d*\xfcjW\xc1\xf8;\xc3EBSZ\x83\xd8\x07\x06\xad\xd9f\xbc\xb9'X+\xf7A\xe4\xff\xacczX+\xd8\xabbH\r\x8cj\x049\x81\xb1p\x0c.\x9c3\x1b\x1d\x87\xe7\xaaCMV\xb71 \xb8\xca\x02\xc7\xa6",
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
                            text="""\
The 100th Fibonacci number (1-indexed) is:
218922995834555169026\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "msg_0f561720cb677a610069492dcf5cb08195b3948d0fabb9ff98",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
The 100th Fibonacci number (1-indexed) is:
218922995834555169026\
""",
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
                    "strict": False,
                }
            ],
        }
    }
)
