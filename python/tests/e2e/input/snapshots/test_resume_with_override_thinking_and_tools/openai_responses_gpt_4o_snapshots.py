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
                            thought="The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call."
                        ),
                        ToolCall(
                            id="toolu_01T6RCnKArQXwXMWXneZC1Dr",
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
                                "signature": "ErQDCkYICRgCKkDaHob9wh+/6LJ48y0NcBWC9b5bnLRiddtv+9x3lKtb9tem+amT31hQnImhTc2hT9bXFFhSVdBD7VEocP8J+/JfEgxw3aUKCBi+vOaGnbIaDL/PxlAtKliVNzM9pCIwzbeeB8v1We9yVgZ/2z54D3153AhhV2DNYFoqHBCXWfFe3dz+60tDwPCHd+0wgMmwKpsCZH7g5mEjuGWh0FBltEmnQnEcnorTT0gfPJTlk5HUvbIFTa0UGonGccnPgidGOLiCZqPfL3Xo0AbyMvhS+yAMKlEE9AlqbBDxoezfpLv0Z+ojBCufeH4oM9xHMtvZbDvAW2wucQQvVT70lIKvTpWM4j6RuWMo8rotZp0awVx0tOlvV6oZLl9BtBoLddXWUwbZz3rSMOByyjydAYUz7SpRuY/ZsV8rR5ibSXUY3rFSrMwFXb13z6BErOoI9/Hbl+d1A35Z3t0m2gRrETvwMTmnEi1+IRwQX5CK189qNTeMA/1R16XZnS9G7W1j73A9r0JjBghphDMKYouca8oX2xqczX/J7uO+/UxEwLYZDeVQt2YejzzJef4cREjs/BgB",
                                "thinking": "The user is asking for the 100th Fibonacci number. I have access to a function called `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.",
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01T6RCnKArQXwXMWXneZC1Dr",
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
                            id="toolu_01T6RCnKArQXwXMWXneZC1Dr",
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
                            "id": "msg_0ea88e5cd959147100690a1e4a547c8193b00f753c9a61f348",
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
                            "response_id": "resp_0ea88e5cd959147100690a1e49d21081938a3e1d67a0ebe69e",
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
