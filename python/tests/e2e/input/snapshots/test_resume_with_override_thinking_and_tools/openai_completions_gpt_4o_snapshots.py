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
            "provider": "openai:completions",
            "model_id": "gpt-4o",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought='The user is asking for the 100th Fibonacci number. I have a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.'
                        ),
                        ToolCall(
                            id="toolu_01LXbYDxRjyLgjMvcPVezUyH",
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
                                "signature": "EqoDCkYICRgCKkAAW+8fgSnrlHy7gs1efkmz9lpewAfgIjUn/LUlYRlq8NvvW+U0i0FB+GPq2y8q+4+yGE7QcfQM8o7zLlIXzlilEgzO++MGfd79vxrbBScaDEzgRM15YwmLBF37viIw/mF7F79V/ZiZO+0+sSUCwy+MzR5cwfcpcb15KwgqtimhY34cY+qnaksHLqv4iZHiKpEC+IFvSvGXHo2T/CPCbT+YqSOLR0HvRtyTKUwl3OoO0y3QzJEyERsFSlwHWFby3erGJuWeMVNoL0XNmNDHIGT8UzzCJQBw4mrmYJVuORCp4JQCeo0LwHfsrF5/LWG5BXeY9CdbI68YuFY/f1H4Cz3jy2osvFetk4FaQL6ueWmBHfzc3Rrz+GQoTC42eWzn9LM10cxGQxt9ImHns26s3p6cbVOVBByG12ee3iOvQKEFFrlRLjQJquWeNgL9IUVKmM3ok3vhVMT8FKrnkLKGyvr4VzAm3bnzVfdpHuIZmuSx3JZlqw7slAu3tMfI6DlyAII0DTAGC0LK6Jya9GmolfEXia/cJdsurNUh90G4np6oY8RjGAE=",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have a function called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.',
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01LXbYDxRjyLgjMvcPVezUyH",
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
                            id="toolu_01LXbYDxRjyLgjMvcPVezUyH",
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
    }
)
