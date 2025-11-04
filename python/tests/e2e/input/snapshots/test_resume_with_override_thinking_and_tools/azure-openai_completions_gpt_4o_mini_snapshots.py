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
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought='The user is asking for the 100th Fibonacci number. I have a tool available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.'
                        ),
                        ToolCall(
                            id="toolu_01MNaK51zGjK8KDSDkA7ARHg",
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
                                "signature": "ErADCkYICRgCKkDtY5aurlbvRdIjHZziePJLwp5rd4Sxn60loU3ehCnSZgVxG/krk7mXK8MYOV9dOdF22U4LhfKinFb1bkULHqtmEgwj0wC4qCRr+bYwFwMaDBcSMJ9N9ijMHFpxVCIw7sNA1zxqzQhGenCmYA+UQIX1GZr0JJXE3XSexw2w6/Xc8GzkSyhQFk8yfzfWvcd+KpcCBMV2enN+T7vSB2yLufw2cwZZ1i1XT4v1RT0nU4fLCQIlxflbvVQ3RoEgEfH6RNQ7w0nosu8HwPvEpjieu5Km/o71MVKzO9oOvWeZfMqDM3IzJP8YE3hDbJOCZcUwLvmsIkk1fQwkoBCjhW3U6S8W3zaTko1M/5IxMxx3pPeGSSNebKtR81LO6Fs1tONPqVVvAReAPQy2fb5cv2uyddfl41SCKx8f64fX2MSB13qfSuXN6YPirhf+GM5t7xzVsnt6kLykuc/C5p8kqllwoZFSIeMEDWIYLgUO0KLG2mu6ARVeZcm0v9RrsndLBRKhQI0nVb0bdGJ6bBQmoWwECe+Y+5q+fFauatm40xpcmHQeKZ6EjIExsOLyGAE=",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have a tool available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.',
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01MNaK51zGjK8KDSDkA7ARHg",
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
                            id="toolu_01MNaK51zGjK8KDSDkA7ARHg",
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
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message={
                        "content": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
                        "role": "assistant",
                        "annotations": [],
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
