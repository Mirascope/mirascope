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
            "provider": "openai:responses",
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
                        ToolCall(
                            id="toolu_01LVmhRSWyUc2ep2hbP7hH84",
                            name="compute_fib",
                            args='{"n": 100}',
                        ),
                    ],
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "signature": "ErQDCkYICBgCKkCsItOUHNinar+NABlYn+UTCEV462H15XiUdax8L7lhYMAvN2X2YxzcMd8Obghv+2Menhq/JUHTvDvU3gt3TiOQEgwBwO65BrVeQDsdzOsaDJLQlWqNjpXdBBjgGiIwd7VNj7mVC11HNOFLqTxqq/O2ERu9FYdGiOFTwMyutumJ2sWNTrrAIzNf9SpAk5SSKpsC0hXQacdwPhqJQxZc8hauodhKwKfpksYOm0yJd7v1aRdrAZHrYwfMYlyiygzctAx3wLXzFE7Ez1frJkF+PZYok76DU7BMP2wC+JSiGsPdeaNcy7RnsP7S2/U86non+98+/LLM6TtJ0tTYl1e5q2H0KFl/J3i+ivRGTkbw7+Nf/LKGxT+luaiZPxwvcSqoQiuRUAx0TV875THH5FWYjxxtRpOFmoYmNglLJ9jkoXc2Z4Tvi1ESojBFWW0aBm8yWPaEb/pnDVKebCXBro+J6Gndpx17Dn74eOv9lmAQqu0QM+ymgMWBeJezBvf7QUQGZ511Dnyliy3HkcahbdT1XMhim6i6lf9Zugcha1lL2ZFHuzaZnMhnG9NxC867vhgB",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.',
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01LVmhRSWyUc2ep2hbP7hH84",
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
                            id="toolu_01LVmhRSWyUc2ep2hbP7hH84",
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
                    raw_message=[
                        {
                            "id": "msg_094f26de235459b00068f9669723508194938b9bf3722348d9",
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
    }
)
