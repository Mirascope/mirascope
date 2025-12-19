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
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 84,
                "output_tokens": 24,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=84, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=24, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=108)",
                "total_tokens": 108,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**The Fibonacci Conundrum**

Alright, so the user is after the 100th Fibonacci number. Easy enough. We've got the `default_api.compute_fib` function specifically designed for this. Seems like all I need to do is feed it the right input.  Let's see, the parameter is `n`, and they want the 100th term. Therefore, I need to call the function with `n=100`. Simple as that.
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
**The Fibonacci Conundrum**

Alright, so the user is after the 100th Fibonacci number. Easy enough. We've got the `default_api.compute_fib` function specifically designed for this. Seems like all I need to do is feed it the right input.  Let's see, the parameter is `n`, and they want the 100th term. Therefore, I need to call the function with `n=100`. Simple as that.
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
                                "thought_signature": b"\n\xe2\x01\x01\xd1\xed\x8ao\x15|nC\xac\xc5\x03Q\x02\xd7\xfao\x9e\x8111\x17m6TO\x0c[C\xb4\xb5w\x06\xd0F\x92\xec\x16\x12\x85q21\xf7{\xd0k\x98j\xb4\xc4T\xe9\xe3d>\xca\x02\xff0\x9b~\xca\xd8\xe0\x04\xeei!0Z\xee&\x90\xb3\x1fPf\r\x8b\xe3Rd}\xa8\xe8\x8ba\xca\xa6\x1c~\xdf&B\x134\r\x12\x1ae\xd5V\xb2qen\\\xc0\xbf\x86\x17P\xebng\x06\x1b\xd5\xd5D\xa7\x00>2\x10\x92\x97V0crXg.\x8c\xa79[\x15\xd0\xeeA\xdb\xaf\xb1m7\x0e\xfa\xc9\xb8\xea\xaaf\x1e\xfe-;2\xba<\x12\xde\x96\xa3\xd2[\xa6\x02|#\xab\xd1\x9fPu$\x8c\xe9(\xb4\xfbwn!Q\xa5\xcar\x82vg!\xf5s\xe2\xd4\x8b\xdb\x87pI:BN\x8b\x9c5\xce\xe5X\xd4\x0fe\x9d\xff\xea\xb0l,]Z\x01(\x01",
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
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_06593a9ea7951926006916133437908193afc85e5604f85aaf",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
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
