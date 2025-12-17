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
                "input_tokens": 107,
                "output_tokens": 38,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought='The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.'
                        ),
                        ToolCall(
                            id="toolu_01MnLnuRr9SYqk4Nt4zvBopq",
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
                                "signature": "ErQDCkYICRgCKkC1U5aLDccw6hfKtcWrClCTiZ6M12W9sfSIILD3F5gCggCOaELdyMLcXBM4QIU+YK9MZn5ZMu5v1Rx8ibkKyrbXEgxN0vJibplcGc6LU58aDI1emmpMRP8L7LzYaiIwmx+BjJtfz6CmWato1sgn/SInbtCLCoMAWXe51nSsFPtvUqF4qeOxliYQQjcxG6HOKpsC+PFTKFloh3uZJU18TX8i9GvZOe6UvoO10NdIZflTrRoBEZIPkGEh0X/8L2qD/ZyWKM+u2N0V7DzcEy+RA0Bczo+pzYmTJQo/xYrg+tOon3aboix8zWZvzolQatvxG9YIUhK8NtPTsFpOOFHmcCb2/Ap+piNfT3AWzKTy3h23Daaz6srxOuaHaW03t3vS4x24pMMrIleTbUcKFa7e+Uh7dSmrwZO5zBxo6RjauZvz5fV/Hz6LOYGHPC8uQ6fSAOgA1wQaRNvcdVHZVdvbWAxfhXoKCEOIRQB1KrqNa/sbo+ru6uXPeBsetHrRmLO8ZU3ZghgLpSrKKWvrdG01frZVS6+fgtdr3alTVsIhyIxXichJxe38IzvsTJyV2RgB",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.',
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01MnLnuRr9SYqk4Nt4zvBopq",
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
                            id="toolu_01MnLnuRr9SYqk4Nt4zvBopq",
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
                                "text": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
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
