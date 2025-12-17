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
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Let's Get That Fibonacci Number!**

Okay, so the user wants the 100th Fibonacci number, which is pretty straightforward. I immediately recognize that the `default_api.compute_fib` function is exactly what's needed here. It's designed to calculate the nth Fibonacci number, and the prompt directly specifies `n=100`. Therefore, the action is crystal clear: I should simply call that function with the input `n` set to 100. Easy peasy!
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
**Let's Get That Fibonacci Number!**

Okay, so the user wants the 100th Fibonacci number, which is pretty straightforward. I immediately recognize that the `default_api.compute_fib` function is exactly what's needed here. It's designed to calculate the nth Fibonacci number, and the prompt directly specifies `n=100`. Therefore, the action is crystal clear: I should simply call that function with the input `n` set to 100. Easy peasy!
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
                                "thought_signature": b"\n\xe2\x01\x01r\xc8\xda|\xff\xfe\xa8q\x9ah\xba\xa2\x9b^\xa3\xd3\xc8\x07\x16\x83\xd1lC1\xff\xa2e\x8a(\x83\x94\xe6Q\xcd\xb7\xd4E\xeb\x06\x82b\x07\x15r\x027Q\xdcH\xfa\x99\xbb\xe6\x02\xb8\n\x1di\xe3\x9a7\x03\xa2\xbc\xa4\xf7\x82\xe3\x89\xbe\xfe\xb2|\x0f\xb6i\xe8\xea$\xa6\x99\xb5\xc3\xde\x8f\xc0u\x9a\xd0\xa2j=\xed\xf1\xf8\x99\x970+Zyb\xac(\xca\x7fI\xa5\xa2\xd9\t\xe1X\x0bf+\x04\xed\xde\xe2\x9a&\xb3\x1e\xed\x17\x82\x94\x80\xc7o~\xe38m\x85\xdc\xc9;B\x1fi?\x84\xe1\x16GA\xfb\x85\xbd9TF\xe7\xb4\x10\xff\xeb\xcf\xf0\xef)BqD\xe1\xd8~)\xe0m5Pm\xe0+\xb2<\x18\xdf\xfa9\xe5\x0c\xd4\x96a\x81y\x14\x0e\xd9q\x11}\x7f\x83\x9a~\xf4\xea(\xa3\x84\xc3\x08\xfe\x0f\xe3\x1b\xd5\xbe\xff\xe5\r\x9foLit\xf4T\x939",
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
