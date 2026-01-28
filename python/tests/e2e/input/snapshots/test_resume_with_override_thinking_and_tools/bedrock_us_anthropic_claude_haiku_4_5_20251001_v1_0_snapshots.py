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
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_model_name": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 660,
                "output_tokens": 26,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=660, output_tokens=26, server_tool_use=None, service_tier=None)",
                "total_tokens": 686,
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
                                "thought_signature": b'\n\xb6\x02\x01r\xc8\xda|\xb0.\xf4\x7f\x83\xddq\x9a\xfc=\xd5H\x8b1\xb5h5\x92\x11\xb1m(6\xbf\x8f\\\xbd{_\xcf\x18\xa85\xd8\xa8R\xc8\x9f\xcd\x01\xed2\xd4\x84\xfa\x96\x12\x1f\x98_\x0b\xdaW\x1b;\xee\xd4!\xf6KC8 @\xa5c"&\xd8D\xd2rr\xfb\x81\x90&\xa17\xf5\x88\xf3?&\xf2\xb0\xf5C\x0b^\xa5D\xfb\x1d\xf4\x9f\xdc\x19\x9e\xca\xdc`\xd1\x93g\xb5\x191e\xafR\x1a\xe7\xd2\xc9b8\xda-jA\xff\r\xe8\xb2\x1c\xcb\xde\x90)SR\xa2]1\xa6w*\x82\x1aB\x10!\'x\x84\x1dxJ\x96\xa1+\xbb\x08(\xcc\xa3j\xa8s\x181\x9e\xa089X\x93\xb8\xf7a\x9b\x93u(\xc3\xf9\x04dy5G"\x85\xe4\x11\xc2\xaem\r\xe7`\xb0\x1d%\x11\xfc\xb9\xdc\xb6a\x13\xcd\x1f\xe0-e\x1b\xb5*\xa1\x97E\xfb\xb87Y\xdeH\xd7\xa1*\x16\xc2Kd\xa8E\xb0\xe9|\xb5m:\x17:\xd9\x8a1\x01D\xac9\x9eP0b<\xe3\xb5.\xf5\x8c\x1b`\n\xa5P\xd7\xd2\xb8\xa2\xfb{a\xfb\x91\xabA\xa7>p\xf1\x87q-\x13\xb7\xf5t\xfb\x10m^`Y\x11\x8e\xf3\x0c\xc7\xdcS\xcfF\xab\xb1MlV\x91\r0ol',
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
                            text="The 100th Fibonacci number is **218,922,995,834,555,169,026**."
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    provider_model_name="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "The 100th Fibonacci number is **218,922,995,834,555,169,026**.",
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
                    "strict": None,
                }
            ],
        }
    }
)
