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
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {"thinking": False},
            "finish_reason": None,
            "usage": {
                "input_tokens": 122,
                "output_tokens": 32,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
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
                        Thought(
                            thought='The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the value n=100, so I have all the required parameters to make the function call.'
                        ),
                        Text(text="I'll compute the 100th Fibonacci number for you."),
                        ToolCall(
                            id="toolu_01KXqBWRjCb92pEDLMwsfkPX",
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
                                "signature": "EqsDCkYIChgCKkBT7oIGohP32ulgcIefSb6/LPBH9l4slTP8rDj/vjx/hHXP0qrU3q3UzFaJ9CdIMPgGA9N8UPCQjrDhhYPhtcMNEgxx9fRkZRRt8VpES1IaDONKBKhOfArHjrsRryIwsOB8tMXns1xHKuiw5nUVxrmgKG7aSUgVkLiTzc7ajNlewQckFNFyvXlrsIrd6138KpICXwjymuKI6f2oYEiSOhuqTvAMEaDsCAintBHezS3JnzDdoQmm3C5c8EXngKE1GBbPh88FKoAYp+gJAtKmLa3vplE7sKqpdDOeoERLOFC0s0PE/LM+YSm0LjBZ/xJym7M2iU1np2mCo1xE0UUpCVbhqHTMHfCL6xozo2glBCZXhYkpBYEG8f/6vIOEb5vf7Cuy64J4PYKeUDCMShp6gNcS3AX5MDivzDMyurrHD55522AmFMYn+shYMeJoth8g+DpwLAtgrgc6gVieAOMBg9xLcKiMOYhxPCHQ0djjlge3sZ6ehUK9zPAyVV4rOY1TbwhBbo4fiXL5eHwrD3/WUdhXOGGOZVkZ+i5PQShbkRfD59GZ1hgB",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the value n=100, so I have all the required parameters to make the function call.',
                                "type": "thinking",
                            },
                            {
                                "citations": None,
                                "text": "I'll compute the 100th Fibonacci number for you.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01KXqBWRjCb92pEDLMwsfkPX",
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
                            id="toolu_01KXqBWRjCb92pEDLMwsfkPX",
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
                    "strict": False,
                }
            ],
        }
    }
)
