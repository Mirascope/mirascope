from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.'
                    ),
                    ToolCall(
                        id="toolu_01Dd13RUEBzJzpRgqdvoG1cY",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "signature": "ErUDCkYICBgCKkBu3sY/7ZuUOcbiLFXGUIPtQ96joTBhtL6mSUbAAiXw+fGhn5Inf6ahCEc4YPLvNE/oEG94XNHLzQLE5Wb3r1AsEgwbYhMO8TDFEJUBby8aDO2PbChDNrBTEn5fyCIwflStxhLS+gCC6G6WOn1m/IzDYD3R2/ttJwJxa0IQjIYQXQgAWvx+smDlFTmSLIqEKpwCfMbFLB1lH8pp8daIF2RN45jLNaKIVr16okin2HbGbzi8k4ssuhG6WYKhPsC1tAuDhL1TFCPiDdNYsUB4XigfJA0loy2AByeuRR9kaY0tT5PS3smlhO+4CCVVtl8LJRBjIYq4epW+59xXAIbUzF1JOM3n4TLmBACety9oFe4PeSXGPVl+oXce5jz9uqOhIRR/Rg4xTd5lDr4OdEgy4LUps6zwe4wLgsPnMWJdPhdE4xKF0pgdfWdk5oogG1rNRSlxyPo7aiWWnWJXs3iXJ54YaMMdylosNr/HEQkt01QJX941YBMKXse+X21L8+UuK8Vf3VR1qgQyM+4Sg5lza59hqglMO8znIHiapdhqw0n7pCkh1Bth44bm2xapB9AYAQ==",
                        "thinking": 'The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.',
                        "type": "thinking",
                    },
                    {
                        "id": "toolu_01Dd13RUEBzJzpRgqdvoG1cY",
                        "input": {"n": 100},
                        "name": "compute_fib",
                        "type": "tool_use",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01Dd13RUEBzJzpRgqdvoG1cY",
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
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0a2f95d621dbe8000068f007ccea548195b8e85bc60bc942ee",
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
)
async_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.'
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_01J3niP9s22AJczND2cmTtAh",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "signature": "ErUDCkYICBgCKkBu3sY/7ZuUOcbiLFXGUIPtQ96joTBhtL6mSUbAAiXw+fGhn5Inf6ahCEc4YPLvNE/oEG94XNHLzQLE5Wb3r1AsEgyanm45KTfzPaKtcPYaDASufmXL6WOvzsj+oiIwdJScHAdRl/Pa2nyOUx4itX9K/XJNSrXuhnFrvrnOuxGpj62WPYI8/XimED5teInFKpwCMletN76xv7b/Xy3+XuoL/j3DErLKo3LFKmDT3SKprpm9sDWajo4CnF8SjkGpfzldNYXdjq6n0I+f8fXo0Q+4oFhKBiyp41iX1+cY6kWEuBNznH1l7TvQRz8qFI0pAGEmB2fcGrPjgiSTf2lnkN69F+M+zsgk0l92g9cqJASqwZmCL+HvKUnNOAC6VwSsZvqfciMn5NgtYIW9Zx5kWToXojSDaVuwxPq2P7xz7T0X7u+A1fQsGDc3xh631sER+NCTYYvik2KFHcYkF4OAgG/UDAHPjQxElhAQU/7kQg2qEDo8IaG41cxrNZlKBJ7sGDkgBKoHqP6N3kDY2nryWt2dLE2VD1trWm9hFKjgVtkHpiE1UU6lAEfTMgBuDZoYAQ==",
                        "thinking": 'The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.',
                        "type": "thinking",
                    },
                    {
                        "citations": None,
                        "text": "I'll compute the 100th Fibonacci number for you.",
                        "type": "text",
                    },
                    {
                        "id": "toolu_01J3niP9s22AJczND2cmTtAh",
                        "input": {"n": 100},
                        "name": "compute_fib",
                        "type": "tool_use",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01J3niP9s22AJczND2cmTtAh",
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
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_06f6f84c41f64e330068f0089e64a08196a8d18c2935bc920c",
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
)
stream_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.'
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_01PrXQWqFwyoFUBK5G9a6Y2r",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01PrXQWqFwyoFUBK5G9a6Y2r",
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
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_003a576e151e08f90068f008af47cc819399862b611b4ba095",
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
        "n_chunks": 24,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.'
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_01TdncDnHvvqXioK1wZWVjmU",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01TdncDnHvvqXioK1wZWVjmU",
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
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_04356c907a7fab870068f008c2c58481948beefff174ec0c8a",
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
        "n_chunks": 24,
    }
)
