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
            "params": {"thinking": {"level": "none"}},
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
Here's a summary of my thought process:

**Calculating the 100th Fibonacci Number**

Okay, the user wants the 100th Fibonacci number.  That's straightforward enough. I recall that the `default_api.compute_fib` function is available, and, from experience, I know this is designed for calculating the nth Fibonacci number. Therefore, to solve this, my plan is to immediately call that function, supplying the input 'n' as 100. Simple!
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
Here's a summary of my thought process:

**Calculating the 100th Fibonacci Number**

Okay, the user wants the 100th Fibonacci number.  That's straightforward enough. I recall that the `default_api.compute_fib` function is available, and, from experience, I know this is designed for calculating the nth Fibonacci number. Therefore, to solve this, my plan is to immediately call that function, supplying the input 'n' as 100. Simple!
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
                                "thought_signature": b"\n\xd5\x01\x01r\xc8\xda|u\x89up\x10V\xabg\x83b\xeb\x8cu\xfc5\xe5X\xaf\xa6\x07,\xda\xa8O\x1c5\xc0\xa0\xe06\x08\xe5\xbb\xca\x85\xfbM\nJ\x80\xdf\n\x8c?\xa21R\x06^\x981N(\xe0\xc2\x943\xd3\x1f\xf9p\x8a\x870\xc7E^\xb4/\x7f\x89(\xa2\xd9\x97\xba}?\xa8\xd0\x8f\xeaS`\x05<3\x85!\x9c\xc7{\x96\xb8\x84\xefE\xec\xdf\x00K=\xb7\x96\xc6\x15w\x85\xe4\x91\xf9\xa7L\xb6\xab\xfc\xa6e\x81H\x9a\xa7\xbf8zRh \\\xca&\xd3\xf7/SZ\xc9\xbd\xf7\xe5W;X?\xa9P\xbfd\xf0\xc7yEtqB\xc2\xc4\xcaI\x94\xe6}/\x8e+9\xbe:\x1c^\x98\x0f\xe2\xc8\xe8\xed\x8a\x0e\xdbIE\xa8\xeb-Y\xc4\xb4$*^\x15\xd5F\xa3\xd6\xb4a\xef\xa2-R\xee\xc0\xfe1\xf3$@",
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
