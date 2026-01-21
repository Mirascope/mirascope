from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 178,
                "output_tokens": 11,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=11, prompt_tokens=178, total_tokens=189, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 189,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            args='{"n": 100}',
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
**Solving for the Hundredth Fibonacci Number**

Okay, so the user wants the 100th Fibonacci number.  No problem.  I know I have the `default_api.compute_fib` function at my disposal; that's designed specifically for this kind of calculation.  The prompt is clear: I just need to call that function.  The input parameter is `n`, which needs to be set to 100 in this case.  Easy peasy.
""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": {
                                    "id": None,
                                    "args": {"n": 100},
                                    "name": "compute_fib",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xe2\x01\x01r\xc8\xda|\xeePFS*\xe6$\xac\x08Ce\x07\xdd\x96>\xf5\x93>*x;9\xb0!S]\t\xb9\xfbX\x92\xaa>\x0b\xde,\xc4\t\xe4\x95\x1a\xa7\x91\xd3g\xb5n\xd8\xd6\x81|@8e\xd0'\xce\xe7>qs\xeb\xaa{\xa6l\x16\xc8:\x12\xa2\xae\xd7Dk\xb8\x1cq\xfc\xec+\x15\xfe\x19p\xeb\x82\xcfF\xc3r\xcc\xa2\x13\x0e\xd0\x93@\xda\xf6N\xbf\xe8\x8c#\xee\xe4y\xb2)\xaaDy5+\xae62\x9d\xc4*\xae\xd8\xbe\xe6\xcd\x95\"\xd0vs.\x9a3\x0f\x90\xba\x0b+7\x87>\t(\xb3\x07'\xff\xa3\xc9\xc6\xff\xd8\xbd\xb3\xa3\x07r\xfc\x81\xfd\xed\x0f4\xf7\x8c\xf2J\x8f\xa4f\xc5\x94\xb0\x85\xa5\x17\xf3\xbf\xa5\x17\xe0a\xb9\xf5\xb9|\xc9^\xf7\xfa<\xfe\xb9\xadr\xc6s{b\xce\xf8\xee\xaf}\xd1\x86\x10\xca\x0ev\xe31~*)U\x80\xfdZ\x83",
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
                            result="218922995834555169026",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="218922995834555169026")],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": "218922995834555169026",
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
                    "strict": None,
                }
            ],
        }
    }
)
