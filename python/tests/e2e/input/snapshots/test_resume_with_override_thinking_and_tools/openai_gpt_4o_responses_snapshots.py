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
            "params": {"thinking": {"level": "none"}},
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
Here's the summary:

**Calculating the 100th Fibonacci Number**

Okay, so the user wants the 100th Fibonacci number.  That's a straightforward request. I recall the `default_api` has a function specifically for this, `compute_fib`. The parameter to that function, which I need to call, is `n`.  It looks like `n` represents the index of the Fibonacci number we want, which in this case is 100. Therefore, I need to execute `compute_fib(n=100)`.  That should give us the answer directly.
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
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
Here's the summary:

**Calculating the 100th Fibonacci Number**

Okay, so the user wants the 100th Fibonacci number.  That's a straightforward request. I recall the `default_api` has a function specifically for this, `compute_fib`. The parameter to that function, which I need to call, is `n`.  It looks like `n` represents the index of the Fibonacci number we want, which in this case is 100. Therefore, I need to execute `compute_fib(n=100)`.  That should give us the answer directly.
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
                                "thought_signature": b"\n\xb3\x04\x01r\xc8\xda|\x9f\xeb\xe3\xae}4\x8ai9\xd3!b\xa2\t\x03\xb9\x98P\x9d\xa0\xeeS\xa7\xb5\xbb\x82\x1aYO\x15J\xe3\x99\x84[]'\x8c5\xe0\xfb\xeaf3\x03\x14\x8dS\xc0\xc7\x97EmqR@\xf0\xcf\xe3~\xea\xab\xc0A\xf3\x1a\xce+\xc2\x17\xae\x04\xe0{\xbd\xa5\xf6>\t\x10\x00\xe9\x00\xd021\xc6,\xac9\xc3\x8dmRA4d\xad\xeb\x19\x8fo\xf9\xe5\xd1e\xe2\xb4\xdd\xbe\n\x11?\xf9\x95\x9c\xa3<\xe1\x11j\xf9\x1cN\x01\xac\xdf\x8ePa\xcd\xfb\xeb!\xd3\xd7n\x82mR\x1a\x8a\xf4\xf0\x7f*P\x12\xae\x17\x1f\xf36\xa0\x01\x96\xbdN\xf8\xc1\xba\x06\x1em\x8ci$\x7fZ0\xd2E\"\xaa@\xd7*6\xce\x08>\x13?\xb6\x89M\x02`\xbf\x1b\xaf\xa1\x9eF\x11\x85$b\xf7\x1dT\xf8?\xa8]\xaf[klxg\x80\xe2\xa1u\x89\xe3\x8fxN0\x0f\xf7AF\xc6N\x8a=\x07\xe8\xa6\xb2\xa9\x87\x11\x03\xcfm\xbb\xb7\x9f\x0e\xff\xa4\x85^X+2\xfa\x05t<+w~z\xc7\x1b+0L\xef\x8f\xbbRH\xd2\xd4zPj\xaft \xa5(\x8d\xc0\n\x0f\x8a\x90ES\xc8\x1c\x16#\x8c\xca\xde{\xff\xd7#3>ec\xf9\x18;`\x92\xc9\x14f\x00\xb8\xc5\xbf\x93\x12N9\xd9\x94\xa9\x8fzw\xb1]8\xeb\x04n\xaf\xe9\xb1}X6Wc\xbfN+6l\xc80\xfc\x10\xb1\x9d\xe3wp\xc6|\xd3~\xf5S\x8f\x9d\x9a\x11`\x91\xf3\x9d\xf1@\xaeI8\xdd\x8bG\xe8\xd0w\xa6\x17\x95\xb3\xd8\x8c\x8dc\x917\xfc\n\x0c\x00q\xea\xc4[<\x0c\xc3\x8e\xdd\x1e\xcc\xd1\xa1\xc34\x08j\xa6\x1a\x8b\xd6O\xbfe\xc9>\xba\xe9<\x93}}\x11\x85\x95<\xb6\x02\x9b\xb2A_\x1f0HI\xac+X\xf8\xa1\xd3~d@\xc6\x1c\xc2\xe3\x84A\xb5\x16\xca\x8a\xda\xb3\xd7\xf7\xde\xa9R~\x07\xbf\xb1\r\xc8x\x02\x00\x10ihB\x9c\xeb\xfa\xfc\xfe\xc6n\xc1\xfa\xcdZ^W\xe2\x8f\xf8\x9d6\xc6b'\x1c_\tc\xe1\x07\xd1\\\xe8<K\x04\x11 \xdf+\xb5*\xfb\xf5(\xe7<\xe2:\xe8z\x80]5\xba\xe1\xd7\xc2\xd5\xb7\x05\x8an\n\xd1\xbd\xa2h\xca\xa0\x1a6\x1a\xf4\xcbTi\xf2\xe9\x97\x7fJ\x0e\"\x9b=",
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
                            "id": "msg_0d910b91893210890069605786859c8190b7badae44dca89e3",
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
