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
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Solving for the Hundredth Fibonacci Number**

Okay, so I see the user wants the 100th Fibonacci number.  No problem.  Fortunately, the documentation clearly states that the `default_api.compute_fib` function is designed for precisely this kind of calculation.  The input `n` determines which Fibonacci number we're after.  Therefore, to get the 100th number, I'll simply call this function with `n=100`.  Straightforward and efficient.
"""
                        ),
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            args='{"n": 100}',
                        ),
                    ],
                    provider="google",
                    model_id="gemini-2.5-flash",
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
**Solving for the Hundredth Fibonacci Number**

Okay, so I see the user wants the 100th Fibonacci number.  No problem.  Fortunately, the documentation clearly states that the `default_api.compute_fib` function is designed for precisely this kind of calculation.  The input `n` determines which Fibonacci number we're after.  Therefore, to get the 100th number, I'll simply call this function with `n=100`.  Straightforward and efficient.
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
                                "thought_signature": b'\n\xe2\x01\x01\xd1\xed\x8ao\xc9"\xb2\xd7\x84\xe7z47\xf5\xbe\xdc\xaf\xcc\x01\xfa\xa7Z\x03\xdf\x00$\x80\x00\x00\xd3\xa6\xfd\xe2\x92\x8d\xae\xcc\xc1\xb2\xcc\x8c\x0f\x02\x88\xe7c}\x1fc\xd0)>\x85h\xe2\xecTW\xda1\x14\xae\x1c!D\xc2Y\xc4\x88H\x18d)\x82\xe8 \xc0\xf1R\xe3\x82\xe0Z\x0fc\x84j\xeb+\xcf\xa0\x19*\x97M\xb4r\xe0\xfc\xf1\x16\xd7\x81\xf0\x01\x03\x82R\xb7\\\x16_%YW\x84\xb6\xdc\xad\x9dw\x07L\x11b6\xafxv\x8a\xfd\x1bN\x12\xa0\xa8\xe9T?}\x8d\x13\xc9$\xb4\x8cb\x9e\xb4r\xd6\xb8\xe6\xba\x8c\x8bLd&\x1b\xedKO\xf2\xa3>\xc1P>\xb7\xc7\xf5\xb4\xe1\xdf\xa8k\xaf\xaf?4j<\x13\xf9\x90V\xd4\x18C\xc2\x0eL\xa4\xee\x10Bo\xfa\xc7\xd3\xa0\xfe\xb6\x1d"\xbe\x80\xea\x0b\x0f\xe2\xc2!\xd1\x18S\xb5IV\x95\x13\x8b\x9e\x9f',
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

This is a very large number with 21 digits! The Fibonacci sequence grows exponentially, so the numbers get quite massive as you go further along the sequence.\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
The 100th Fibonacci number is **218,922,995,834,555,169,026**.

This is a very large number with 21 digits! The Fibonacci sequence grows exponentially, so the numbers get quite massive as you go further along the sequence.\
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
