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
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 496,
                "output_tokens": 48,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 544,
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
                                "thought_signature": b"\n\xeb\x01\x01r\xc8\xda|\xe49<\x00\xe2\xd7\xb9q/\x0b\xb6\x1ek\xb3 \x17\xe2<\xe8\x88\x0cc\x80\xfar\xb4Qf\xe85\xaen\xef\xde\xb0\x1e0\xf3MP\xf7\x0c\xa2\xc8$5c\xf7\x83\x05\xe3\xbe\x82s\x85\x0e\xed9\xd6.j\x0f\xe2\x14\x13\xf29O\x1d\xdfH\xb0K\xe1!\x81Yr_\xa8.n9$]\x16d\xdc\x13\xfb\x05\xc3\x14\xe6J\xc2\x877k\x00\xe3v\xd4O\x80\xc6|\xe9\x8a\x82\x14\xbc\xd9\xe3|\xb8\xaaB\xfb\x85s\xa9s!\xb3\xbf\x06?\xf2@\xa9\xae\x94\xd3C\xaa\xbf\xfcT\xb1\xfc\xddN\xea\x94\xda'\xd9h\x12}\x7f\xfdU\x16\xa3\xba\x1a$PM;\x8a\x98\xb8\xbbk\xa2\xeeBI\x8e`>2\x1ek}\x1e\x1c\x8b\xf4c>\xf4\x0b\x05/\xe9x2\xa8S\xdd3\xdaW\x97\x07\x02$j\xb8_Xe\x8cK\"\x01k\xe5]\xe5\xc9\xb7M\xe3\x0c\xea\xae_f\xfd\xd6/\xf7q\xe1\x18",
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
                            text="The 100th Fibonacci number is 218922995834555169026. This number is quite large due to the exponential growth characteristic of the Fibonacci sequence."
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
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
