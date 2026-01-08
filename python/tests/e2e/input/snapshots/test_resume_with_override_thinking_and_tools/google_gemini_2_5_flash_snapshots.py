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
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 122,
                "output_tokens": 38,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=38 candidates_tokens_details=None prompt_token_count=122 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=122
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=160 traffic_type=None\
""",
                "total_tokens": 160,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought='The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.'
                        ),
                        Text(text="I'll compute the 100th Fibonacci number for you."),
                        ToolCall(
                            id="toolu_01CjFzbAZRjYvqVoXGRET7ZX",
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
                                "signature": "ErUDCkYICxgCKkBu3sY/7ZuUOcbiLFXGUIPtQ96joTBhtL6mSUbAAiXw+fGhn5Inf6ahCEc4YPLvNE/oEG94XNHLzQLE5Wb3r1AsEgwO5fdJWVC/HC4w620aDG1I8rKvTNjmDXVciCIwFfnbOabYIPTQXCb2FMnpyVv+LHxmXUZa+vZMgYNlPTqx+/loctbacaIrx2zk0+P6KpwCV4CQqBWN1nxkTe4bDOe9L2nlwuzyOzl1QC/QnW03+LlmTn8o5HOZasALRgskJVQ2XlIt+phB894/5yCLDHrilBhUKeLzZqJpjrW5n90A+ZAGcc7kE+qlp2hM4TYqMwz0KbbrZIW6B4Q8tfqqYbODm3xHIAO/pjjLH4r9wV6M5Tyjvivx8+wf3HHGxXWPh3PnPtSannMXpg/jMDjRHXT+el6fghY9R6tnBdgB4VLPRKJyup1MxCvtCwF5Eqjkyy6Fui/PJ28MMOVZEUgi/pa0aaovd2X9VT5R3gVnsurJY/O4yKXNsJRd3QUEAAcybBl8yfUfmkdnL7Zl+Oqu+YObQe2y35Y2r3VxGRUEbAgCbt1pkMiHpJB1zxPcyj4YAQ==",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.',
                                "type": "thinking",
                            },
                            {
                                "citations": None,
                                "text": "I'll compute the 100th Fibonacci number for you.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01CjFzbAZRjYvqVoXGRET7ZX",
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
                            id="toolu_01CjFzbAZRjYvqVoXGRET7ZX",
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
