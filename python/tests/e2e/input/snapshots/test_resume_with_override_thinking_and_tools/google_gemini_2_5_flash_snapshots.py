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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 122,
                "output_tokens": 32,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=32 candidates_tokens_details=None prompt_token_count=122 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=122
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=154 traffic_type=None\
""",
                "total_tokens": 154,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Text(text="I'll compute the 100th Fibonacci number for you."),
                        ToolCall(
                            id="toolu_016feRCAQERKZe9apWg1fnsJ",
                            name="compute_fib",
                            args='{"n": 100}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "signature": "EqsDCkYICxgCKkDlyJ5F08q1ul9N4Sb7iho/bgJZqZyZFMHOcP/PFmTtBbupvF+V+BTnFU1xGUzM91yvi92HufLaHM9v5xXkFVeiEgzQY/S7aAJcMjBF3JEaDIYqzR5QP5f/piK0fyIwf6R6YIzh43EeI0J6fO/kNWBHNDGqS3W255JX4E0BQ5w58YR7QPw+wDYLqa2V9nFmKpICUjBPYDVQY2TSJEORcPnDTEBCH4D7CWCGDj40MB1+SU3EuRt/up+caQQ3/sP69cQmWJQF9mfES4e2OsK4n9kkEoYhs7EgL7hEjs6r8xAzALkf7XfApmBTLdvakuPu66eme/swjT0D0YyyLxwyFGg8OcnfW6d2r9o6HiGyjaGgI1ceAKa3ZCeEvSdqGXELepRoNRZVUpQbS/wvDTMp9RutnmcWljez4DoN85s/FfnMWt9yq8fIRES7QK6cBqvP5KauP1RfEeaRcbZmOLvRfKglXDr2zuSklsxQ29ptEotIvXshl3gBFVZJvCCdJSydpv6FbhfXKt0ZCxqRMWr5IhkLArkioDjAji/Cy+ae8H8jdfzOohgB",
                                "thinking": "The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the value n=100, so I have all the required parameters to make the function call.",
                                "type": "thinking",
                            },
                            {
                                "citations": None,
                                "text": "I'll compute the 100th Fibonacci number for you.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_016feRCAQERKZe9apWg1fnsJ",
                                "input": {"n": 100},
                                "name": "compute_fib",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_016feRCAQERKZe9apWg1fnsJ",
                            name="compute_fib",
                            result="218922995834555169026",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The 100th Fibonacci number is 218922995834555169026."
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
                                "text": "The 100th Fibonacci number is 218922995834555169026.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
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
