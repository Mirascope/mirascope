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
            "provider_id": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "provider_model_name": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
**The Fibonacci Quandary**

Okay, so the user needs the 100th Fibonacci number.  That's straightforward enough.  Thankfully, we have this handy `default_api.compute_fib` function at our disposal.  Perfect!  It's designed to calculate the nth Fibonacci number.  All I need to do is call that function and pass in `n=100`.  That should give us the result we need. Simple and elegant.
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
**The Fibonacci Quandary**

Okay, so the user needs the 100th Fibonacci number.  That's straightforward enough.  Thankfully, we have this handy `default_api.compute_fib` function at our disposal.  Perfect!  It's designed to calculate the nth Fibonacci number.  All I need to do is call that function and pass in `n=100`.  That should give us the result we need. Simple and elegant.
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
                                "thought_signature": b"\n\xe2\x01\x01r\xc8\xda|=\xf4u\xbf\xf9\xc0\x1d\xcd}\xf1\x9a\x15[\xb3\xeci\r\xb7\xa2\xb6)3\xdf9\xeb\x92\x92'\x0bP\xdc;\x90\x1f\x85s\x88N\x188\xf3W\x9f,\xbf]\xeb\x19\xa9\xb9G\x7fg\xf1\xd2\xcf\xcb\x14\x95\xc3\xc8q\x05\x8b'\x1a\x03c\x8e\xf0\xc4v/\xf8\x0e\xfe&2S\x03\xd8'\xa5F2\xbd\x12~\xa2\xefY6\xdfb\xb4\xf9\xa7\xa7\xf9\x8d\xde\xae^\x86\tw\x15\x7f\xff$\xddu`\xb1\xee/k\xbdl\xd4g\xf1\x89\xd2\xac\xee\x99\xc9\x0e6\xd2\xf5\x0f\xec'\xd8hr}\xb3\xc3\xbf\x1a\xe3\x1c\xb8\x07\xea\x994\xb2;`Y\xea\xb0\xc1\x0f\xc4\xf4\xe9q\xf8\xe7\xb8\tW\x0fK\xa3}\xca\xdd*H\xfb9\x83i?V\x87\xe0\xa4\x95\x97\xb7\t)\x10\xef\xb5\xb0:W'\xb1\xf39\x8a#\x05-\x92\xfd\x95\xe3=:#n\xc2\x879\xb3\xa9\xfaW\x1e\xcd\x82",
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
                            text="The 100th Fibonacci number is 218922995834555169026."
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message={
                        "role": "assistant",
                        "content": "The 100th Fibonacci number is 218922995834555169026.",
                        "tool_calls": [],
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
