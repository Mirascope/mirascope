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
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.'
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_011SpxgqXejF9h3wrt4SyaFP",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "signature": "ErQDCkYICBgCKkCsItOUHNinar+NABlYn+UTCEV462H15XiUdax8L7lhYMAvN2X2YxzcMd8Obghv+2Menhq/JUHTvDvU3gt3TiOQEgxVQmtvPwbACWlmQD4aDBFlaxR4JMosnW4A1yIwSwjMmJDn902+lH06Am/APOMC4B8Fz86quURxMGdaunSfdjvshCmgm0fyH5B+Q4kUKpsCwIzDz5apo+fFUF5jprfkM13JgmezqPTMuHikBR6JVXLgKi9Fj7JL6OOdoda9j+/4vclYi7Tg+krRmqMcpKE5mhPt6kUhAZHG/U5FXezM7ALZwmJsJeYRaOdpJhq7PS/9DRPuBs6Ys3T4TZQX+ghxAqoUypR3pTM49s4MmvgNQzMKDpKK8GET+UJ6DXb6JvRjo7xpTQiD1t8uvmwDP4IX+U2g2Toq+1RWvok5UIEQ6W59VKvajmfgziC16mM8gXzg67ylI5H2Ooc7Wmxi5KtKglNXmaoA/wYcFEfYsnrtMP+Pqz3TNJmD+7yE8UP+ntlHhd90K9gK23cO2bJz/6amFofV9/+0sH2wpUYSp7iDkXHvMzeNlegkeFJ6WRgB",
                        "thinking": 'The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.',
                        "type": "thinking",
                    },
                    {
                        "citations": None,
                        "text": "I'll compute the 100th Fibonacci number for you.",
                        "type": "text",
                    },
                    {
                        "id": "toolu_011SpxgqXejF9h3wrt4SyaFP",
                        "input": {"n": 100},
                        "name": "compute_fib",
                        "type": "tool_use",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_011SpxgqXejF9h3wrt4SyaFP",
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
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[],
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
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="The user is asking for the 100th Fibonacci number. I have a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the value n=100, so I have all the required parameters to make this function call."
                    ),
                    ToolCall(
                        id="toolu_01VXjAWpsagqhHFGrVHifRNn",
                        name="compute_fib",
                        args='{"n": 100}',
                    ),
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "signature": "EqIDCkYICBgCKkAXfE8Ma/1W1RMJEJAaONVTPTR5PEkfVgcNZ1GfbHCHXjpakEQyB9FKD6qX5kSpu0kn4D588pTWLlceVUssMvgMEgw+jJeb1/hJMUBgy9EaDIonYmeS9w2QlXCeZSIwjm/MGZZM/xM8r/K5q6Ek6qRdVALWMqfYFBQJ7I6d9BI/kqYJD6M1V2+UAMOf1UGHKokChJMybEYuRrlpGShmkDK7Nl8y+U7gON6Xvuqc1+pkoNPqInorqVrRvwKtqzpR368mnDOs2GfrwduT3FfDHleY+EZpyrzPRBRWGtqwSFOuyCi7C1mpo3LI3yjdwIm2KZimQwT+ZtpenUPqV21UhQaRkIsBsb9os+yl9iq6QD4UlVrB3oR9QmnhINAzSC77fa1mY/pbxIIAPrs4ifkXj1Z5C2W9AMzSx6iFBS0Hyf2h+BjTyflL66CixosZePBdKdDACz4zCz5ut/mWqA9qHrf2uO4w5dEwl16pktzv6Nj9Gjw2dDk4Llv46sZKcA6f+bdwQQIVwMxia868Mo4At1VAytTONPIJxl8+aRgB",
                        "thinking": "The user is asking for the 100th Fibonacci number. I have a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the value n=100, so I have all the required parameters to make this function call.",
                        "type": "thinking",
                    },
                    {
                        "id": "toolu_01VXjAWpsagqhHFGrVHifRNn",
                        "input": {"n": 100},
                        "name": "compute_fib",
                        "type": "tool_use",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_01VXjAWpsagqhHFGrVHifRNn",
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
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[],
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
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have access to a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided a specific value of n = 100, so I have all the required parameters to make the function call.'
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_01SR7KDhN2rcEoJLpD5sqTgL",
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
                        id="toolu_01SR7KDhN2rcEoJLpD5sqTgL",
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
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[],
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
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="The user is asking for the 100th Fibonacci number. I have a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the value n=100, so I have all the required parameters to make this function call."
                    ),
                    ToolCall(
                        id="toolu_01AWi396Gpcy2Xm2K8HkGnjh",
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
                        id="toolu_01AWi396Gpcy2Xm2K8HkGnjh",
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
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[],
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
