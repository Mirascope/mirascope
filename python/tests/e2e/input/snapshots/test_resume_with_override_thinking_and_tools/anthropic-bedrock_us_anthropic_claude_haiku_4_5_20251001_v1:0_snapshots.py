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
        "provider": "anthropic-bedrock",
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "params": {"thinking": False},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
            AssistantMessage(
                content=[
                    Thought(
                        thought='The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.'
                    ),
                    Text(text="I'll compute the 100th Fibonacci number for you."),
                    ToolCall(
                        id="toolu_01KyfnGtAxQP73fNgYzniVBF",
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
                            "signature": "ErUDCkYICBgCKkAZ8Eyo/8TVOqZn7wmDOwDNCnvMQZnR8ebbqmE1iXAyk0CI8vPxchSKHhby929aBl6m37sFV14KFFq9D3adnjL0Egy2lhHFyokdxegShCAaDPqTQUfBnGL0PXCqUiIwWbZVxdFYldYArJudAXqGxBQPQ2fzn9eGC7txPMj9SnsfA2F9q1BUngTPxsFkeGPtKpwCnTqq000CwNtvWpYM2nyG+WBpAQFzN7whwVLSld1YTF0z5N1Vt1xM4BwPewQmbqhln8v3GhAqzdOSh22Pw7tc917f2ggNg5Cfy5u3NsKsFw+GPvS/8bpIecRSoJ/hwbhzqwNewiVtK79+86ZurQqYrioU6MOw59PmPaGebUzyl6q1IgK/LdczCUpxqZPhhP9h/YUvYjh7fuOcDGOfIHMp8IkTQAjhk9+EjHCxBguSeGYJ70/cKLpXP0twLGAFJAiYB5lemCfycDj0FyxPSZN1Oy03s35KtK1G4E52gpcFwCyJaJnzX3e10cJa8ZuaGlkQD41YdoCSO09YITKi5yraSa2LRbK6aIfyo62RcGosMwP7g0eb0VefHlmBmg8YAQ==",
                            "thinking": 'The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.',
                            "type": "thinking",
                        },
                        {
                            "citations": None,
                            "text": "I'll compute the 100th Fibonacci number for you.",
                            "type": "text",
                        },
                        {
                            "id": "toolu_01KyfnGtAxQP73fNgYzniVBF",
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
                        id="toolu_01KyfnGtAxQP73fNgYzniVBF",
                        name="compute_fib",
                        value="218922995834555169026",
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The 100th Fibonacci number is **218,922,995,834,555,169,026**.

This is a very large number with 21 digits! The Fibonacci sequence grows exponentially, so the numbers become quite substantial as you progress through the sequence.\
"""
                    )
                ],
                provider="anthropic",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": """\
The 100th Fibonacci number is **218,922,995,834,555,169,026**.

This is a very large number with 21 digits! The Fibonacci sequence grows exponentially, so the numbers become quite substantial as you progress through the sequence.\
""",
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
)
