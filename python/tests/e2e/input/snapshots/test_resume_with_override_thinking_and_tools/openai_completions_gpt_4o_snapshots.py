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
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought="The user is asking for the 100th Fibonacci number. I have a function available called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call."
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_01UvLhE2u2ZGcdihNhXUm1wp",
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
                            "signature": "ErQDCkYICBgCKkAvaj6zwlcCXh989DjfcJKxhnEl5NQA4aOMRq/nZzCYnhPFXVcF6OMlhlPU/gK+hzNjWeY/3Q7HLQvMtqr3wym/Egy6b14LOeSQ1wVvF24aDN+G5tLY1buyBhc4gSIwmOXjvuWtJb+x3LV1DMpXkb1R97E3wRyIs+LTxLJ7p9LAebDnW4dIFtJt5vTUqK40KpsCz+4VXHewhrDmLzXOo858J2FHSzuQprqwULAPba1kasCHTEt1Z5eSc3thRuGJReZNpCU82BFeESHvrKj45BSrHxKUsrb9eU9JBGdSgdz/cgKdj3LvkRIhrAq6NIG83hgG2cK6lF2Ae361w+KeBIenHj589Dw9ufmd6Nj6mTNvN2WBcDbRZnn+X4tAl8xIelZ0sBG7bvuzBxV7iPv7+N2qWbiLm68PH3UaBjD2/SKcPUbHB5sv5N6laxwSM6RIZy/hg33l0eXQMT0jHjHHK4vI0Flum4eJwN/7rOM4DAnJCHux297HwheEVzARd4L5qQfTr1q9kdFDlrE7B+FVhD0NURmBKDpkcQ2cYCgnK+uRz2+LW/IZqPWurdiVPBgB",
                            "thinking": "The user is asking for the 100th Fibonacci number. I have a function available called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.",
                            "type": "thinking",
                        },
                        {
                            "citations": None,
                            "text": "I'll compute the 100th Fibonacci number for you.",
                            "type": "text",
                        },
                        {
                            "id": "toolu_01UvLhE2u2ZGcdihNhXUm1wp",
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
                        id="toolu_01UvLhE2u2ZGcdihNhXUm1wp",
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
)
