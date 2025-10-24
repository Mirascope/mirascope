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
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call."
                        ),
                        ToolCall(
                            id="toolu_01VPt9Qk6MWVS38d2E9dU9DH",
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
                                "signature": "ErQDCkYICRgCKkDaHob9wh+/6LJ48y0NcBWC9b5bnLRiddtv+9x3lKtb9tem+amT31hQnImhTc2hT9bXFFhSVdBD7VEocP8J+/JfEgw/V3ysIvIxLeK0A44aDE3p8dmkMXHu6sctbSIwdNHzsEA4cxScgOqPQn+MzczOBypvDzjB5xzyPOqkHsC+Ce1TIz/dEd3sgcnYn4quKpsC/W6bXxwQwur9UrDczbsnodJqPAR7vaVGA359g1guZBx83OUtXfLdeP6A0lroMlTIQnrUB7lmadaGtOQZ5puMGKb5n+dMBeZ9I7UnZKz84lRoYZETck/96TodRlNQEJVt5d4HtNLC4ZXLxfAn+bpw7Mcn7URhFi818xtpg6peqkmTEfWjVP8vqbviZLyylNDxeNp8lBWf/ps1IjtdiwPfCoHFrVQua94bSDWIDLPG9BKTD9qR84YnC2rqkT3GZpISZNzXMYFxw78AIWg4e7NdblsrcUU/Cszv+36h/xSAiwMimA9uLvNTjvSH/XykF5zg+buXcbAuIsLSzTDY57hVIUJhTmpvSf7Mu1wSiP5AMlSqjr8CmYpNiX1F6RgB",
                                "thinking": "The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.",
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01VPt9Qk6MWVS38d2E9dU9DH",
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
                            id="toolu_01VPt9Qk6MWVS38d2E9dU9DH",
                            name="compute_fib",
                            value="218922995834555169026",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The 100th Fibonacci number is **218,922,995,834,555,169,026**."
                        )
                    ],
                    provider="anthropic",
                    model_id="claude-haiku-4-5@20251001",
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
                    "strict": False,
                }
            ],
        }
    }
)
