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
                            thought='The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.'
                        ),
                        ToolCall(
                            id="toolu_01M2MyAhQSWScDhpxTAfK9Fe",
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
                                "signature": "ErUDCkYICRgCKkAZ8Eyo/8TVOqZn7wmDOwDNCnvMQZnR8ebbqmE1iXAyk0CI8vPxchSKHhby929aBl6m37sFV14KFFq9D3adnjL0EgytewXgGCoHlMCudl0aDHAUyi01daHuDdAL3yIw4sisG/xC3vzCMvPlqTcmyDfBEkhtCx7yeYqFn5/rAZuaII5m4iqSYuK40ZSAQG9EKpwCD2ScmXSq4yUb+vcxMNSA5WaYUaQPhUFjMvoLyzv1FqkqXg+YqUJGVd5DWEpWhUaUWNCJ5tJAvQ55n5gub0HTqgBJN7NcENrfm2t0l1cClSQHhZmcfLG+Hz+OzSyHWSMHk7A+ZJ0cieBh/BMEDLTwvzyZ12s5VQ3myy67/cteDtGg1/ekv1DjXr7NE3KlJtjdJxtXTNCjX7X0Rs6QsOKuR6eoJ1TR6gi10ivz2IA6zmGUydlrMGT1SqHFbY0/9bHzJS/yJVl+OmD+G2tDzKdg6Myga2HNGFWe/2FYf3J2zkzjayf0mcQz6EEjRivyUa4hJQxhubrgPDdhNSNVZXnmgL6AT5CiscBWf5bHEnnlS12xWw8mYPvSQwRYIQIYAQ==",
                                "thinking": 'The user is asking for the 100th Fibonacci number. I have a function available called "compute_fib" that can compute the nth Fibonacci number (1-indexed). The user has provided the specific value n=100, so I have all the required parameters to make this function call.',
                                "type": "thinking",
                            },
                            {
                                "id": "toolu_01M2MyAhQSWScDhpxTAfK9Fe",
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
                            id="toolu_01M2MyAhQSWScDhpxTAfK9Fe",
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
