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
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 178,
                "output_tokens": 23,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=23, prompt_tokens=178, total_tokens=201, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 201,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Solving for the Hundredth Fibonacci Number**

Okay, so I see the user wants the 100th Fibonacci number.  That's straightforward.  I remember that we have the `default_api.compute_fib` function available for just this kind of calculation.  The description is pretty clear: it takes `n` and returns the nth Fibonacci number.  Since we need the 100th, the solution is simple - I'll just call `default_api.compute_fib(n=100)`.  No need to overthink it.  This should provide the answer directly and efficiently.
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
**Solving for the Hundredth Fibonacci Number**

Okay, so I see the user wants the 100th Fibonacci number.  That's straightforward.  I remember that we have the `default_api.compute_fib` function available for just this kind of calculation.  The description is pretty clear: it takes `n` and returns the nth Fibonacci number.  Since we need the 100th, the solution is simple - I'll just call `default_api.compute_fib(n=100)`.  No need to overthink it.  This should provide the answer directly and efficiently.
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
                                "thought_signature": b'\n\xe0\x01\x01r\xc8\xda|\x89\xe4\xb0n\x84o\xa0g9w\xfeJ\xa7>\xc8\x9a\xbf\xd1\xf2\xff\x02\xbc$\xfb\xc6\x0b~%\xfa\xbc\xa8\x01E4\x10AT>\xc9\xddtv\xdb +"\xda\xcb\r\x98\x99\x8e\x0e\xaf(\xe5iUF\x1b\xfaM#c?\xdfP\xe7\x89\xfbU{t2\xc1\x84\xbc$r\x9f\xc9\x0bl\xcb/T\xd2\xee\xdf\xd7\xf0m\x13\xf0\xc7\xdbK@\xa3"\x11\xd1\xf8\xff\xc9\x15\xbc\x8d\x92\xe0\x86$\x13\xd8\n\x12\x17\x10;6\xa4\xf8\tq6\xea\xd2n\x8c\x9fJi\x05<\xe0h~E\x19\x98\xa1\x8e\x1c5G\x0br\x90\xcd\xc2\xca\xb4Z\xd2<a\x98H)En\xef\xa0.\xd4trX\x05\x1f\xc8\x98\x08.\xab\xa5zoj\x9d\xd6]\xdd\x0c\xf3\x8c\x9d\n]\x8c_\x87\xb1\xdb\xc4A;\xc6\x84u)U\xc6N\xe5\xa0\xe9\xa9\xc9N\xa0\xa7\x0e/\x81+\x1f\xc5)',
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
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "content": """\
The 100th Fibonacci number (1-indexed) is:
218922995834555169026\
""",
                        "role": "assistant",
                        "annotations": [],
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
