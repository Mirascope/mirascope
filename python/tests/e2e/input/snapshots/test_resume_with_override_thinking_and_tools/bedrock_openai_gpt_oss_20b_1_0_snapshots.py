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
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 176,
                "output_tokens": 119,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=119, prompt_tokens=176, total_tokens=295, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 295,
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
                                "thought_signature": b"\n\xe2\x01\x01r\xc8\xda|v\x1c\xdd2\x80DF\x88_\x9a\x8bO\xdb\x11)\x8bUW\\W\xc5\xbd\xfa9}\xc2K\x15\xad\xe4\xe5=\xe4u{\x1f\xfc'1~L\x05\x0c'\x91m\xd2\xd42\xde\x94\xd7\xa7L\x9eZ\xad\xf4\x87>\xff8\xd21\x0c\x96[3\xfe{\xef\xf2\xad\x06S\xdbyW\xdb\xbe\xa4m\xfa \xed\x18\xe5}\xac\xa8\x16\xfb0K\xadau\xc7\x18[@\x08\xd0\xb1\xbc\xbd\xc1)wC\xff\xba_\xa6\x96(\x18\xefS\x10#\xb0E\xb4\xfa/Vv\x14\x90\xa6\xe8M\xc0N\xdb\x1f\xaf\xca\x00\r\x1e\xa2\x93\x06aV\xcf\xbc\x97\xb1\xbdi3\xbc~\xb0c\xf3\"\xf6\xf2'\x1d\xd86\x97\xe1\xbfa\xa2I\xe5W\xb6he|\x9b<\xffMH\xc9\x04\x83g\x90\xc0\x00\xd8\xf3\xf1\xecv}\xb8\x08\xf20\xcd\xbe E\xad\t\xaczSCf\xe0\x15\x00\x0e\xa0\x7f\x18\x0f\x1d\xf4",
                                "video_metadata": None,
                            }
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
                    content=[
                        Text(
                            text="""\
<reasoning>User asked: "What is the 100th fibonacci number?" We gave the number. That is the answer. Probably show it. And mention maybe 1-indexed. They might want the answer. We'll respond.</reasoning>The 100th Fibonacci number (using the usual 1‑indexed definition, where\u202fF₁\u202f=\u202f1,\u202fF₂\u202f=\u202f1) is:

**218\u202f922\u202f995\u202f834\u202f555\u202f169\u202f026**

(You can verify it by generating the sequence up to that index.)\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": """\
<reasoning>User asked: "What is the 100th fibonacci number?" We gave the number. That is the answer. Probably show it. And mention maybe 1-indexed. They might want the answer. We'll respond.</reasoning>The 100th Fibonacci number (using the usual 1‑indexed definition, where\u202fF₁\u202f=\u202f1,\u202fF₂\u202f=\u202f1) is:

**218\u202f922\u202f995\u202f834\u202f555\u202f169\u202f026**

(You can verify it by generating the sequence up to that index.)\
""",
                        "role": "assistant",
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
