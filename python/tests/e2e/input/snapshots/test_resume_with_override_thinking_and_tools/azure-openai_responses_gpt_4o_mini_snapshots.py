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
                            thought='The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.'
                        ),
                        ToolCall(
                            id="toolu_01P11Xus7T44xSAftSiPypjg",
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
                                "signature": "ErQDCkYICRgCKkCsItOUHNinar+NABlYn+UTCEV462H15XiUdax8L7lhYMAvN2X2YxzcMd8Obghv+2Menhq/JUHTvDvU3gt3TiOQEgxszw1MpIIhFZgRSwgaDHeuziQr1BJAfRZa3iIw2lShdgUjzJ2sYGPDBenCasn61QeIbmGIudwJla01o0VqN5TZhzzzA2Mb9Oo0mltnKpsCRbsCLQYx1ey2LTkxznrao325r+ba0PLvnW4bVOKmNPQj4iH70+v3rPZ4WgBU5AwoAb9GDD786aWVx12wX0/dBJESDnk9tIqOt70eh8BU+T+hpJRqyi+E3VuYm5cZ5+EfmkH7uWqZYWdBfqSjHwX4rfQjbsPwF1m6CYKV+w641/uU529GDQWrbS3fT6xvIyIhy7ttExfMVxANn0NPdCtG0VFpeIbkGqaq5+l2/vVKu3j7I9jQTpnXNrxJEgI63vKJT5vVNL985biHTGTnZ8tPosszH/FcC+O7aiFaHtiId86P2JBCZL5SKDWb48dLgEU1UdUq27+7XIyP2sMf91Zr0ExXovY5pPq07kvPNsvt3xOR0X+FaaGPAedWiRgB",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.',
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01P11Xus7T44xSAftSiPypjg",
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
                            id="toolu_01P11Xus7T44xSAftSiPypjg",
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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_047cfe89c033e48400690ac70764dc8196aa3b75bd30944e7e",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "The 100th Fibonacci number is **218,922,995,834,555,169,026**.",
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
