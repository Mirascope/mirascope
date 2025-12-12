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
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Let's Get This Fibonacci Number**

Okay, so I see the user wants the 100th Fibonacci number.  No problem. I immediately think of that handy `compute_fib` function in the `default_api`.  Seems like the perfect tool for this task.  I just need to call `compute_fib` with `n=100`, and I should have the answer in no time. Simple and straightforward, exactly how I like it.
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
**Let's Get This Fibonacci Number**

Okay, so I see the user wants the 100th Fibonacci number.  No problem. I immediately think of that handy `compute_fib` function in the `default_api`.  Seems like the perfect tool for this task.  I just need to call `compute_fib` with `n=100`, and I should have the answer in no time. Simple and straightforward, exactly how I like it.
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
                                "thought_signature": b"\n\xcc\x01\x01\xd1\xed\x8aoC>s\xdd\x7f\xa6\xeb\x01\xdf>R\x07\xddI\xc3\xe6x\xbb\xa2\xbd/\x8f\x1c\x05'\x12\x945\xecv6w<\x86\x9d\x89\xb6\xbc\xfd\x85m\xd9\xfb&\xa5MR\xe7]_\r\x16\x1c\x13\x18\xac\xe7\x95\xfcW\x90\x9e\x14O\xf1D\x97\xcb\x87e\xb9\x94R\x8d\xb0\xc4\xed\xf37#\xbb1\xdf\xae\xd7\xf0\xe39\xf3T\x01]\xfb:Q\xae@\xfc\x12;\xfdFj\x02!\x89\x02\x9ez>\xfaK\x940}f\xe2\xdav\xac\x1f\x14l\xffJ\xf0\x0c\xcb?\xdf&\xfb9'z|\xa4\x1a\xc0\x03OQ\x80\xcd\xd0\xd6\x92\xc9hi{f\x07\x1c\xf5X\x0e\x93\x8d\xdf\xad\xb5l]\x8f\x856\xb8V\xa3]!\x8a\x1d\x9b\xd7\xef\xc9Y)\xb6\x01}!\xd7\xb8]\xf8\xdf\xa7\x1bJ\x870\x81N&]@",
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
The 100th Fibonacci number is **218,922,995,834,555,169,026**.

This is quite a large number! The Fibonacci sequence grows exponentially, so by the time we reach the 100th term, we're dealing with a 21-digit number.\
"""
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
                                "text": """\
The 100th Fibonacci number is **218,922,995,834,555,169,026**.

This is quite a large number! The Fibonacci sequence grows exponentially, so by the time we reach the 100th term, we're dealing with a 21-digit number.\
""",
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
