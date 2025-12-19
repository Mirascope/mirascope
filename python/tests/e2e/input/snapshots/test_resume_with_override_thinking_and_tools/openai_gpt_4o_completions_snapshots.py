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
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 91,
                "output_tokens": 23,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=23, prompt_tokens=91, total_tokens=114, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 114,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**Let's Calculate That Fibonacci Number!**

Okay, so the user wants the 100th Fibonacci number, which is pretty straightforward. I immediately recognize that `default_api.compute_fib` is the tool for the job.  No need to reinvent the wheel, I can just leverage that existing functionality. The solution is simply to call that function with the input parameter `n` set to 100.  Efficient and direct - that should do the trick.
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
**Let's Calculate That Fibonacci Number!**

Okay, so the user wants the 100th Fibonacci number, which is pretty straightforward. I immediately recognize that `default_api.compute_fib` is the tool for the job.  No need to reinvent the wheel, I can just leverage that existing functionality. The solution is simply to call that function with the input parameter `n` set to 100.  Efficient and direct - that should do the trick.
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
                                "thought_signature": b"\n\xe2\x01\x01\xd1\xed\x8ao\x03Q\xf9\xda\xec1'-oCu\n\xbc\x9f\x87[\x12\x88t\x15\xbf\x81\x13\\\xf4Q\xde\x10\xa2\xf5\x1dE\xe3\x8e\\0>a\xfauT\x15\xe6T\ra:\x05\x94u\x84\x0c:~\x08\xd2\xcb\xd9)\xe1w\xcc\x8d\xd7\x1d* \x97k\x8c\xe2\x18\x81\xa0\xd7\xd3-><\xbb\xb4\xa0\xe6\xe3|\xacH\xfaL\xc0\r\x96 \xc5\x1d%\xd0\x19\xac\xd7\xb3\xce\xf94\xb5\xc4\xe3%\xea\x8c\x85\x96O[dNaU{\xc3\xd1\xe8\xc1\x92\xf6\xa0\xecYF\x8f\xf4\xa2\x96A\x87\x0e,\xcb<\xa1\xf9:\x10^\x16|\x1c\x02uML\xe3\x86%{4\x1a\xdb\xe5r\xd1\xd0`\x9es\xa7\xf5\xe6\xb3\x01\n7\x07g\x92\x06+\xa5\x9d\xa5s\x18O~n\x175\xeb\x1c\xc4m\x8d\x0bpG\x15*\xf6/\xe5\xe3=\x1dhz\x96\xff?\xb9\x93B\xcf\xf3g\xd4Xr\x81w\xa6F",
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
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
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
