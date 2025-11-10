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
                            thought="The user is asking for the 100th Fibonacci number. I have a function `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call."
                        ),
                        Text(text="I'll compute the 100th Fibonacci number for you."),
                        ToolCall(
                            id="toolu_017pdVGDVrtZjby5USUYNXtn",
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
                                "signature": "EqMDCkYICRgCKkAH0AN4D9k63uMdx9oxQba1K1kY9liw5lWVneiTioQ260RfffuugJh1F2Wd2SmUK3q8tnv56+2/U2WRR1fruFfyEgxg9Kl/N6E0bh+RMCQaDJHlQebs9cbNcuKBEiIwF9d/Om82EpKtgelFJHBNtMDB8F2irPKlPvo5QLgTDf5fsaLBMRaIcilF6G9qn9lTKooCeJ7sgwsVz1FBq1vWcn2aNXsSb1jaqdnmu2AtkeKfoGwBAVaSOTilDXR1h7bwYfNv6HZQadQN18JSgh7mcp8SZ9J3Ik4xtTYaKqk2A4dGuJ7/q2RV82rtRzmH7fULzN8UwVvOTI7oVipQ7LPGIf7znd3JE4iEfDOyWRppnXhXZzBMn3xSFGhTvwnXDszfecBasZSxS8cWt4ahLlgymTP1xwOIm6RrrmRH4f5B4rrfpm7KRbCi5eKVLqJqs+48sb6RGCX9K+MvoaMKkHJTCuEFoZa1qabAAaF15avgRJAtgJnlI+lvBQ7pvIpgghdvQ/77fdgvVfXJgKD3JSCYiCmFq9jpsdduanHl2tUYAQ==",
                                "thinking": "The user is asking for the 100th Fibonacci number. I have a function `compute_fib` that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make the function call.",
                                "type": "thinking",
                            },
                            {
                                "citations": None,
                                "text": "I'll compute the 100th Fibonacci number for you.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_017pdVGDVrtZjby5USUYNXtn",
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
                            id="toolu_017pdVGDVrtZjby5USUYNXtn",
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
                    provider="anthropic-vertex",
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
