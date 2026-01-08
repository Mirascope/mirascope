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
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 477,
                "output_tokens": 26,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=477, output_tokens=26, server_tool_use=None, service_tier='standard')",
                "total_tokens": 503,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
Okay, here's my summary, presented as a stream of thought:

**Calculating the 100th Fibonacci Number**

Alright, I see the request – the user wants the 100th Fibonacci number. Straightforward. Thankfully, based on my understanding of the system, I know there's a handy function for this: `default_api.compute_fib`. This function is *designed* to handle exactly this kind of calculation. So, the most direct and efficient approach is to simply call `default_api.compute_fib` and pass it the desired index, which, in this case, is `n=100`. No need to overcomplicate things; leverage the tools available. That should provide the answer they're looking for, pronto.
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
Okay, here's my summary, presented as a stream of thought:

**Calculating the 100th Fibonacci Number**

Alright, I see the request – the user wants the 100th Fibonacci number. Straightforward. Thankfully, based on my understanding of the system, I know there's a handy function for this: `default_api.compute_fib`. This function is *designed* to handle exactly this kind of calculation. So, the most direct and efficient approach is to simply call `default_api.compute_fib` and pass it the desired index, which, in this case, is `n=100`. No need to overcomplicate things; leverage the tools available. That should provide the answer they're looking for, pronto.
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
                                "thought_signature": b"\n\xe2\x01\x01r\xc8\xda|\xadV\xe8@\x06\x86@\xd4\xafIJ=/P\x9d\x94$mE\xe1\x82\xdd\xdaX|\x1e\xea\x86\x92\x1db&\x9e@i\x11\xd5\xf7\x90\x8a\xf3\x95\xca\x88\x9d\x92\x00\x0f\x81\x1e\xee\xc6}\xe1\x1d\x1a\x82\xd8\xc6\x7f\x8f\xd8\xe1\x9e\x03\xa3\x86\xdfqF\x13\xd7\x90\x90W/\xc9\xd5f#%\xb4@\x18\x88:\x9d@1G\x93b\xef\x8eC\x9c0:DK\x90\x04\x15\x15\x8ei\x15\xa3fW\xa7\xed4C\x88qyUu\xf9\x98\x98\x96\xf2R+r\x87Nw\xadp\xb2\xbf\xbc!\xf3\xe3\xd5\x83bQ\xcc\xad\xd4,\x84\xa1m\x86?;XL\x8d~\xb4\xf7\xd7\xe3Y\xc8M\xe3\xd5\xa4\x8dA\xfe\xdf\\\xef\xf6\xd8\x04\x8d\xc1>\x8d\x14\xda\xfaF\x81W\x87I\xd3d\xb7\x81\xa6\xbcP\xb9\xc8\x1a\xdf\xf6+\x0b\x1b{_I0{pdO\xdd'\xe8?4C\xad\x88\xea\x02\xab",
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
