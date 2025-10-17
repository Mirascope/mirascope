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
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="""\
**The Fibonacci Challenge**

Okay, so the user needs the 100th Fibonacci number.  Fortunately, I know that `default_api.compute_fib` is the function to use for this kind of calculation. That's a no-brainer.  So, I just need to call that function with the input `n=100`. Simple and straightforward. No need to overthink this.
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
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": True,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
**The Fibonacci Challenge**

Okay, so the user needs the 100th Fibonacci number.  Fortunately, I know that `default_api.compute_fib` is the function to use for this kind of calculation. That's a no-brainer.  So, I just need to call that function with the input `n=100`. Simple and straightforward. No need to overthink this.
""",
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n\xee\x01\x01\xd1\xed\x8ao\xd6f\xb0&\xa3d\xe66Q\x0cZ\x96<yfw4u*7us5\xd0y\xb6\xa61\xa8\xce\x1eq\x12\xedq+\xf9\xccd\xfa\x972\"\xa4\x8a)`\x12\xe8\xc2b\xf43\x9c\xb5:\xca\xf6\x11\x91\\\xfe>\xfa\xf7yl\xe9l&\xe8r=+\x98^\xe9R\xc2\x9a\xcc\xb6\xfe 7\xef/\x03\xe5\xd1\xbb>\x99\xac\xa5\xf0>\xf9\x8f\x8f\xe0k1\x9bR0\xb3\xa2\x84\x17\xe1\xa8i\xc1\xe8]:\xef\x93/\xd9(\x9f\xb3N\x0e\xc7Z\xcb\x03\xca\x03\xbe6w7v\xfe\xd2\xfaC4\xae,C\xea\rP\xcaL&\xca$Y\x96-l\xef\xf6t\x94M\x81\xcd\x15Ct\x82\xd2\xa1\xfd\x8d\xcbc\x18\x94F\xeb\x84J\xbb\xe8\xdb\x8ca\xd5'\x9e\x1bP)\x9d\xfe\xc5/\x19\xfa\xa2%\x1b\xea\xee\x8a\x14\xefp)\xd3y\xefk-z\xf3P\x8e\x96D\xe4\x07\xfbd\xd3Uv\x84\xa8\xc7O\x8a\x9a\xd0\xee",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"n": 100},
                            "name": "compute_fib",
                        },
                        "function_response": None,
                        "text": None,
                    },
                ],
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
                        text="The 100th Fibonacci number is 218,922,995,834,555,169,026. This is a very large number with 21 digits!"
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": "The 100th Fibonacci number is 218,922,995,834,555,169,026. This is a very large number with 21 digits!",
                        "type": "text",
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
)
