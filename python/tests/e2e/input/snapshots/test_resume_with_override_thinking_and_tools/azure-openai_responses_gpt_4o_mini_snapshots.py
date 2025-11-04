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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought='The user is asking for the 100th Fibonacci number. I have a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the required parameter n=100, so I can proceed with the function call.'
                        ),
                        Text(text="I'll compute the 100th Fibonacci number for you."),
                        ToolCall(
                            id="toolu_01DQ76WAnf7k9UQTUptfmL6D",
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
                                "signature": "EpYDCkYICRgCKkBc5mUeNHmZxC3fi+j4G0f/JOXNCuUTETVF1y7vxVFBbN1b35uQqZg7ekueHo1XO3i2/II0IuViSFmNLxET0+8KEgwAET4b/TB4TJsYR1caDKshYgFv3hD7hlCg6iIw6Qn0MRmZ/ehW8OiOVJMoQCKg7EpcrbzRaY0WC7eRCiJmO22RgnClZKFhwX1ZxnQzKv0B+xXLKZiBRoVyRV6cLprWEV/5PVGeEflqSXghJsHNGpahlppnZ0MQ2PqKCFNPu2nXmzVYNGxlNGpgIqIeqqjy7c8SP+Eg6anfvPmproRmMmnmHzC36zNX0EaBcS7ODhKyUYGED9GoT7Cjmb5Qebf6p1ljxjfvpttTMs6VMdH7RSCUz/VLgAoczM2Jk5q82R2r1HsU5vx/YYipwKz5ypTCUkZsluCBO94xf9obYW65/BUZFouUyrL4wmk0Nw69sDvRQG2dfY0vdzbVLN9KNDgqEUWvc60SfehdjrrokLZW4Bsj8ZMjozIx/xrnJwx8F34ZUXzf5f991uww8K0h1RgB",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the required parameter n=100, so I can proceed with the function call.',
                                "type": "thinking",
                            },
                            {
                                "citations": None,
                                "text": "I'll compute the 100th Fibonacci number for you.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01DQ76WAnf7k9UQTUptfmL6D",
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
                            id="toolu_01DQ76WAnf7k9UQTUptfmL6D",
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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_070c9ddf30fdd20500690c21699764819590749ca87b5302d1",
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
